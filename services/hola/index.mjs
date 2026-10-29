// Imagen provisional del bloque 1: responde que el servicio está en construcción.
// No lee datos ni registra el cuerpo de la solicitud. El código real de cada
// microservicio (con CTRL-01 a CTRL-06, CTRL-09 y CTRL-14) llega en el bloque 3.
const CABECERAS = {
  "Content-Type": "application/json",
  "Cache-Control": "no-store",
  "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
  "X-Content-Type-Options": "nosniff",
  "X-Frame-Options": "DENY",
};

export const handler = async (event) => {
  const correlationId = event?.requestContext?.requestId ?? "sin-id";
  console.log(JSON.stringify({ nivel: "info", correlationId, servicio: process.env.SERVICIO, ruta: event?.resource, metodo: event?.httpMethod }));
  return {
    statusCode: 501,
    headers: CABECERAS,
    body: JSON.stringify({ servicio: process.env.SERVICIO, estado: "en construccion", correlationId }),
  };
};
