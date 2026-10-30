// Datos personales: teléfono normalizado, huella para búsqueda y enmascarado (CTRL-03).
import { createHash } from "node:crypto";
import { z } from "zod";

/** Teléfono de Guatemala: +502 y 8 dígitos que empiezan con 2 a 7 (fijo o móvil). */
export const telefono = z
  .string()
  .trim()
  .transform((t) => t.replace(/[\s-]/g, ""))
  .pipe(z.string().regex(/^(\+502)?[2-7]\d{7}$/))
  .transform((t) => (t.startsWith("+502") ? t : `+502${t}`));

/**
 * Huella del teléfono para el índice por-telefono. Es un SHA-256 del número
 * normalizado: sirve para buscar sin usar el número como llave. No es un secreto
 * (el espacio de números es pequeño); la protección del dato es el cifrado de la
 * tabla con la llave propia y el permiso IAM por tabla.
 */
export function huellaTelefono(normalizado: string): string {
  return createHash("sha256").update(`qwallet:tel:${normalizado}`).digest("hex");
}

export function enmascararTelefono(normalizado: string): string {
  return `****${normalizado.slice(-4)}`;
}

export function enmascararDpi(dpi: string): string {
  return `*********${dpi.slice(-4)}`;
}

export function enmascararCorreo(correo: string): string {
  const [usuario = "", dominio = ""] = correo.split("@");
  return `${usuario.slice(0, 1)}***@${dominio}`;
}

/** "Daniel Barrios" -> "Daniel B." (para confirmar el destinatario sin exponer el nombre completo). */
export function nombreCorto(nombre: string): string {
  const partes = nombre.trim().split(/\s+/);
  const [primero = ""] = partes;
  const ultimo = partes.length > 1 ? partes[partes.length - 1] : undefined;
  return ultimo ? `${primero} ${ultimo.slice(0, 1)}.` : primero;
}
