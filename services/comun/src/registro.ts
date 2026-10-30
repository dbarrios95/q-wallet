// Logs JSON estructurados con redacción de datos sensibles (CTRL-09, A09 / CWE-532).
// Cada línea lleva correlationId para unir el log con la respuesta y la auditoría.

/** Campos que nunca se escriben en un log, sin importar dónde aparezcan. */
const SENSIBLES = new Set([
  "authorization",
  "token",
  "accesstoken",
  "idtoken",
  "refreshtoken",
  "pin",
  "pinhash",
  "hash",
  "sal",
  "telefono",
  "phone",
  "dpi",
  "email",
  "correo",
  "password",
  "contrasena",
  "secret",
  "secreto",
  "cookie",
]);

const JWT = /eyJ[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]*/g;

export function redactar(valor: unknown, profundidad = 0): unknown {
  if (profundidad > 6) return "[profundo]";
  if (typeof valor === "string") return valor.replace(JWT, "[jwt-redactado]");
  if (Array.isArray(valor)) return valor.map((v) => redactar(v, profundidad + 1));
  if (valor && typeof valor === "object") {
    const salida: Record<string, unknown> = {};
    for (const [k, v] of Object.entries(valor as Record<string, unknown>)) {
      salida[k] = SENSIBLES.has(k.toLowerCase().replace(/[-_]/g, "")) ? "[redactado]" : redactar(v, profundidad + 1);
    }
    return salida;
  }
  return valor;
}

export type Nivel = "info" | "aviso" | "error";

export interface Registro {
  info(evento: string, datos?: Record<string, unknown>): void;
  aviso(evento: string, datos?: Record<string, unknown>): void;
  error(evento: string, datos?: Record<string, unknown>): void;
}

export function crearRegistro(
  servicio: string,
  correlationId: string,
  salida: (linea: string) => void = (l) => console.log(l),
): Registro {
  const escribir = (nivel: Nivel, evento: string, datos?: Record<string, unknown>) =>
    salida(
      JSON.stringify({
        nivel,
        evento,
        servicio,
        correlationId,
        ts: new Date().toISOString(),
        ...(datos ? (redactar(datos) as Record<string, unknown>) : {}),
      }),
    );
  return {
    info: (e, d) => escribir("info", e, d),
    aviso: (e, d) => escribir("aviso", e, d),
    error: (e, d) => escribir("error", e, d),
  };
}
