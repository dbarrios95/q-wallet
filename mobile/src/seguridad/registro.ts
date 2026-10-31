// Marcas de seguridad para el registro del sistema (logcat, etiqueta ReactNativeJS).
// Solo se escribe el tipo de evento y datos técnicos: nunca tokens, montos ni PII
// (CTRL-09). Las pruebas del flujo movil.yml buscan el prefijo QWALLET_.

export function marcaSeguridad(origen: "RASP" | "API", datos: Record<string, string | number>): void {
  const partes = Object.entries(datos).map(([k, v]) => `${k}=${String(v).replace(/\s+/g, "_")}`);
  // eslint-disable-next-line no-console -- marca técnica sin datos personales, ver comentario arriba
  console.info(`QWALLET_${origen} ${partes.join(" ")}`);
}
