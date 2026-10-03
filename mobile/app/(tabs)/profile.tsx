import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Switch,
  Alert,
} from "react-native";
import { useRouter } from "expo-router";
import { usePreventScreenCapture } from "expo-screen-capture";
import {
  User,
  Shield,
  Smartphone,
  CreditCard,
  Lock,
  Fingerprint,
  Bell,
  LogOut,
  ChevronRight,
  Info,
  ShieldCheck,
} from "lucide-react-native";
import { useTheme } from "../../src/theme";
import { Header, Card, Button } from "../../src/components";
import { mockUser, mockAccount } from "../../src/mocks";

export default function ProfileScreen() {
  const router = useRouter();
  const { colors, palette, isDark } = useTheme();

  // FLAG_SECURE: protege información sensible (PII, DPI, datos bancarios) contra capturas y grabación (MASVS-STORAGE)
  usePreventScreenCapture();

  const [biometricsEnabled, setBiometricsEnabled] = useState(true);
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);

  const handleLogout = () => {
    // Redirigir a bienvenida y limpiar sesión
    router.replace("/(auth)/welcome");
  };

  return (
    <View style={[styles.container, { backgroundColor: colors.background }]}>
      <Header title="Mi Perfil" />

      <ScrollView
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* User Card */}
        <Card style={styles.userCard}>
          <View style={styles.userHeader}>
            <View
              style={[
                styles.avatarLarge,
                { backgroundColor: palette.primary },
              ]}
            >
              <Text style={styles.avatarLargeText}>MM</Text>
            </View>
            <View style={styles.userDetails}>
              <Text style={[styles.userName, { color: colors.text }]}>
                {mockUser.name}
              </Text>
              <Text style={[styles.userEmail, { color: colors.textMuted }]}>
                {mockUser.email}
              </Text>
              <View style={styles.verifiedTag}>
                <ShieldCheck size={12} color="#00D688" />
                <Text style={styles.verifiedText}>Usuario Verificado (KYC)</Text>
              </View>
            </View>
          </View>
        </Card>

        {/* Datos Personales Enmascarados (CTRL-03) */}
        <Text style={[styles.sectionTitle, { color: colors.text }]}>
          Datos Personales Protegidos (CTRL-03)
        </Text>

        <Card style={styles.infoCard}>
          <View style={styles.infoRow}>
            <View style={styles.infoIconWrapper}>
              <Smartphone size={18} color={palette.accent} />
            </View>
            <View style={styles.infoContent}>
              <Text style={[styles.infoLabel, { color: colors.textMuted }]}>
                Teléfono móvil
              </Text>
              <Text style={[styles.infoValue, { color: colors.text }]}>
                +502 {mockUser.maskedPhone}
              </Text>
            </View>
          </View>

          <View style={styles.divider} />

          <View style={styles.infoRow}>
            <View style={styles.infoIconWrapper}>
              <CreditCard size={18} color={palette.accent} />
            </View>
            <View style={styles.infoContent}>
              <Text style={[styles.infoLabel, { color: colors.textMuted }]}>
                DPI (Documento de Identificación)
              </Text>
              <Text style={[styles.infoValue, { color: colors.text }]}>
                {mockUser.maskedDpi}
              </Text>
            </View>
          </View>

          <View style={styles.divider} />

          <View style={styles.infoRow}>
            <View style={styles.infoIconWrapper}>
              <Lock size={18} color={palette.accent} />
            </View>
            <View style={styles.infoContent}>
              <Text style={[styles.infoLabel, { color: colors.textMuted }]}>
                Cuenta Monetaria Asociada
              </Text>
              <Text style={[styles.infoValue, { color: colors.text }]}>
                Cuenta {mockAccount.accountNumber}
              </Text>
            </View>
          </View>
        </Card>

        {/* Seguridad y Privacidad */}
        <Text style={[styles.sectionTitle, { color: colors.text }]}>
          Seguridad y Acceso
        </Text>

        <Card style={styles.settingsCard}>
          <View style={styles.settingRow}>
            <View style={styles.settingLeft}>
              <Fingerprint size={20} color={colors.text} />
              <View style={styles.settingTextGroup}>
                <Text style={[styles.settingTitle, { color: colors.text }]}>
                  Biometría para ingresar
                </Text>
                <Text
                  style={[styles.settingSubtitle, { color: colors.textMuted }]}
                >
                  Huella dactilar o reconocimiento facial
                </Text>
              </View>
            </View>
            <Switch
              value={biometricsEnabled}
              onValueChange={setBiometricsEnabled}
              trackColor={{ false: palette.gray[300], true: palette.accent }}
            />
          </View>

          <View style={styles.divider} />

          <View style={styles.settingRow}>
            <View style={styles.settingLeft}>
              <Bell size={20} color={colors.text} />
              <View style={styles.settingTextGroup}>
                <Text style={[styles.settingTitle, { color: colors.text }]}>
                  Alertas de transferencias
                </Text>
                <Text
                  style={[styles.settingSubtitle, { color: colors.textMuted }]}
                >
                  Notificar débitos y movimientos
                </Text>
              </View>
            </View>
            <Switch
              value={notificationsEnabled}
              onValueChange={setNotificationsEnabled}
              trackColor={{ false: palette.gray[300], true: palette.accent }}
            />
          </View>

          <View style={styles.divider} />

          <TouchableOpacity
            style={styles.settingRowClickable}
            onPress={() => router.push("/(auth)/unlock")}
          >
            <View style={styles.settingLeft}>
              <Lock size={20} color={colors.text} />
              <View style={styles.settingTextGroup}>
                <Text style={[styles.settingTitle, { color: colors.text }]}>
                  Cambiar PIN de Transacción
                </Text>
                <Text
                  style={[styles.settingSubtitle, { color: colors.textMuted }]}
                >
                  6 dígitos protegidos con hash scrypt (CTRL-02)
                </Text>
              </View>
            </View>
            <ChevronRight size={18} color={colors.textMuted} />
          </TouchableOpacity>
        </Card>

        {/* Security Info Tag */}
        <View style={styles.complianceBox}>
          <Shield size={16} color={palette.accent} />
          <Text style={[styles.complianceText, { color: colors.textSubtle }]}>
            FLAG_SECURE activo. Q-Wallet protege tus datos contra ingeniería inversa, captura de pantalla y fugas en memoria.
          </Text>
        </View>

        {/* Cerrar Sesión */}
        <View style={styles.logoutContainer}>
          <Button
            title="Cerrar sesión segura"
            onPress={handleLogout}
            variant="danger"
            size="lg"
            icon={<LogOut size={20} color="#FFFFFF" />}
          />
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
    paddingTop: 8,
    paddingBottom: 36,
  },
  userCard: {
    marginBottom: 20,
    padding: 18,
  },
  userHeader: {
    flexDirection: "row",
    alignItems: "center",
    gap: 16,
  },
  avatarLarge: {
    width: 60,
    height: 60,
    borderRadius: 30,
    alignItems: "center",
    justifyContent: "center",
  },
  avatarLargeText: {
    color: "#FFFFFF",
    fontSize: 22,
    fontFamily: "Inter_700Bold",
  },
  userDetails: {
    flex: 1,
  },
  userName: {
    fontSize: 18,
    fontFamily: "Inter_700Bold",
  },
  userEmail: {
    fontSize: 13,
    fontFamily: "Inter_400Regular",
    marginTop: 2,
    marginBottom: 6,
  },
  verifiedTag: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
    backgroundColor: "rgba(0, 168, 107, 0.15)",
    paddingVertical: 2,
    paddingHorizontal: 8,
    borderRadius: 12,
    alignSelf: "flex-start",
  },
  verifiedText: {
    color: "#00A86B",
    fontSize: 11,
    fontFamily: "Inter_600SemiBold",
  },
  sectionTitle: {
    fontSize: 15,
    fontFamily: "Inter_700Bold",
    marginTop: 6,
    marginBottom: 10,
  },
  infoCard: {
    marginBottom: 20,
    padding: 16,
    gap: 8,
  },
  infoRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    paddingVertical: 4,
  },
  infoIconWrapper: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: "rgba(0, 168, 107, 0.1)",
    alignItems: "center",
    justifyContent: "center",
  },
  infoContent: {
    flex: 1,
  },
  infoLabel: {
    fontSize: 12,
    fontFamily: "Inter_400Regular",
  },
  infoValue: {
    fontSize: 14,
    fontFamily: "Inter_600SemiBold",
    marginTop: 2,
  },
  divider: {
    height: 1,
    backgroundColor: "rgba(148, 163, 184, 0.15)",
    marginVertical: 4,
  },
  settingsCard: {
    marginBottom: 20,
    padding: 16,
    gap: 8,
  },
  settingRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingVertical: 6,
  },
  settingRowClickable: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingVertical: 6,
  },
  settingLeft: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    flex: 1,
  },
  settingTextGroup: {
    flex: 1,
  },
  settingTitle: {
    fontSize: 14,
    fontFamily: "Inter_600SemiBold",
  },
  settingSubtitle: {
    fontSize: 12,
    fontFamily: "Inter_400Regular",
    marginTop: 2,
  },
  complianceBox: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    paddingHorizontal: 8,
    marginBottom: 24,
  },
  complianceText: {
    fontSize: 11,
    fontFamily: "Inter_400Regular",
    flex: 1,
    lineHeight: 16,
  },
  logoutContainer: {
    marginTop: 4,
  },
});
