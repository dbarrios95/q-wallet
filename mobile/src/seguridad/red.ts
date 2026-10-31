// CTRL-08 (sección 5.2 y caso de abuso CA-08): pinning de llave pública y sonda
// mínima contra la API real. La sonda llama GET /me sin token: lo correcto es 401.
// Si alguien intercepta la conexión con un certificado propio (proxy MITM, aunque
// su CA esté instalada en el teléfono), el pinning corta la conexión y la app
// registra el error en lugar de hablar con el atacante.

import {
  addSslPinningErrorListener,
  initializeSslPinning,
  isSslPinningAvailable,
} from "react-native-ssl-public-key-pinning";
import { API_HOST, API_URL, PINES_AMAZON } from "./config";
import { marcaSeguridad } from "./registro";

let iniciado: Promise<boolean> | null = null;

/** Activa el pinning una sola vez. Devuelve false si el módulo nativo no está (Expo Go). */
export function iniciarPinning(): Promise<boolean> {
  if (!iniciado) {
    iniciado = (async () => {
      if (!isSslPinningAvailable()) {
        marcaSeguridad("API", { pinning: "no_disponible" });
        return false;
      }
      await initializeSslPinning({
        [API_HOST]: { includeSubdomains: false, publicKeyHashes: PINES_AMAZON },
      });
      addSslPinningErrorListener((e) => {
        marcaSeguridad("API", { error: "pinning", host: e.serverHostname });
      });
      marcaSeguridad("API", { pinning: "activo", host: API_HOST, pines: PINES_AMAZON.length });
      return true;
    })();
  }
  return iniciado;
}

/** Sonda: GET /me sin token. Resultado esperado: estado=401 con pinning activo. */
export async function sondaApi(): Promise<void> {
  const pinning = await iniciarPinning();
  const inicio = Date.now();
  try {
    const r = await fetch(`${API_URL}/me`, { method: "GET", headers: { Accept: "application/json" } });
    marcaSeguridad("API", { sonda: "GET_/me", estado: r.status, pinning: pinning ? "activo" : "inactivo", ms: Date.now() - inicio });
  } catch (e) {
    const tipo = e instanceof Error ? e.name : "desconocido";
    marcaSeguridad("API", { sonda: "GET_/me", estado: "sin_conexion", motivo: tipo, ms: Date.now() - inicio });
  }
}
