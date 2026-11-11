// CTRL-15 (sección 5.2): protección en tiempo de ejecución con freeRASP (Talsec).
// Detecta root, hooking (Frida), depurador, emulador, APK re-empaquetado y otros
// riesgos del dispositivo. Política de reacción:
//   - Amenazas que permiten leer o alterar la app en memoria (root, hooking,
//     depurador, integridad, emulador): en la versión de producción la app se
//     bloquea y no muestra datos ni permite operar.
//   - Señales del entorno (opciones de desarrollador, ADB, tienda no oficial,
//     VPN, sin bloqueo de pantalla...): solo se registran.
// En desarrollo (__DEV__) nada bloquea: el emulador de desarrollo es un "emulador".
// APK de prueba (bloque 7, solo CI): EXPO_PUBLIC_QWALLET_APK_PRUEBA=ca07 compila una copia que
// solo registra, para iniciar sesión en el emulador con root y revisar el almacenamiento (CA-07).
// La versión de producción no define la variable y bloquea igual; el flujo movil.yml lo comprueba.

import { useState } from "react";
import { useFreeRasp, type TalsecConfig, type ThreatEventActions } from "freerasp-react-native";
import { CORREO_RASP, HUELLA_FIRMA_APK, PAQUETE_ANDROID } from "./config";
import { marcaSeguridad } from "./registro";

const APK_PRUEBA_CA07 = process.env.EXPO_PUBLIC_QWALLET_APK_PRUEBA === "ca07";

export const AMENAZAS_QUE_BLOQUEAN = ["privilegedAccess", "hooks", "debug", "appIntegrity", "simulator"] as const;

const configuracion: TalsecConfig = {
  androidConfig: {
    packageName: PAQUETE_ANDROID,
    // Sin huella (compilación local de desarrollo) freeRASP marcará appIntegrity: es lo esperado.
    certificateHashes: [HUELLA_FIRMA_APK || "sin-huella-de-firma"],
  },
  watcherMail: CORREO_RASP,
  isProd: !__DEV__,
};

export type EstadoRasp = { amenazas: string[]; bloqueada: boolean; revisionTerminada: boolean };

export function useProteccionRasp(): EstadoRasp {
  const [amenazas, setAmenazas] = useState<string[]>([]);
  const [revisionTerminada, setRevisionTerminada] = useState(false);

  const detectar = (tipo: string) => () => {
    const bloquea = (AMENAZAS_QUE_BLOQUEAN as readonly string[]).includes(tipo);
    marcaSeguridad("RASP", { amenaza: tipo, reaccion: bloquea && !__DEV__ && !APK_PRUEBA_CA07 ? "bloquear" : "registrar" });
    setAmenazas((previas) => (previas.includes(tipo) ? previas : [...previas, tipo]));
  };

  const acciones: ThreatEventActions = {
    privilegedAccess: detectar("privilegedAccess"),
    hooks: detectar("hooks"),
    debug: detectar("debug"),
    appIntegrity: detectar("appIntegrity"),
    simulator: detectar("simulator"),
    unofficialStore: detectar("unofficialStore"),
    deviceBinding: detectar("deviceBinding"),
    passcode: detectar("passcode"),
    secureHardwareNotAvailable: detectar("secureHardwareNotAvailable"),
    obfuscationIssues: detectar("obfuscationIssues"),
    devMode: detectar("devMode"),
    adbEnabled: detectar("adbEnabled"),
    systemVPN: detectar("systemVPN"),
    screenshot: detectar("screenshot"),
    screenRecording: detectar("screenRecording"),
    multiInstance: detectar("multiInstance"),
    timeSpoofing: detectar("timeSpoofing"),
    locationSpoofing: detectar("locationSpoofing"),
    unsecureWifi: detectar("unsecureWifi"),
    automation: detectar("automation"),
    bootloader: detectar("bootloader"),
    malware: () => detectar("malware")(),
  };

  useFreeRasp(configuracion, acciones, {
    allChecksFinished: () => {
      marcaSeguridad("RASP", { revision: "terminada" });
      setRevisionTerminada(true);
    },
  });

  const bloqueada = !__DEV__ && !APK_PRUEBA_CA07 && amenazas.some((a) => (AMENAZAS_QUE_BLOQUEAN as readonly string[]).includes(a));
  return { amenazas, bloqueada, revisionTerminada };
}
