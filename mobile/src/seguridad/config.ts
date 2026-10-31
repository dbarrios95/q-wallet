// Configuración de seguridad de la app (bloque 5).
// Nada de esto es secreto: la URL de la API es pública (endpoint execute-api) y
// los pines son huellas de llaves públicas. No hay secretos en el cliente (CTRL-16).

/** Etapa v1 de la API (API Gateway regional, solo TLS 1.3). */
export const API_HOST = "dk1m3avi8i.execute-api.us-east-1.amazonaws.com";
// Se arma con texto: el URL de React Native no implementa .host (lanza error).
export const API_URL = `https://${API_HOST}/v1`;

/**
 * CTRL-08: pinning por llave pública (SHA-256 del SubjectPublicKeyInfo, en base64)
 * de las raíces de Amazon Trust Services. Se fija la raíz y no el certificado del
 * servidor porque AWS rota el certificado del endpoint sin aviso; las cuatro raíces
 * dan pines de respaldo. Calculados desde el almacén de raíces del sistema (bloque 5)
 * y verificados contra la cadena real en el flujo movil.yml.
 */
export const PINES_AMAZON = [
  "++MBgDH5WGvL9Bcn5Be30cRcL0f5O+NyoXuWtQdX1aI=", // Amazon Root CA 1 (RSA 2048)
  "f0KW/FtqTjs108NpYj42SrGvOB2PpxIVM8nWxjPqJGE=", // Amazon Root CA 2 (RSA 4096)
  "NqvDJlas/GRcYbcWE8S/IceH9cq77kg0jVhZeAPXq8k=", // Amazon Root CA 3 (ECC P-256)
  "9+ze1cZgR9KO1kZrVDxA4HQ6voHRCSVNz4RdTCx4U8U=", // Amazon Root CA 4 (ECC P-384)
];

/**
 * CTRL-15: huella SHA-256 (base64) del certificado con que se firma el APK.
 * freeRASP la compara para detectar un APK re-empaquetado (appIntegrity).
 * La pone el flujo de compilación (variable EXPO_PUBLIC_RASP_CERT_HASH); en un
 * despliegue real sería la del certificado de firma de Google Play.
 */
export const HUELLA_FIRMA_APK = process.env.EXPO_PUBLIC_RASP_CERT_HASH ?? "";

export const PAQUETE_ANDROID = "gt.qwallet.app";

/** freeRASP envía reportes semanales a este buzón. Buzón del proyecto, no personal. */
export const CORREO_RASP = "seguridad@qwallet.example";
