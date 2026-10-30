// Acceso a datos de svc-accounts: solo lectura de cuentas (Get/Query) y movimientos (Query).
import { GetCommand, QueryCommand, type DynamoDBDocumentClient } from "@aws-sdk/lib-dynamodb";

export interface Cuenta {
  userId: string;
  accountId: string;
  moneda: string;
  saldoCentavos: number;
  alias: string;
}

export interface Movimiento {
  accountId: string;
  fechaId: string;
  fecha: string;
  tipo: "credito" | "debito";
  montoCentavos: number;
  categoria: string;
  descripcion?: string;
  contraparte?: string;
  transferId?: string;
}

export interface Pagina<T> {
  items: T[];
  siguiente?: Record<string, unknown>;
}

export interface RepositorioCuentas {
  listarCuentas(userId: string): Promise<Cuenta[]>;
  /** Busca la cuenta con la llave (userId, accountId): si no es del usuario, no existe. */
  obtenerCuenta(userId: string, accountId: string): Promise<Cuenta | null>;
  listarMovimientos(accountId: string, limite: number, desde?: Record<string, string>): Promise<Pagina<Movimiento>>;
}

export function repositorioDynamo(c: DynamoDBDocumentClient, t: { cuentas: string; movimientos: string }): RepositorioCuentas {
  return {
    async listarCuentas(userId) {
      const r = await c.send(
        new QueryCommand({
          TableName: t.cuentas,
          KeyConditionExpression: "userId = :u",
          ExpressionAttributeValues: { ":u": userId },
          Limit: 10,
        }),
      );
      return (r.Items ?? []) as Cuenta[];
    },
    async obtenerCuenta(userId, accountId) {
      const r = await c.send(new GetCommand({ TableName: t.cuentas, Key: { userId, accountId } }));
      return (r.Item as Cuenta | undefined) ?? null;
    },
    async listarMovimientos(accountId, limite, desde) {
      const r = await c.send(
        new QueryCommand({
          TableName: t.movimientos,
          KeyConditionExpression: "accountId = :a",
          ExpressionAttributeValues: { ":a": accountId },
          ScanIndexForward: false, // los más recientes primero
          Limit: limite,
          ExclusiveStartKey: desde,
        }),
      );
      return { items: (r.Items ?? []) as Movimiento[], siguiente: r.LastEvaluatedKey };
    },
  };
}
