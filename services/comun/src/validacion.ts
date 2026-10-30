// Validación de entrada con zod en modo estricto (CTRL-04, API3:2023, A05:2025).
// - .strict(): cualquier campo no previsto se rechaza (evita mass assignment).
// - Tamaño máximo del cuerpo antes de interpretar el JSON.
// - Todas las listas llevan tope de elementos (evita GHSA-mrhx-c7xc-m3w5 y similares).
import type { APIGatewayProxyEvent } from "aws-lambda";
import { z } from "zod";
import { ErrorHttp } from "./http";

export const TAMANO_MAXIMO_CUERPO = 8 * 1024;

function rechazar(error: z.ZodError): never {
  const campos = [...new Set(error.issues.map((i) => i.path.join(".") || "(raíz)"))].slice(0, 10);
  throw new ErrorHttp(400, "solicitud_invalida", campos);
}

export function leerCuerpo<T extends z.ZodType>(event: APIGatewayProxyEvent, esquema: T): z.infer<T> {
  const crudo = event.isBase64Encoded && event.body ? Buffer.from(event.body, "base64").toString("utf8") : event.body;
  if (crudo === null || crudo === undefined || crudo === "") throw new ErrorHttp(400, "solicitud_invalida", ["(cuerpo)"]);
  if (Buffer.byteLength(crudo, "utf8") > TAMANO_MAXIMO_CUERPO) throw new ErrorHttp(413, "cuerpo_muy_grande");
  let datos: unknown;
  try {
    datos = JSON.parse(crudo);
  } catch {
    throw new ErrorHttp(400, "solicitud_invalida", ["(json)"]);
  }
  const r = esquema.safeParse(datos);
  if (!r.success) rechazar(r.error);
  return r.data;
}

export function leerConsulta<T extends z.ZodType>(event: APIGatewayProxyEvent, esquema: T): z.infer<T> {
  const r = esquema.safeParse(event.queryStringParameters ?? {});
  if (!r.success) rechazar(r.error);
  return r.data;
}

export function leerRuta<T extends z.ZodType>(event: APIGatewayProxyEvent, esquema: T): z.infer<T> {
  const r = esquema.safeParse(event.pathParameters ?? {});
  if (!r.success) rechazar(r.error);
  return r.data;
}

/** Montos siempre en centavos enteros (nunca decimales de punto flotante). */
export const centavos = z.number().int().positive().max(100_000_000);
export const uuid = z.uuid();
export const mes = z.string().regex(/^20\d{2}-(0[1-9]|1[0-2])$/);
export const dia = z.string().regex(/^20\d{2}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$/);
export const texto = (min: number, max: number) =>
  z
    .string()
    .trim()
    .min(min)
    .max(max)
    // Solo letras, números, espacios y puntuación básica: nada de < > { } ni caracteres de control.
    .regex(/^[\p{L}\p{N} .,'#()\-]+$/u);
