// Apoyo de pruebas: eventos de API Gateway, verificador JWT falso y auditoría en memoria.
import type { APIGatewayProxyEvent } from "aws-lambda";
import type { Auditoria, EventoAuditoria } from "../src/auditoria";
import type { VerificadorJwt } from "../src/identidad";

export const ANA = "11111111-1111-4111-8111-111111111111";
export const BETO = "22222222-2222-4222-8222-222222222222";
export const ADMIN = "33333333-3333-4333-8333-333333333333";

/** Token "firmado" de prueba: tres partes, la del medio dice el sub y los grupos. */
export function token(sub: string, grupos: string[] = []): string {
  return `cabecera.${Buffer.from(JSON.stringify({ sub, grupos })).toString("base64url")}.firma`;
}

export const verificadorFalso: VerificadorJwt = {
  async verify(t: string) {
    const [, carga, firma] = t.split(".");
    if (firma !== "firma" || !carga) throw new Error("firma inválida");
    const { sub, grupos } = JSON.parse(Buffer.from(carga, "base64url").toString("utf8")) as { sub: string; grupos: string[] };
    return { sub, "cognito:groups": grupos, token_use: "access" };
  },
};

export interface OpcionesEvento {
  sub?: string | null;
  grupos?: string[];
  cuerpo?: unknown;
  cuerpoCrudo?: string;
  consulta?: Record<string, string>;
  ruta?: Record<string, string>;
  cabeceras?: Record<string, string>;
}

export function evento(metodo: string, recurso: string, o: OpcionesEvento = {}): APIGatewayProxyEvent {
  const sub = o.sub === undefined ? ANA : o.sub;
  return {
    httpMethod: metodo,
    resource: recurso,
    path: recurso,
    headers: { ...(sub ? { Authorization: `Bearer ${token(sub, o.grupos)}` } : {}), ...(o.cabeceras ?? {}) },
    multiValueHeaders: {},
    queryStringParameters: o.consulta ?? null,
    multiValueQueryStringParameters: null,
    pathParameters: o.ruta ?? null,
    stageVariables: null,
    body: o.cuerpoCrudo ?? (o.cuerpo === undefined ? null : JSON.stringify(o.cuerpo)),
    isBase64Encoded: false,
    requestContext: { requestId: "prueba-123", authorizer: sub ? { claims: { sub } } : null } as unknown as APIGatewayProxyEvent["requestContext"],
  };
}

export function auditoriaMemoria(): Auditoria & { eventos: EventoAuditoria[] } {
  const eventos: EventoAuditoria[] = [];
  return {
    eventos,
    async registrar(e) {
      eventos.push(e);
    },
  };
}

export function cuerpo(r: { body: string }): Record<string, unknown> {
  return r.body ? (JSON.parse(r.body) as Record<string, unknown>) : {};
}
