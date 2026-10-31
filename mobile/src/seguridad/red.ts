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

/**
 * Cliente de la API de Q-Wallet. Usa XMLHttpRequest, que en React Native pasa por el
 * cliente OkHttp de NetworkingModule, donde la librería instala el CertificatePinner.
 * HAL-13: en Expo SDK 57 el fetch global es expo/fetch (otro cliente, sin pinning); por eso
 * la app no usa fetch para la API (regla Semgrep qwallet-fetch-sin-pinning).
 */
export async function llamarApi(
  ruta: string,
  opciones: { metodo?: "GET" | "POST" | "PATCH" | "PUT" | "DELETE"; token?: string; cuerpo?: unknown } = {},
): Promise<{ estado: number; cuerpo: string }> {
  await iniciarPinning();
  return new Promise((resolver, rechazar) => {
    const xhr = new XMLHttpRequest();
    xhr.open(opciones.metodo ?? "GET", `${API_URL}${ruta}`);
    xhr.setRequestHeader("Accept", "application/json");
    if (opciones.token) xhr.setRequestHeader("Authorization", `Bearer ${opciones.token}`);
    if (opciones.cuerpo !== undefined) xhr.setRequestHeader("Content-Type", "application/json");
    xhr.timeout = 15000;
    xhr.onload = () => resolver({ estado: xhr.status, cuerpo: xhr.responseText });
    xhr.onerror = () => rechazar(new Error("conexion_rechazada"));
    xhr.ontimeout = () => rechazar(new Error("tiempo_agotado"));
    xhr.send(opciones.cuerpo === undefined ? null : JSON.stringify(opciones.cuerpo));
  });
}

/**
 * Sonda al arrancar: GET /me sin token por el cliente de la API (esperado: 401 con pinning).
 * También registra, solo como diagnóstico de HAL-13, qué pasa con el fetch global de Expo;
 * la app no lo usa para hablar con la API.
 */
export async function sondaApi(): Promise<void> {
  const pinning = await iniciarPinning();
  const caminos: [string, () => Promise<number>][] = [
    ["cliente_api", async () => (await llamarApi("/me")).estado],
    ["fetch_global_diagnostico", async () => (await fetch(`${API_URL}/me`, { headers: { Accept: "application/json" } })).status],
  ];
  for (const [via, pedir] of caminos) {
    const inicio = Date.now();
    try {
      const estado = await pedir();
      marcaSeguridad("API", { sonda: "GET_/me", via, estado, pinning: pinning ? "activo" : "inactivo", ms: Date.now() - inicio });
    } catch (e) {
      const tipo = e instanceof Error ? e.message || e.name : "desconocido";
      marcaSeguridad("API", { sonda: "GET_/me", via, estado: "sin_conexion", motivo: tipo, ms: Date.now() - inicio });
    }
  }
}
