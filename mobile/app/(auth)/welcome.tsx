import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { useRouter } from "expo-router";
import { ShieldCheck, Wallet, ArrowRight, Fingerprint } from "lucide-react-native";
import { LinearGradient } from "expo-linear-gradient";
import Animated, { FadeInDown, FadeInUp } from "react-native-reanimated";
import { useTheme } from "../../src/theme";
import { Button } from "../../src/components";

export default function WelcomeScreen() {
  const router = useRouter();
  const { colors, palette, isDark } = useTheme();

  return (
    <View style={[styles.container, { backgroundColor: colors.background }]}>
      {/* Decorative gradient header */}
      <LinearGradient
        colors={["#0B1F3A", "#16345C", isDark ? "#070E1C" : "#F8FAFC"]}
        style={styles.headerGradient}
      >
        <Animated.View
          entering={FadeInUp.delay(100).duration(700)}
          style={styles.logoBadge}
        >
          <View style={styles.iconCircle}>
            <Wallet size={40} color="#00D688" />
          </View>
          <Text style={styles.brandTitle}>Q-Wallet</Text>
          <View style={styles.securityTag}>
            <ShieldCheck size={14} color="#00D688" />
            <Text style={styles.securityTagText}>Fintech Guatemala</Text>
          </View>
        </Animated.View>
      </LinearGradient>

      {/* Main content */}
      <View style={styles.content}>
        <Animated.View entering={FadeInDown.delay(200).duration(700)}>
          <Text style={[styles.heading, { color: colors.text }]}>
            Tu dinero en Quetzales, seguro y al instante.
          </Text>
          <Text style={[styles.subheading, { color: colors.textMuted }]}>
            Transfiere a cualquier teléfono, controla tus presupuestos mensuales y protege tus finanzas con estándares bancarios.
          </Text>
        </Animated.View>

        {/* Action buttons */}
        <Animated.View
          entering={FadeInDown.delay(350).duration(700)}
          style={styles.buttonGroup}
        >
          <Button
            title="Iniciar sesión"
            onPress={() => router.push("/(auth)/login")}
            variant="accent"
            size="lg"
            icon={<ArrowRight size={20} color="#FFFFFF" />}
            iconPosition="right"
          />

          <View style={{ height: 12 }} />

          <Button
            title="Desbloquear con Biometría"
            onPress={() => router.push("/(auth)/unlock")}
            variant="outline"
            size="lg"
            icon={<Fingerprint size={20} color={palette.accent} />}
          />
        </Animated.View>

        {/* Security badge at bottom */}
        <View style={styles.footer}>
          <Text style={[styles.footerText, { color: colors.textSubtle }]}>
            Cifrado de extremo a extremo · Cumplimiento JM-104-2021
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
  headerGradient: {
    height: "44%",
    alignItems: "center",
    justifyContent: "center",
    paddingTop: 40,
  },
  logoBadge: {
    alignItems: "center",
  },
  iconCircle: {
    width: 80,
    height: 80,
    borderRadius: 24,
    backgroundColor: "rgba(255, 255, 255, 0.1)",
    borderWidth: 1.5,
    borderColor: "rgba(0, 214, 136, 0.3)",
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 16,
  },
  brandTitle: {
    fontSize: 32,
    fontFamily: "Inter_700Bold",
    color: "#FFFFFF",
    letterSpacing: -0.5,
  },
  securityTag: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    backgroundColor: "rgba(0, 168, 107, 0.2)",
    paddingVertical: 4,
    paddingHorizontal: 12,
    borderRadius: 20,
    marginTop: 8,
  },
  securityTagText: {
    color: "#00D688",
    fontSize: 12,
    fontFamily: "Inter_500Medium",
  },
  content: {
    flex: 1,
    paddingHorizontal: 24,
    paddingTop: 32,
    paddingBottom: 24,
    justifyContent: "space-between",
  },
  heading: {
    fontSize: 26,
    fontFamily: "Inter_700Bold",
    lineHeight: 34,
    marginBottom: 12,
  },
  subheading: {
    fontSize: 15,
    fontFamily: "Inter_400Regular",
    lineHeight: 22,
  },
  buttonGroup: {
    width: "100%",
    marginTop: "auto",
    marginBottom: 16,
  },
  footer: {
    alignItems: "center",
  },
  footerText: {
    fontSize: 11,
    fontFamily: "Inter_400Regular",
  },
});
