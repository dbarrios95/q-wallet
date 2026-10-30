// Acceso a datos de svc-transfers (permisos de su rol IAM, CTRL-12):
// perfiles (Query al índice por-telefono), pin (Get/Update), cuentas (Get/Query/Update),
// movimientos (Put), transferencias (Get/Put), beneficiarios (Query/Put/Delete), auditoria (Put).
import { randomUUID } from "node:crypto";
import { ConditionalCheckFailedException, TransactionCanceledException } from "@aws-sdk/client-dynamodb";
import {
  DeleteCommand,
  GetCommand,
  PutCommand,
  QueryCommand,
  TransactWriteCommand,
  UpdateCommand,
  type DynamoDBDocumentClient,
} from "@aws-sdk/lib-dynamodb";
import { INTENTOS_MAXIMOS, MINUTOS_BLOQUEO } from "../../comun/src/pin";

export interface Cuenta {
  userId: string;
  accountId: string;
  saldoCentavos: number;
}

export interface Transferencia {
  transferId: string;
  origenUserId: string;
  destinoUserId: string;
  montoCentavos: number;
  categoria: string;
  descripcion?: string;
  destinoMascara: string;
  fecha: string;
  estado: "completada";
}

export interface Beneficiario {
  userId: string;
  beneficiarioId: string;
  alias: string;
  destinoUserId: string;
  telefonoMascara: string;
  creado: string;
}

export interface RegistroIdempotencia {
  huella: string;
  status: number;
  respuesta: string;
}

export type ReservaPin = { estado: "ok"; hash: string; intentos: number } | { estado: "bloqueado" } | { estado: "sin_pin" };

export interface NuevaTransferencia {
  claveIdempotencia: string;
  huellaSolicitud: string;
  respuesta: (t: Transferencia) => { status: number; cuerpo: unknown };
  origen: Cuenta;
  destino: Cuenta;
  transferencia: Transferencia;
}

export type ResultadoTransferencia = { estado: "ok"; status: number; cuerpo: unknown } | { estado: "saldo_insuficiente" } | { estado: "duplicada" };

export interface RepositorioTransferencias {
  leerIdempotencia(userId: string, clave: string): Promise<RegistroIdempotencia | null>;
  reservarIntentoPin(userId: string, ahora: number): Promise<ReservaPin>;
  cerrarIntentoPin(userId: string, correcto: boolean, intentos: number, ahora: number): Promise<void>;
  usuarioPorHuella(huella: string): Promise<string | null>;
  cuentaPrincipal(userId: string): Promise<Cuenta | null>;
  ejecutar(t: NuevaTransferencia): Promise<ResultadoTransferencia>;
  obtenerTransferencia(transferId: string): Promise<Transferencia | null>;
  listarBeneficiarios(userId: string): Promise<Beneficiario[]>;
  obtenerBeneficiario(userId: string, beneficiarioId: string): Promise<Beneficiario | null>;
  crearBeneficiario(b: Beneficiario): Promise<void>;
  eliminarBeneficiario(userId: string, beneficiarioId: string): Promise<boolean>;
}

export interface Tablas {
  perfiles: string;
  pin: string;
  cuentas: string;
  movimientos: string;
  transferencias: string;
  beneficiarios: string;
}

const HORAS_IDEMPOTENCIA = 24;
export const MAXIMO_BENEFICIARIOS = 50;

export function repositorioDynamo(c: DynamoDBDocumentClient, t: Tablas): RepositorioTransferencias {
  return {
    async leerIdempotencia(userId, clave) {
      const r = await c.send(new GetCommand({ TableName: t.transferencias, Key: { pk: `IDEMP#${userId}#${clave}` }, ConsistentRead: true }));
      return (r.Item as RegistroIdempotencia | undefined) ?? null;
    },

    async reservarIntentoPin(userId, ahora) {
      const r = await c.send(new GetCommand({ TableName: t.pin, Key: { userId }, ConsistentRead: true }));
      if (!r.Item) return { estado: "sin_pin" };
      try {
        // Reserva atómica del intento ANTES de verificar: aunque lleguen 20 solicitudes a la vez,
        // como máximo 5 llegan a comparar el PIN antes del bloqueo (CTRL-02, CA-02).
        const u = await c.send(
          new UpdateCommand({
            TableName: t.pin,
            Key: { userId },
            UpdateExpression: "SET intentos = if_not_exists(intentos, :cero) + :uno",
            ConditionExpression: "(attribute_not_exists(bloqueadoHasta) OR bloqueadoHasta < :ahora) AND (attribute_not_exists(intentos) OR intentos < :max)",
            ExpressionAttributeValues: { ":cero": 0, ":uno": 1, ":ahora": ahora, ":max": INTENTOS_MAXIMOS },
            ReturnValues: "ALL_NEW",
          }),
        );
        return { estado: "ok", hash: u.Attributes?.hash as string, intentos: u.Attributes?.intentos as number };
      } catch (e) {
        if (e instanceof ConditionalCheckFailedException) return { estado: "bloqueado" };
        throw e;
      }
    },

    async cerrarIntentoPin(userId, correcto, intentos, ahora) {
      if (correcto) {
        await c.send(
          new UpdateCommand({
            TableName: t.pin,
            Key: { userId },
            UpdateExpression: "SET intentos = :cero REMOVE bloqueadoHasta",
            ExpressionAttributeValues: { ":cero": 0 },
          }),
        );
      } else if (intentos >= INTENTOS_MAXIMOS) {
        await c.send(
          new UpdateCommand({
            TableName: t.pin,
            Key: { userId },
            UpdateExpression: "SET bloqueadoHasta = :hasta, intentos = :cero",
            ExpressionAttributeValues: { ":hasta": ahora + MINUTOS_BLOQUEO * 60_000, ":cero": 0 },
          }),
        );
      }
    },

    async usuarioPorHuella(huella) {
      const r = await c.send(
        new QueryCommand({
          TableName: t.perfiles,
          IndexName: "por-telefono",
          KeyConditionExpression: "telefonoHash = :h",
          ExpressionAttributeValues: { ":h": huella },
          Limit: 1,
        }),
      );
      return (r.Items?.[0]?.userId as string | undefined) ?? null;
    },

    async cuentaPrincipal(userId) {
      const r = await c.send(
        new QueryCommand({
          TableName: t.cuentas,
          KeyConditionExpression: "userId = :u",
          ExpressionAttributeValues: { ":u": userId },
          Limit: 1,
          ConsistentRead: true,
        }),
      );
      return (r.Items?.[0] as Cuenta | undefined) ?? null;
    },

    async ejecutar(n) {
      const tr = n.transferencia;
      const { status, cuerpo } = n.respuesta(tr);
      const expiraEn = Math.floor(Date.now() / 1000) + HORAS_IDEMPOTENCIA * 3600;
      try {
        // CTRL-06: todo o nada. Doble gasto imposible: la clave de idempotencia solo se
        // escribe una vez y el débito exige saldo suficiente en el mismo instante.
        await c.send(
          new TransactWriteCommand({
            TransactItems: [
              {
                Put: {
                  TableName: t.transferencias,
                  Item: { pk: `IDEMP#${tr.origenUserId}#${n.claveIdempotencia}`, huella: n.huellaSolicitud, status, respuesta: JSON.stringify(cuerpo), expiraEn },
                  ConditionExpression: "attribute_not_exists(pk)",
                },
              },
              {
                Update: {
                  TableName: t.cuentas,
                  Key: { userId: n.origen.userId, accountId: n.origen.accountId },
                  UpdateExpression: "SET saldoCentavos = saldoCentavos - :m",
                  ConditionExpression: "saldoCentavos >= :m",
                  ExpressionAttributeValues: { ":m": tr.montoCentavos },
                },
              },
              {
                Update: {
                  TableName: t.cuentas,
                  Key: { userId: n.destino.userId, accountId: n.destino.accountId },
                  UpdateExpression: "SET saldoCentavos = saldoCentavos + :m",
                  ConditionExpression: "attribute_exists(accountId)",
                  ExpressionAttributeValues: { ":m": tr.montoCentavos },
                },
              },
              { Put: { TableName: t.transferencias, Item: { pk: `TRF#${tr.transferId}`, ...tr }, ConditionExpression: "attribute_not_exists(pk)" } },
              {
                Put: {
                  TableName: t.movimientos,
                  Item: {
                    accountId: n.origen.accountId,
                    fechaId: `${tr.fecha}#${randomUUID()}`,
                    fecha: tr.fecha,
                    tipo: "debito",
                    montoCentavos: tr.montoCentavos,
                    categoria: tr.categoria,
                    descripcion: tr.descripcion,
                    contraparte: tr.destinoMascara,
                    transferId: tr.transferId,
                  },
                },
              },
              {
                Put: {
                  TableName: t.movimientos,
                  Item: {
                    accountId: n.destino.accountId,
                    fechaId: `${tr.fecha}#${randomUUID()}`,
                    fecha: tr.fecha,
                    tipo: "credito",
                    montoCentavos: tr.montoCentavos,
                    categoria: "transferencias",
                    descripcion: tr.descripcion,
                    contraparte: "Usuario Q-Wallet",
                    transferId: tr.transferId,
                  },
                },
              },
            ],
          }),
        );
        return { estado: "ok", status, cuerpo };
      } catch (e) {
        if (e instanceof TransactionCanceledException) {
          const motivos = e.CancellationReasons ?? [];
          if (motivos[0]?.Code === "ConditionalCheckFailed") return { estado: "duplicada" };
          if (motivos[1]?.Code === "ConditionalCheckFailed") return { estado: "saldo_insuficiente" };
        }
        throw e;
      }
    },

    async obtenerTransferencia(transferId) {
      const r = await c.send(new GetCommand({ TableName: t.transferencias, Key: { pk: `TRF#${transferId}` } }));
      return (r.Item as Transferencia | undefined) ?? null;
    },

    async listarBeneficiarios(userId) {
      const r = await c.send(
        new QueryCommand({
          TableName: t.beneficiarios,
          KeyConditionExpression: "userId = :u",
          ExpressionAttributeValues: { ":u": userId },
          Limit: MAXIMO_BENEFICIARIOS,
        }),
      );
      return (r.Items ?? []) as Beneficiario[];
    },

    async obtenerBeneficiario(userId, beneficiarioId) {
      const r = await c.send(
        new QueryCommand({
          TableName: t.beneficiarios,
          KeyConditionExpression: "userId = :u AND beneficiarioId = :b",
          ExpressionAttributeValues: { ":u": userId, ":b": beneficiarioId },
          Limit: 1,
        }),
      );
      return (r.Items?.[0] as Beneficiario | undefined) ?? null;
    },

    async crearBeneficiario(b) {
      await c.send(new PutCommand({ TableName: t.beneficiarios, Item: b, ConditionExpression: "attribute_not_exists(beneficiarioId)" }));
    },

    async eliminarBeneficiario(userId, beneficiarioId) {
      try {
        await c.send(
          new DeleteCommand({ TableName: t.beneficiarios, Key: { userId, beneficiarioId }, ConditionExpression: "attribute_exists(beneficiarioId)" }),
        );
        return true;
      } catch (e) {
        if (e instanceof ConditionalCheckFailedException) return false;
        throw e;
      }
    },
  };
}
