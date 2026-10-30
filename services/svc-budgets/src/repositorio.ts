// Acceso a datos de svc-budgets: presupuestos (Get/Query/Put/Update), cuentas y movimientos (Query).
import { ConditionalCheckFailedException } from "@aws-sdk/client-dynamodb";
import { PutCommand, QueryCommand, UpdateCommand, type DynamoDBDocumentClient } from "@aws-sdk/lib-dynamodb";

export interface Presupuesto {
  userId: string;
  mesCategoria: string; // "2026-10#alimentacion"
  limiteCentavos: number;
}

export interface Gasto {
  categoria: string;
  montoCentavos: number;
}

/** Tope de movimientos que se suman por mes (evita recorrer historiales enormes). */
export const MAXIMO_MOVIMIENTOS_MES = 1000;

export interface RepositorioPresupuestos {
  listar(userId: string, mes: string): Promise<Presupuesto[]>;
  crear(p: Presupuesto): Promise<boolean>;
  actualizar(p: Presupuesto): Promise<boolean>;
  gastosDelMes(userId: string, mes: string): Promise<Gasto[]>;
}

export function repositorioDynamo(c: DynamoDBDocumentClient, t: { presupuestos: string; cuentas: string; movimientos: string }): RepositorioPresupuestos {
  return {
    async listar(userId, mes) {
      const r = await c.send(
        new QueryCommand({
          TableName: t.presupuestos,
          KeyConditionExpression: "userId = :u AND begins_with(mesCategoria, :m)",
          ExpressionAttributeValues: { ":u": userId, ":m": `${mes}#` },
          Limit: 50,
        }),
      );
      return (r.Items ?? []) as Presupuesto[];
    },
    async crear(p) {
      try {
        await c.send(new PutCommand({ TableName: t.presupuestos, Item: p, ConditionExpression: "attribute_not_exists(mesCategoria)" }));
        return true;
      } catch (e) {
        if (e instanceof ConditionalCheckFailedException) return false;
        throw e;
      }
    },
    async actualizar(p) {
      try {
        await c.send(
          new UpdateCommand({
            TableName: t.presupuestos,
            Key: { userId: p.userId, mesCategoria: p.mesCategoria },
            UpdateExpression: "SET limiteCentavos = :l",
            ConditionExpression: "attribute_exists(mesCategoria)",
            ExpressionAttributeValues: { ":l": p.limiteCentavos },
          }),
        );
        return true;
      } catch (e) {
        if (e instanceof ConditionalCheckFailedException) return false;
        throw e;
      }
    },
    async gastosDelMes(userId, mes) {
      const cuentas = await c.send(
        new QueryCommand({ TableName: t.cuentas, KeyConditionExpression: "userId = :u", ExpressionAttributeValues: { ":u": userId }, Limit: 10 }),
      );
      const gastos: Gasto[] = [];
      for (const cuenta of cuentas.Items ?? []) {
        let desde: Record<string, unknown> | undefined;
        do {
          const r = await c.send(
            new QueryCommand({
              TableName: t.movimientos,
              KeyConditionExpression: "accountId = :a AND fechaId BETWEEN :ini AND :fin",
              ExpressionAttributeValues: { ":a": cuenta.accountId, ":ini": mes, ":fin": `${mes}~` },
              ExclusiveStartKey: desde,
              Limit: 200,
            }),
          );
          for (const m of r.Items ?? []) if (m.tipo === "debito") gastos.push({ categoria: m.categoria, montoCentavos: m.montoCentavos });
          desde = r.LastEvaluatedKey;
        } while (desde && gastos.length < MAXIMO_MOVIMIENTOS_MES);
      }
      return gastos;
    },
  };
}
