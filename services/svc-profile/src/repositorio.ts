// Acceso a datos de svc-profile. Solo usa las tablas y acciones de su rol IAM:
// perfiles (Get/Put/Update, Query al índice por-telefono), pin (Put/Update),
// cuentas y movimientos (Put, solo al crear la cuenta inicial) y auditoria (Put).
import { randomUUID } from "node:crypto";
import { TransactionCanceledException } from "@aws-sdk/client-dynamodb";
import {
  GetCommand,
  PutCommand,
  QueryCommand,
  TransactWriteCommand,
  UpdateCommand,
  type DynamoDBDocumentClient,
} from "@aws-sdk/lib-dynamodb";
import { ConditionalCheckFailedException } from "@aws-sdk/client-dynamodb";

export interface Perfil {
  userId: string;
  nombre?: string;
  telefono?: string;
  telefonoHash?: string;
  tienePin: boolean;
  creado: string;
}

/** Dinero simulado: cada cuenta nueva empieza con Q1,000.00 (100 000 centavos). */
export const SALDO_INICIAL_CENTAVOS = 100_000;

export interface RepositorioPerfil {
  obtener(userId: string): Promise<Perfil | null>;
  crearInicial(userId: string): Promise<Perfil>;
  actualizar(userId: string, cambios: Partial<Pick<Perfil, "nombre" | "telefono" | "telefonoHash">>): Promise<Perfil>;
  buscarPorHuella(huella: string): Promise<string | null>;
  crearPin(userId: string, hash: string): Promise<boolean>;
}

export interface Tablas {
  perfiles: string;
  pin: string;
  cuentas: string;
  movimientos: string;
}

export function repositorioDynamo(c: DynamoDBDocumentClient, t: Tablas): RepositorioPerfil {
  const obtener = async (userId: string): Promise<Perfil | null> => {
    const r = await c.send(new GetCommand({ TableName: t.perfiles, Key: { userId }, ConsistentRead: true }));
    return (r.Item as Perfil | undefined) ?? null;
  };

  return {
    obtener,

    async crearInicial(userId) {
      const ahora = new Date().toISOString();
      const perfil: Perfil = { userId, tienePin: false, creado: ahora };
      const accountId = randomUUID();
      try {
        // Perfil, cuenta y movimiento inicial en una sola transacción: o se crean los tres o ninguno.
        await c.send(
          new TransactWriteCommand({
            TransactItems: [
              { Put: { TableName: t.perfiles, Item: perfil, ConditionExpression: "attribute_not_exists(userId)" } },
              {
                Put: {
                  TableName: t.cuentas,
                  Item: { userId, accountId, moneda: "GTQ", saldoCentavos: SALDO_INICIAL_CENTAVOS, alias: "Cuenta principal", creado: ahora },
                  ConditionExpression: "attribute_not_exists(accountId)",
                },
              },
              {
                Put: {
                  TableName: t.movimientos,
                  Item: {
                    accountId,
                    fechaId: `${ahora}#${randomUUID()}`,
                    fecha: ahora,
                    tipo: "credito",
                    montoCentavos: SALDO_INICIAL_CENTAVOS,
                    categoria: "otros",
                    descripcion: "Saldo inicial simulado",
                  },
                },
              },
            ],
          }),
        );
        return perfil;
      } catch (e) {
        // Dos solicitudes simultáneas del mismo usuario: la segunda lee lo que creó la primera.
        if (e instanceof TransactionCanceledException) {
          const existente = await obtener(userId);
          if (existente) return existente;
        }
        throw e;
      }
    },

    async actualizar(userId, cambios) {
      const nombres: Record<string, string> = {};
      const valores: Record<string, unknown> = {};
      const sets: string[] = [];
      for (const [k, v] of Object.entries(cambios)) {
        if (v === undefined) continue;
        nombres[`#${k}`] = k;
        valores[`:${k}`] = v;
        sets.push(`#${k} = :${k}`);
      }
      const r = await c.send(
        new UpdateCommand({
          TableName: t.perfiles,
          Key: { userId },
          UpdateExpression: `SET ${sets.join(", ")}`,
          ConditionExpression: "attribute_exists(userId)",
          ExpressionAttributeNames: nombres,
          ExpressionAttributeValues: valores,
          ReturnValues: "ALL_NEW",
        }),
      );
      return r.Attributes as Perfil;
    },

    async buscarPorHuella(huella) {
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

    async crearPin(userId, hash) {
      try {
        await c.send(
          new PutCommand({
            TableName: t.pin,
            Item: { userId, hash, intentos: 0, creado: new Date().toISOString() },
            ConditionExpression: "attribute_not_exists(userId)",
          }),
        );
      } catch (e) {
        if (e instanceof ConditionalCheckFailedException) return false;
        throw e;
      }
      await c.send(
        new UpdateCommand({
          TableName: t.perfiles,
          Key: { userId },
          UpdateExpression: "SET tienePin = :v",
          ExpressionAttributeValues: { ":v": true },
        }),
      );
      return true;
    },
  };
}
