// Identidad del que llama (CTRL-18, CTRL-14) y manejo seguro del JWT.
// API Gateway ya validó el access token con el authorizer de Cognito. La Lambda lo
// vuelve a verificar (defensa en profundidad): firma con las llaves públicas del user
// pool, emisor, expiración, token_use = access, client_id de la app y el scope de la API.
// Así, si alguien invoca la función por otra vía o el authorizer se configura mal,
// la Lambda no confía en encabezados sin firma.
import { CognitoJwtVerifier } from "aws-jwt-verify";
import type { APIGatewayProxyEvent } from "aws-lambda";
import { ErrorHttp } from "./http";

export interface Identidad {
  sub: string;
  grupos: string[];
  esAdmin: boolean;
}

export interface VerificadorJwt {
  verify(token: string): Promise<Record<string, unknown>>;
}

let verificadorPorDefecto: VerificadorJwt | undefined;

export function verificadorCognito(): VerificadorJwt {
  if (!verificadorPorDefecto) {
    const userPoolId = process.env.USER_POOL_ID;
    const clientId = process.env.COGNITO_CLIENT_ID;
    const scope = process.env.API_SCOPE;
    if (!userPoolId || !clientId || !scope) throw new Error("Falta configuración de Cognito");
    // El verificador guarda en memoria las llaves públicas (JWKS) entre invocaciones.
    verificadorPorDefecto = CognitoJwtVerifier.create({ userPoolId, tokenUse: "access", clientId, scope }) as unknown as VerificadorJwt;
  }
  return verificadorPorDefecto;
}

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

function leerToken(event: APIGatewayProxyEvent): string {
  const cabeceras = event.headers ?? {};
  const valor = Object.entries(cabeceras).find(([k]) => k.toLowerCase() === "authorization")?.[1];
  if (!valor) throw new ErrorHttp(401, "no_autenticado");
  const token = valor.startsWith("Bearer ") ? valor.slice(7) : valor;
  if (token.length > 4096 || token.split(".").length !== 3) throw new ErrorHttp(401, "no_autenticado");
  return token;
}

export async function obtenerIdentidad(event: APIGatewayProxyEvent, verificador: VerificadorJwt): Promise<Identidad> {
  const token = leerToken(event);
  let carga: Record<string, unknown>;
  try {
    carga = await verificador.verify(token);
  } catch {
    // Firma inválida, token vencido, de otro cliente o sin el scope: no se da detalle.
    throw new ErrorHttp(401, "no_autenticado");
  }
  const sub = carga.sub;
  if (typeof sub !== "string" || !UUID.test(sub)) throw new ErrorHttp(401, "no_autenticado");

  // El sub que puso el authorizer (si existe) debe ser el mismo del token verificado.
  const subAuthorizer = (event.requestContext?.authorizer as { claims?: { sub?: unknown } } | null)?.claims?.sub;
  if (subAuthorizer !== undefined && subAuthorizer !== sub) throw new ErrorHttp(401, "no_autenticado");

  const crudo = carga["cognito:groups"];
  const grupos = Array.isArray(crudo) ? crudo.filter((g): g is string => typeof g === "string") : [];
  return { sub, grupos, esAdmin: grupos.includes("admins") };
}

/** CTRL-14: autorización por función. Solo el grupo admins de Cognito pasa. */
export function exigirAdmin(identidad: Identidad): void {
  if (!identidad.esAdmin) throw new ErrorHttp(403, "prohibido");
}

export function esUuid(valor: string): boolean {
  return UUID.test(valor);
}
