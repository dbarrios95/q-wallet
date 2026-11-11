import React, { useState } from "react";
import { View, Text, StyleSheet, ScrollView } from "react-native";
import { useRouter } from "expo-router";
import { KeyRound, ShieldCheck, Smartphone } from "lucide-react-native";
import { useTheme } from "../../src/theme";
import { Header, Button, Card } from "../../src/components";
import { iniciarSesion, loginConfigurado, tokenAcceso } from "../../src/seguridad/sesion";
import { llamarApi } from "../../src/seguridad/red";
import { marcaSeguridad } from "../../src/seguridad/registro";

// CTRL-18: la contraseña y el código TOTP se escriben en la página de inicio de sesión de
// Q-Wallet (login administrado de Amazon Cognito, con PKCE), nunca en esta pantalla.
export default function LoginScreen() {
  const router = useRouter();
  const { colors, palette, isDark } = useTheme();
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const entrar = async () => {
    setError(null);
    setCargando(true);
    try {
      if (!(await iniciarSesion())) {
        setError("No se completó el inicio de sesión. Intenta de nuevo.");
        return;
      }
      // Primera llamada con el token: el authorizer de API Gateway y la Lambda lo validan (CTRL-18).
      const r = await llamarApi("/me", { token: await tokenAcceso() });
      marcaSeguridad("AUTH", { api: "GET_/me", estado: r.estado });
      router.replace("/(tabs)/home");
    } catch (e) {
      marcaSeguridad("AUTH", { login: "error", motivo: e instanceof Error ? e.message : "desconocido" });
      setError("No se pudo iniciar sesión. Revisa tu conexión e intenta de nuevo.");
    } finally {
      setCargando(false);
    }
  };

  const fondoAviso = isDark ? colors.surfaceSubtle : palette.gray[100];

  return (
    <View style={[styles.container, { backgroundColor: colors.background }]}>
      <Header title="Iniciar Sesión" showBack />

      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.introSection}>
          <Text style={[styles.title, { color: colors.text }]}>Bienvenido de nuevo</Text>
          <Text style={[styles.subtitle, { color: colors.textMuted }]}>
            Vas a ingresar tu correo, tu contraseña y el código de tu app autenticadora en la página
            segura de inicio de sesión de Q-Wallet.
          </Text>
        </View>

        <Card style={styles.formCard}>
          <View style={styles.paso}>
            <KeyRound size={20} color={palette.accent} />
            <Text style={[styles.pasoTexto, { color: colors.text }]}>Correo y contraseña</Text>
          </View>
          <View style={styles.paso}>
            <Smartphone size={20} color={palette.accent} />
            <Text style={[styles.pasoTexto, { color: colors.text }]}>
              Código de 6 dígitos de tu app autenticadora (MFA)
            </Text>
          </View>

          <View style={{ height: 16 }} />

          <Button
            title="Continuar a la página segura"
            onPress={entrar}
            variant="accent"
            size="lg"
            loading={cargando}
            disabled={!loginConfigurado()}
          />
          {error ? <Text style={[styles.error, { color: palette.error }]}>{error}</Text> : null}
        </Card>

        <View style={[styles.noticeBox, { backgroundColor: fondoAviso, borderColor: colors.cardBorder }]}>
          <ShieldCheck size={20} color={palette.info} style={styles.noticeIcon} />
          <View style={styles.noticeContent}>
            <Text style={[styles.noticeTitle, { color: colors.text }]}>Tu contraseña no pasa por la app</Text>
            <Text style={[styles.noticeText, { color: colors.textMuted }]}>
              La página se abre en el navegador del teléfono con conexión cifrada. Q-Wallet recibe solo
              un permiso temporal (OAuth 2.0 con PKCE) y lo guarda cifrado con el almacén de llaves de Android.
            </Text>
          </View>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollContent: {
    paddingHorizontal: 20,
    paddingBottom: 32,
  },
  introSection: {
    marginVertical: 18,
  },
  title: {
    fontSize: 26,
    fontFamily: "Inter_700Bold",
    marginBottom: 6,
  },
  subtitle: {
    fontSize: 14,
    fontFamily: "Inter_400Regular",
    lineHeight: 20,
  },
  formCard: {
    marginBottom: 20,
  },
  noticeBox: {
    flexDirection: "row",
    padding: 14,
    borderRadius: 12,
    borderWidth: 1,
    marginTop: 8,
  },
  noticeIcon: {
    marginRight: 10,
    marginTop: 2,
  },
  noticeContent: {
    flex: 1,
  },
  noticeTitle: {
    fontSize: 13,
    fontFamily: "Inter_600SemiBold",
    marginBottom: 4,
  },
  noticeText: {
    fontSize: 12,
    fontFamily: "Inter_400Regular",
    lineHeight: 18,
  },
  paso: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    marginBottom: 10,
  },
  pasoTexto: {
    fontSize: 14,
    fontFamily: "Inter_500Medium",
    flex: 1,
  },
  error: {
    marginTop: 12,
    fontSize: 13,
    fontFamily: "Inter_500Medium",
  },
});
