// Paginación por cursor con tope (CTRL-05, API4:2023).
// - limit entre 1 y 50 (por defecto 20). Nunca se devuelve una tabla completa.
// - El cursor es la última llave leída, en base64url. Al recibirlo se valida su forma
//   y que la llave de partición sea la misma que la consulta pide: un cursor armado
//   con la cuenta de otra persona se rechaza (no sirve para saltar a datos ajenos).
import { z } from "zod";
import { ErrorHttp } from "./http";

export const LIMITE_MAXIMO = 50;
export const LIMITE_POR_DEFECTO = 20;

export const limite = z.coerce.number().int().min(1).max(LIMITE_MAXIMO).default(LIMITE_POR_DEFECTO);
export const cursor = z.string().max(512).regex(/^[A-Za-z0-9_-]+$/).optional();

export function codificarCursor(llave: Record<string, unknown> | undefined): string | null {
  if (!llave) return null;
  return Buffer.from(JSON.stringify(llave), "utf8").toString("base64url");
}

export function decodificarCursor(
  valor: string | undefined,
  campos: readonly string[],
  particion: { campo: string; valor: string },
): Record<string, string> | undefined {
  if (!valor) return undefined;
  let llave: unknown;
  try {
    llave = JSON.parse(Buffer.from(valor, "base64url").toString("utf8"));
  } catch {
    throw new ErrorHttp(400, "solicitud_invalida", ["cursor"]);
  }
  const forma = z.object(Object.fromEntries(campos.map((c) => [c, z.string().min(1).max(200)]))).strict();
  const r = forma.safeParse(llave);
  if (!r.success) throw new ErrorHttp(400, "solicitud_invalida", ["cursor"]);
  const datos = r.data as Record<string, string>;
  if (datos[particion.campo] !== particion.valor) throw new ErrorHttp(400, "solicitud_invalida", ["cursor"]);
  return datos;
}
