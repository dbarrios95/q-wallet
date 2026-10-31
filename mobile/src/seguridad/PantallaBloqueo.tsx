// Pantalla que se muestra cuando freeRASP detecta un dispositivo o una app
// comprometida (CTRL-15). No muestra datos del cliente ni deja operar.

import React from "react";
import { Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

const NOMBRES: Record<string, string> = {
  privilegedAccess: "Dispositivo con acceso root",
  hooks: "Herramienta de instrumentación (hooking)",
  debug: "Depurador conectado",
  appIntegrity: "La app fue modificada o re-firmada",
  simulator: "Emulador",
};

export function PantallaBloqueo({ amenazas }: { amenazas: string[] }) {
  const motivos = amenazas.filter((a) => a in NOMBRES);
  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: "#0B1F3A" }}>
      <View style={{ flex: 1, padding: 24, justifyContent: "center" }} testID="pantalla-bloqueo-rasp">
        <Text style={{ color: "#FFFFFF", fontSize: 26, fontWeight: "700", marginBottom: 12 }}>
          Q-Wallet se bloqueó por seguridad
        </Text>
        <Text style={{ color: "#CBD5E1", fontSize: 16, lineHeight: 24, marginBottom: 20 }}>
          Detectamos un riesgo en este dispositivo. Para proteger tu dinero, la app no
          mostrará información ni permitirá operar aquí.
        </Text>
        {motivos.map((m) => (
          <Text key={m} style={{ color: "#00D688", fontSize: 16, marginBottom: 6 }}>
            • {NOMBRES[m]}
          </Text>
        ))}
        <Text style={{ color: "#94A3B8", fontSize: 14, marginTop: 20 }}>
          Usá un teléfono sin modificaciones o comunicate con soporte.
        </Text>
      </View>
    </SafeAreaView>
  );
}
