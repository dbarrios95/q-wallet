import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
} from "react-native";
import { useRouter } from "expo-router";
import { z } from "zod";
import { Lock, Mail, ShieldAlert } from "lucide-react-native";
import { useTheme } from "../../src/theme";
import { Header, Input, Button, Card } from "../../src/components";

// Esquema Zod estricto para validación de inicio de sesión
const loginSchema = z
  .object({
    username: z
      .string()
      .min(3, "El usuario, teléfono o correo es requerido")
      .max(100, "Máximo 100 caracteres"),
    password: z
      .string()
      .min(8, "La contraseña debe tener al menos 8 caracteres"),
  })
  .strict();

export default function LoginScreen() {
  const router = useRouter();
  const { colors, palette, isDark } = useTheme();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState<{ username?: string; password?: string }>({});
  const [loading, setLoading] = useState(false);

  // TODO(CTRL-18): Integrar flujo OAuth2 Authorization Code con PKCE usando expo-auth-session
  // hacia el Hosted UI de Amazon Cognito con MFA TOTP obligatorio.
  const handleLogin = () => {
    setErrors({});
    const result = loginSchema.safeParse({ username, password });

    if (!result.success) {
      const fieldErrors: { username?: string; password?: string } = {};
      result.error.issues.forEach((issue) => {
        if (issue.path[0] === "username") fieldErrors.username = issue.message;
        if (issue.path[0] === "password") fieldErrors.password = issue.message;
      });
      setErrors(fieldErrors);
      return;
    }

    setLoading(true);
    // Simulación de navegación hacia pantalla principal sin backend
    setTimeout(() => {
      setLoading(false);
      router.replace("/(tabs)/home");
    }, 600);
  };

  const handleBypassToHome = () => {
    // Acceso directo simulado para desarrollo
    router.replace("/(tabs)/home");
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === "ios" ? "padding" : undefined}
      style={[styles.container, { backgroundColor: colors.background }]}
    >
      <Header title="Iniciar Sesión" showBack />

      <ScrollView
        contentContainerStyle={styles.scrollContent}
        keyboardShouldPersistTaps="handled"
      >
        <View style={styles.introSection}>
          <Text style={[styles.title, { color: colors.text }]}>
            Bienvenido de nuevo
          </Text>
          <Text style={[styles.subtitle, { color: colors.textMuted }]}>
            Ingresa tus credenciales para acceder a tu billetera Q-Wallet.
          </Text>
        </View>

        <Card style={styles.formCard}>
          <Input
            label="Correo o Teléfono"
            placeholder="ej. usuario@qwallet.gt o 55551234"
            value={username}
            onChangeText={setUsername}
            autoCapitalize="none"
            keyboardType="email-address"
            leftIcon={<Mail size={20} color={colors.textMuted} />}
            error={errors.username}
          />

          <Input
            label="Contraseña"
            placeholder="••••••••"
            value={password}
            onChangeText={setPassword}
            secureTextEntry
            leftIcon={<Lock size={20} color={colors.textMuted} />}
            error={errors.password}
          />

          <View style={{ height: 16 }} />

          <Button
            title="Iniciar sesión"
            onPress={handleLogin}
            variant="accent"
            size="lg"
            loading={loading}
          />
        </Card>

        {/* Banner de arquitectura e integración futura */}
        <View
          style={[
            styles.noticeBox,
            {
              backgroundColor: isDark ? colors.surfaceSubtle : palette.gray[100],
              borderColor: colors.cardBorder,
            },
          ]}
        >
          <ShieldAlert size={20} color={palette.info} style={styles.noticeIcon} />
          <View style={styles.noticeContent}>
            <Text style={[styles.noticeTitle, { color: colors.text }]}>
              Control CTRL-18 (Cognito PKCE)
            </Text>
            <Text style={[styles.noticeText, { color: colors.textMuted }]}>
              En producción este botón invoca el Cognito Hosted UI con PKCE y MFA TOTP. En esta fase de andamiaje, puedes continuar al panel principal.
            </Text>
          </View>
        </View>

        <View style={styles.bypassSection}>
          <Button
            title="Entrar con sesión simulada (Dev)"
            onPress={handleBypassToHome}
            variant="ghost"
            size="md"
          />
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
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
  bypassSection: {
    marginTop: 24,
    alignItems: "center",
  },
});
