// Registro de auditoría en DynamoDB (CTRL-09, CTRL-20, repudio).
// Una fila por acción sensible: quién, qué, sobre qué recurso, resultado y correlationId.
// Nunca guarda montos de PIN, tokens ni datos personales completos.
import { randomUUID } from "node:crypto";
import { PutCommand, type DynamoDBDocumentClient } from "@aws-sdk/lib-dynamodb";

export interface EventoAuditoria {
  actor: string;
  accion: string;
  recurso: string;
  resultado: "ok" | "rechazado";
  correlationId: string;
  detalle?: Record<string, string | number | boolean>;
}

export interface Auditoria {
  registrar(evento: EventoAuditoria): Promise<void>;
}

export function filaAuditoria(evento: EventoAuditoria, ahora = new Date()): Record<string, unknown> {
  const ts = ahora.toISOString();
  return { dia: ts.slice(0, 10), tsId: `${ts}#${randomUUID()}`, ts, ...evento };
}

export function auditoriaDynamo(cliente: DynamoDBDocumentClient, tabla: string): Auditoria {
  return {
    async registrar(evento) {
      await cliente.send(new PutCommand({ TableName: tabla, Item: filaAuditoria(evento) }));
    },
  };
}
