// PIN de transacción (CTRL-02, API6:2023, CWE-307 / CWE-916).
// - Hash scrypt (Node crypto) con sal aleatoria de 16 bytes por usuario.
// - Comparación en tiempo constante.
// - Bloqueo de 15 minutos al quinto intento fallido.
// - Se rechazan PIN triviales (todos iguales o consecutivos).
import { randomBytes, scrypt as scryptCb, timingSafeEqual, type ScryptOptions } from "node:crypto";
import { z } from "zod";

const N = 2 ** 15;
const R = 8;
const P = 1;
const LARGO = 32;

export const INTENTOS_MAXIMOS = 5;
export const MINUTOS_BLOQUEO = 15;

function scrypt(pin: string, sal: Buffer, n: number, r: number, p: number): Promise<Buffer> {
  const opciones: ScryptOptions = { N: n, r, p, maxmem: 128 * n * r * 2 };
  return new Promise((ok, mal) => scryptCb(pin, sal, LARGO, opciones, (e, h) => (e ? mal(e) : ok(h))));
}

function esTrivial(pin: string): boolean {
  if (/^(\d)\1+$/.test(pin)) return true;
  const d = [...pin].map(Number);
  const sube = d.every((x, i) => i === 0 || x === (d[i - 1]! + 1) % 10);
  const baja = d.every((x, i) => i === 0 || x === (d[i - 1]! + 9) % 10);
  return sube || baja;
}

export const pinNuevo = z
  .string()
  .regex(/^\d{6}$/)
  .refine((p) => !esTrivial(p), { message: "pin trivial" });

export const pinIngresado = z.string().regex(/^\d{6}$/);

/** Formato guardado: scrypt$N$r$p$sal$hash (permite subir el costo en el futuro). */
export async function hashPin(pin: string): Promise<string> {
  const sal = randomBytes(16);
  const h = await scrypt(pin, sal, N, R, P);
  return `scrypt$${N}$${R}$${P}$${sal.toString("base64")}$${h.toString("base64")}`;
}

export async function verificarPin(pin: string, guardado: string): Promise<boolean> {
  const partes = guardado.split("$");
  if (partes.length !== 6 || partes[0] !== "scrypt") return false;
  const [, n, r, p, salB64, hashB64] = partes as [string, string, string, string, string, string];
  const esperado = Buffer.from(hashB64, "base64");
  const calculado = await scrypt(pin, Buffer.from(salB64, "base64"), Number(n), Number(r), Number(p));
  return esperado.length === calculado.length && timingSafeEqual(esperado, calculado);
}

export interface EstadoPin {
  hash: string;
  intentos: number;
  bloqueadoHasta?: number; // epoch en milisegundos
}

export function estaBloqueado(estado: EstadoPin, ahora = Date.now()): boolean {
  return (estado.bloqueadoHasta ?? 0) > ahora;
}

/** Devuelve el nuevo estado después de un intento fallido. */
export function trasFallo(intentosPrevios: number, ahora = Date.now()): { intentos: number; bloqueadoHasta?: number } {
  const intentos = intentosPrevios + 1;
  return intentos >= INTENTOS_MAXIMOS ? { intentos: 0, bloqueadoHasta: ahora + MINUTOS_BLOQUEO * 60_000 } : { intentos };
}
