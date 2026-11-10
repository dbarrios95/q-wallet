// CTRL-18 y CTRL-07 (bloque 7): inicio de sesión real con Amazon Cognito y guarda segura de la sesión.
//
//   - Login administrado de Cognito (Authorization Code + PKCE S256, cliente público sin secreto).
//     La contraseña y el código TOTP (MFA obligatorio) se escriben en la página de Cognito, abierta
//     en una pestaña segura del navegador del sistema (Custom Tab): la app nunca los ve.
//   - El canje del código y la renovación de tokens van por pedirHttps() con pinning (CTRL-08),
//     no por el fetch de expo-auth-session.
//   - access token e id token: solo en memoria (duran 15 minutos).
//   - refresh token (12 horas, con rotación): en expo-secure-store, cifrado con una llave AES de
//     Android Keystore. Si el teléfono tiene biometría fuerte, la llave exige huella o rostro
//     (requireAuthentication); si solo tiene PIN o patrón, la app pide el bloqueo del teléfono antes
//     de leerlo. Sin ningún bloqueo de pantalla no se guarda: la sesión muere al cerrar la app.
//   - Cerrar sesión revoca el refresh token en Cognito (/oauth2/revoke) y borra lo guardado.
// Nunca se escriben tokens en el registro (CTRL-09): solo marcas QWALLET_AUTH sin datos.

import { Buffer } from "buffer";
import { useSyncExternalStore } from "react";
import { AuthRequest, ResponseType } from "expo-auth-session";
import * as LocalAuthentication from "expo-local-authentication";
import * as SecureStore from "expo-secure-store";
import { z } from "zod";
import { API_SCOPE, COGNITO_CLIENT_ID, COGNITO_HOST, REDIRECT_LOGIN } from "./config";
import { pedirHttps } from "./red";
import { marcaSeguridad } from "./registro";

const CLAVE_REFRESH = "qw_refresh";
const CLAVE_MODO = "qw_modo"; // "bio" (llave con biometría) o "bloqueo" (PIN o patrón del teléfono)

const BASE = `https://${COGNITO_HOST}`;
const descubrimiento = {
  authorizationEndpoint: `${BASE}/oauth2/authorize`,
  tokenEndpoint: `${BASE}/oauth2/token`,
  revocationEndpoint: `${BASE}/oauth2/revoke`,
};

const respuestaTokens = z.object({
  access_token: z.string().min(20),
  id_token: z.string().min(20),
  refresh_token: z.string().min(20).optional(),
  expires_in: z.number().int().positive(),
  token_type: z.literal("Bearer"),
});

export type Usuario = { correo: string; sub: string };

type Estado = {
  usuario: Usuario | null;
  acceso: string | null;
  vence: number; // ms
  refresh: string | null;
};

let estado: Estado = { usuario: null, acceso: null, vence: 0, refresh: null };
const oyentes = new Set<() => void>();
function cambiar(nuevo: Partial<Estado>): void {
  estado = { ...estado, ...nuevo };
  oyentes.forEach((o) => o());
}

/** Usuario con sesión abierta (o null), para las pantallas. */
export function useUsuario(): Usuario | null {
  return useSyncExternalStore(
    (o) => {
      oyentes.add(o);
      return () => oyentes.delete(o);
    },
    () => estado.usuario,
  );
}

export function loginConfigurado(): boolean {
  return COGNITO_HOST.length > 0 && COGNITO_CLIENT_ID.length > 0;
}

/** Lee los campos de un JWT recibido por TLS con pinning desde el emisor (solo para mostrar). */
function campos(jwt: string): Record<string, unknown> {
  const parte = jwt.split(".")[1] ?? "";
  return JSON.parse(Buffer.from(parte.replace(/-/g, "+").replace(/_/g, "/"), "base64").toString("utf8"));
}

function formulario(datos: Record<string, string>): string {
  return Object.entries(datos)
    .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
    .join("&");
}

async function pedirTokens(datos: Record<string, string>): Promise<z.infer<typeof respuestaTokens>> {
  const r = await pedirHttps(descubrimiento.tokenEndpoint, {
    metodo: "POST",
    cabeceras: { "Content-Type": "application/x-www-form-urlencoded" },
    cuerpo: formulario({ ...datos, client_id: COGNITO_CLIENT_ID }),
  });
  if (r.estado !== 200) {
    marcaSeguridad("AUTH", { tokens: "rechazado", estado: r.estado, grant: datos.grant_type ?? "" });
    throw new Error("tokens_rechazados");
  }
  return respuestaTokens.parse(JSON.parse(r.cuerpo));
}

function abrirSesion(t: z.infer<typeof respuestaTokens>): void {
  const id = campos(t.id_token);
  const acceso = campos(t.access_token);
  // Defensa en profundidad: el token debe ser de este cliente y traer el alcance de la API.
  if (acceso.client_id !== COGNITO_CLIENT_ID || !String(acceso.scope ?? "").split(" ").includes(API_SCOPE)) {
    throw new Error("token_de_otro_cliente");
  }
  cambiar({
    usuario: { correo: String(id.email ?? ""), sub: String(id.sub ?? "") },
    acceso: t.access_token,
    vence: Date.now() + t.expires_in * 1000,
    refresh: t.refresh_token ?? estado.refresh,
  });
}

/** Guarda el refresh token según lo que permita el teléfono. Devuelve dónde quedó. */
async function guardarRefresh(refresh: string): Promise<"bio" | "bloqueo" | "memoria"> {
  const nivel = await LocalAuthentication.getEnrolledLevelAsync();
  if (nivel === LocalAuthentication.SecurityLevel.NONE) {
    await borrarGuardado();
    return "memoria";
  }
  const bio = nivel === LocalAuthentication.SecurityLevel.BIOMETRIC_STRONG && SecureStore.canUseBiometricAuthentication();
  await SecureStore.setItemAsync(CLAVE_REFRESH, refresh, {
    requireAuthentication: bio,
    authenticationPrompt: "Confirma tu identidad para guardar la sesión",
    keychainAccessible: SecureStore.WHEN_PASSCODE_SET_THIS_DEVICE_ONLY,
  });
  await SecureStore.setItemAsync(CLAVE_MODO, bio ? "bio" : "bloqueo");
  return bio ? "bio" : "bloqueo";
}

async function borrarGuardado(): Promise<void> {
  await SecureStore.deleteItemAsync(CLAVE_REFRESH);
  await SecureStore.deleteItemAsync(CLAVE_MODO);
}

/** Abre el login administrado de Cognito. true si la sesión quedó abierta. */
export async function iniciarSesion(): Promise<boolean> {
  if (!loginConfigurado()) throw new Error("login_no_configurado");
  const solicitud = new AuthRequest({
    clientId: COGNITO_CLIENT_ID,
    redirectUri: REDIRECT_LOGIN,
    scopes: ["openid", "email", API_SCOPE],
    responseType: ResponseType.Code,
    usePKCE: true, // S256 por defecto
    extraParams: { lang: "es" },
  });
  const resultado = await solicitud.promptAsync(descubrimiento, { showInRecents: false });
  // AuthRequest ya comprobó que el state que volvió es el que se mandó (anti-CSRF).
  if (resultado.type !== "success" || !resultado.params.code || !solicitud.codeVerifier) {
    marcaSeguridad("AUTH", { login: resultado.type });
    return false;
  }
  const tokens = await pedirTokens({
    grant_type: "authorization_code",
    code: resultado.params.code,
    redirect_uri: REDIRECT_LOGIN,
    code_verifier: solicitud.codeVerifier,
  });
  abrirSesion(tokens);
  const guardado = tokens.refresh_token ? await guardarRefresh(tokens.refresh_token) : "memoria";
  marcaSeguridad("AUTH", { login: "ok", pkce: "S256", refresh: guardado });
  return true;
}

/** ¿Hay una sesión guardada que se pueda desbloquear? */
export async function haySesionGuardada(): Promise<boolean> {
  return (await SecureStore.getItemAsync(CLAVE_MODO)) !== null;
}

/**
 * Desbloqueo al volver a abrir la app: biometría (la exige la propia llave de Keystore) o el
 * bloqueo del teléfono, y después renovación de tokens en Cognito. true si quedó abierta.
 */
export async function desbloquear(): Promise<boolean> {
  const modo = await SecureStore.getItemAsync(CLAVE_MODO);
  if (!modo) return false;
  if (modo === "bloqueo") {
    const r = await LocalAuthentication.authenticateAsync({
      promptMessage: "Desbloquear Q-Wallet",
      cancelLabel: "Cancelar",
      disableDeviceFallback: false,
    });
    if (!r.success) return false;
  }
  let refresh: string | null;
  try {
    refresh = await SecureStore.getItemAsync(CLAVE_REFRESH, {
      requireAuthentication: modo === "bio",
      authenticationPrompt: "Desbloquear Q-Wallet",
    });
  } catch {
    // Biometría cancelada, o la llave se invalidó porque cambió la huella registrada.
    marcaSeguridad("AUTH", { desbloqueo: "llave_no_disponible" });
    return false;
  }
  if (!refresh) return false;
  try {
    const tokens = await pedirTokens({ grant_type: "refresh_token", refresh_token: refresh });
    cambiar({ refresh });
    abrirSesion(tokens);
    if (tokens.refresh_token) await guardarRefresh(tokens.refresh_token); // rotación
    marcaSeguridad("AUTH", { desbloqueo: "ok", modo });
    return true;
  } catch {
    // Refresh vencido o revocado: hay que iniciar sesión de nuevo.
    await borrarGuardado();
    marcaSeguridad("AUTH", { desbloqueo: "refresh_invalido" });
    return false;
  }
}

/** Access token vigente (lo renueva con el refresh en memoria si está por vencer). */
export async function tokenAcceso(): Promise<string> {
  if (estado.acceso && Date.now() < estado.vence - 60_000) return estado.acceso;
  if (!estado.refresh) throw new Error("sin_sesion");
  const tokens = await pedirTokens({ grant_type: "refresh_token", refresh_token: estado.refresh });
  abrirSesion(tokens);
  if (tokens.refresh_token && (await haySesionGuardada())) await guardarRefresh(tokens.refresh_token);
  return estado.acceso as string;
}

/** Cierra la sesión: revoca el refresh token en Cognito y borra todo lo local. */
export async function cerrarSesion(): Promise<void> {
  const refresh = estado.refresh;
  cambiar({ usuario: null, acceso: null, vence: 0, refresh: null });
  await borrarGuardado();
  if (refresh) {
    try {
      const r = await pedirHttps(descubrimiento.revocationEndpoint, {
        metodo: "POST",
        cabeceras: { "Content-Type": "application/x-www-form-urlencoded" },
        cuerpo: formulario({ token: refresh, client_id: COGNITO_CLIENT_ID }),
      });
      marcaSeguridad("AUTH", { logout: "ok", revocacion: r.estado });
    } catch {
      marcaSeguridad("AUTH", { logout: "ok", revocacion: "sin_conexion" });
    }
  }
}
