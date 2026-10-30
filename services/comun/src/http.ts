// Respuestas HTTP y errores controlados (CTRL-13).
// - Cabeceras de seguridad en todas las respuestas.
// - Sin Access-Control-Allow-Origin: la API solo la usa la app Android; un navegador no puede leerla.
// - Los errores son genéricos: código corto + correlationId, nunca la pila ni el mensaje interno.
import type { APIGatewayProxyResult } from "aws-lambda";

export const CABECERAS: Readonly<Record<string, string>> = {
  "Content-Type": "application/json; charset=utf-8",
  "Cache-Control": "no-store",
  "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
  "X-Content-Type-Options": "nosniff",
  "X-Frame-Options": "DENY",
  "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'",
  "Referrer-Policy": "no-referrer",
};

/** Error que el manejador convierte en una respuesta controlada. */
export class ErrorHttp extends Error {
  constructor(
    public readonly status: number,
    public readonly codigo: string,
    public readonly campos?: string[],
  ) {
    super(codigo);
    this.name = "ErrorHttp";
  }
}

/** Mensajes fijos por código: el cliente nunca ve detalles internos. */
const MENSAJES: Record<string, string> = {
  solicitud_invalida: "La solicitud no es válida.",
  no_autenticado: "Se requiere iniciar sesión.",
  prohibido: "No tiene permiso para esta operación.",
  no_encontrado: "El recurso no existe.",
  conflicto: "La operación entra en conflicto con el estado actual.",
  pin_incorrecto: "El PIN no es correcto.",
  pin_bloqueado: "El PIN está bloqueado temporalmente. Intente más tarde.",
  saldo_insuficiente: "Saldo insuficiente.",
  limite_excedido: "El monto supera el límite permitido.",
  cuerpo_muy_grande: "La solicitud es demasiado grande.",
  ruta_no_soportada: "Operación no soportada.",
  error_interno: "Ocurrió un error. Intente de nuevo más tarde.",
};

export function responder(status: number, cuerpo: unknown, correlationId: string): APIGatewayProxyResult {
  return {
    statusCode: status,
    headers: { ...CABECERAS, "X-Correlation-Id": correlationId },
    body: status === 204 ? "" : JSON.stringify(cuerpo),
  };
}

export function responderError(error: ErrorHttp, correlationId: string): APIGatewayProxyResult {
  const cuerpo: Record<string, unknown> = {
    error: error.codigo,
    mensaje: MENSAJES[error.codigo] ?? MENSAJES.error_interno,
    correlationId,
  };
  // Solo los nombres de los campos rechazados, nunca su valor.
  if (error.campos?.length) cuerpo.campos = error.campos;
  return responder(error.status, cuerpo, correlationId);
}
