import React, { useState, useEffect, useCallback } from "react";
import { View, Text, StyleSheet } from "react-native";
import { useRouter } from "expo-router";
import { usePreventScreenCapture } from "expo-screen-capture";
import { Fingerprint, ShieldCheck } from "lucide-react-native";
import { useTheme } from "../../src/theme";
import { Header, Button, Card } from "../../src/components";
import { desbloquear, haySesionGuardada } from "../../src/seguridad/sesion";

// CTRL-07: la sesión guardada (refresh token cifrado con Android Keystore) solo se abre con la
// biometría del teléfono o con su PIN/patrón; después se renuevan los tokens en Cognito.
export default function UnlockScreen() {
  const router = useRouter();
  const { colors, palette, isDark } = useTheme();

  // FLAG_SECURE: previene captura de pantalla y grabación en vistas sensibles (MASVS-STORAGE)
  usePreventScreenCapture();

  const [mensaje, setMensaje] = useState<string | null>(null);
  const [cargando, setCargando] = useState(false);

  const intentar = useCallback(async () => {
    setMensaje(null);
    setCargando(true);
    try {
      if (!(await haySesionGuardada())) {
        router.replace("/(auth)/login");
        return;
      }
      if (await desbloquear()) {
        router.replace("/(tabs)/home");
      } else if (await haySesionGuardada()) {
        setMensaje("No se pudo confirmar tu identidad. Intenta de nuevo.");
      } else {
        setMensaje("Tu sesión venció. Inicia sesión de nuevo.");
      }
    } finally {
      setCargando(false);
    }
  }, [router]);

  useEffect(() => {
    void intentar();
  }, [intentar]);

  const fondo = isDark ? colors.surfaceSubtle : palette.gray[100];

  return (
    <View style={[styles.container, { backgroundColor: colors.background }]}>
      <Header title="Desbloqueo de Sesión" showBack />

      <View style={styles.content}>
        <View style={styles.topSection}>
          <View style={[styles.avatarCircle, { backgroundColor: fondo }]}>
            <ShieldCheck size={48} color={palette.accent} />
          </View>
          <Text style={[styles.greeting, { color: colors.text }]}>Hola de nuevo</Text>
          <Text style={[styles.subGreeting, { color: colors.textMuted }]}>
            Confirma tu identidad con la huella, el rostro o el bloqueo de tu teléfono
          </Text>
        </View>

        <Card style={styles.unlockCard}>
          <Button
            title="Desbloquear"
            onPress={intentar}
            variant="primary"
            size="lg"
            loading={cargando}
            icon={<Fingerprint size={20} color="#FFFFFF" />}
          />
          {mensaje ? <Text style={[styles.mensaje, { color: colors.textMuted }]}>{mensaje}</Text> : null}
          <View style={{ height: 12 }} />
          <Button title="Iniciar sesión con otra cuenta" onPress={() => router.replace("/(auth)/login")} variant="ghost" size="md" />
        </Card>

        <View style={styles.footerNote}>
          <Text style={[styles.footerText, { color: colors.textSubtle }]}>
            Protegido con FLAG_SECURE y Android Keystore
          </Text>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  content: {
    flex: 1,
    paddingHorizontal: 24,
    paddingBottom: 24,
    justifyContent: "space-between",
  },
  topSection: {
    alignItems: "center",
    marginTop: 16,
  },
  avatarCircle: {
    width: 88,
    height: 88,
    borderRadius: 44,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 16,
  },
  greeting: {
    fontSize: 22,
    fontFamily: "Inter_700Bold",
    marginBottom: 4,
  },
  subGreeting: {
    fontSize: 14,
    fontFamily: "Inter_400Regular",
  },
  unlockCard: {
    marginVertical: 20,
    alignItems: "center",
  },
  mensaje: {
    marginTop: 12,
    fontSize: 13,
    fontFamily: "Inter_500Medium",
    textAlign: "center",
  },
  pinPrompt: {
    fontSize: 15,
    fontFamily: "Inter_600SemiBold",
    marginBottom: 12,
  },
  biometryButton: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: 14,
    borderRadius: 14,
    gap: 12,
    marginTop: 8,
  },
  biometryText: {
    fontSize: 15,
    fontFamily: "Inter_600SemiBold",
  },
  footerNote: {
    alignItems: "center",
    marginTop: 16,
  },
  footerText: {
    fontSize: 11,
    fontFamily: "Inter_400Regular",
  },
});
