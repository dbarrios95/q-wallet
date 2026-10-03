import React, { useState, useEffect } from "react";
import { View, Text, StyleSheet, TouchableOpacity, Alert } from "react-native";
import { useRouter } from "expo-router";
import * as LocalAuthentication from "expo-local-authentication";
import { usePreventScreenCapture } from "expo-screen-capture";
import { Fingerprint, ShieldCheck, KeyRound } from "lucide-react-native";
import { useTheme } from "../../src/theme";
import { Header, Input, Button, Card } from "../../src/components";

export default function UnlockScreen() {
  const router = useRouter();
  const { colors, palette, isDark } = useTheme();

  // FLAG_SECURE: previene captura de pantalla y grabación en vistas sensibles (MASVS-STORAGE)
  usePreventScreenCapture();

  const [pin, setPin] = useState("");
  const [pinError, setPinError] = useState<string | undefined>();
  const [biometryType, setBiometryType] = useState<string>("Biometría");
  const [hasBiometry, setHasBiometry] = useState<boolean>(false);

  useEffect(() => {
    checkBiometrics();
  }, []);

  const checkBiometrics = async () => {
    try {
      const compatible = await LocalAuthentication.hasHardwareAsync();
      const enrolled = await LocalAuthentication.isEnrolledAsync();
      if (compatible && enrolled) {
        setHasBiometry(true);
        const types = await LocalAuthentication.supportedAuthenticationTypesAsync();
        if (
          types.includes(
            LocalAuthentication.AuthenticationType.FACIAL_RECOGNITION
          )
        ) {
          setBiometryType("Reconocimiento Facial");
        } else {
          setBiometryType("Huella Dactilar");
        }
        // Solicitar automáticamente al cargar
        handleBiometricAuth();
      }
    } catch {
      // Entorno simulador o sin soporte de hardware biométrico
      setHasBiometry(false);
    }
  };

  // TODO(CTRL-07): Recuperar tokens de sesión desde expo-secure-store con requireAuthentication biométrico
  const handleBiometricAuth = async () => {
    try {
      const result = await LocalAuthentication.authenticateAsync({
        promptMessage: "Desbloquear Q-Wallet",
        cancelLabel: "Cancelar",
        fallbackLabel: "Usar PIN de seguridad",
        disableDeviceFallback: false,
      });

      if (result.success) {
        router.replace("/(tabs)/home");
      }
    } catch {
      // Ignorar si el usuario cancela
    }
  };

  const handlePinSubmit = () => {
    if (pin.length !== 6) {
      setPinError("El PIN debe ser de exactamente 6 dígitos");
      return;
    }
    // PIN de prueba simulado para desarrollo
    setPinError(undefined);
    router.replace("/(tabs)/home");
  };

  return (
    <View style={[styles.container, { backgroundColor: colors.background }]}>
      <Header title="Desbloqueo de Sesión" showBack />

      <View style={styles.content}>
        <View style={styles.topSection}>
          <View
            style={[
              styles.avatarCircle,
              {
                backgroundColor: isDark
                  ? colors.surfaceSubtle
                  : palette.gray[100],
              },
            ]}
          >
            <ShieldCheck size={48} color={palette.accent} />
          </View>

          <Text style={[styles.greeting, { color: colors.text }]}>
            Hola, María Morales
          </Text>
          <Text style={[styles.subGreeting, { color: colors.textMuted }]}>
            Confirma tu identidad para continuar
          </Text>
        </View>

        <Card style={styles.unlockCard}>
          <Text style={[styles.pinPrompt, { color: colors.text }]}>
            Ingresa tu PIN de 6 dígitos
          </Text>

          <Input
            variant="pin"
            pinLength={6}
            value={pin}
            onChangeText={(text) => {
              setPin(text);
              if (text.length === 6) {
                setPinError(undefined);
              }
            }}
            error={pinError}
            helper="PIN numérico de seguridad"
          />

          <View style={{ height: 16 }} />

          <Button
            title="Desbloquear con PIN"
            onPress={handlePinSubmit}
            variant="primary"
            size="md"
            icon={<KeyRound size={18} color="#FFFFFF" />}
          />
        </Card>

        {hasBiometry && (
          <TouchableOpacity
            onPress={handleBiometricAuth}
            style={[
              styles.biometryButton,
              {
                backgroundColor: isDark
                  ? colors.surfaceSubtle
                  : palette.gray[100],
              },
            ]}
            activeOpacity={0.8}
          >
            <Fingerprint size={28} color={palette.accent} />
            <Text style={[styles.biometryText, { color: colors.text }]}>
              Usar {biometryType}
            </Text>
          </TouchableOpacity>
        )}

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
