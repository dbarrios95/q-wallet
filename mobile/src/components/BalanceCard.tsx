import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ViewStyle,
} from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import { Eye, EyeOff, Send, ArrowDownLeft, ShieldCheck } from "lucide-react-native";

export interface BalanceCardProps {
  amountCents: number; // Stored in integer centavos (GTQ)
  accountNumber?: string;
  onTransferPress?: () => void;
  onReceivePress?: () => void;
  style?: ViewStyle;
}

export const formatGTQ = (cents: number): string => {
  const quetzales = cents / 100;
  return `Q ${quetzales.toLocaleString("es-GT", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
};

export const BalanceCard: React.FC<BalanceCardProps> = ({
  amountCents,
  accountNumber = "•••• 8921",
  onTransferPress,
  onReceivePress,
  style,
}) => {
  const [isVisible, setIsVisible] = useState(true);

  return (
    <LinearGradient
      colors={["#0B1F3A", "#16345C", "#0D4035"]}
      start={{ x: 0, y: 0 }}
      end={{ x: 1, y: 1 }}
      style={[styles.container, style]}
    >
      {/* Top row */}
      <View style={styles.topRow}>
        <View style={styles.badge}>
          <ShieldCheck size={14} color="#00D688" />
          <Text style={styles.badgeText}>Q-Wallet Protegida</Text>
        </View>

        <TouchableOpacity
          onPress={() => setIsVisible(!isVisible)}
          style={styles.eyeButton}
          accessibilityLabel={isVisible ? "Ocultar saldo" : "Mostrar saldo"}
        >
          {isVisible ? (
            <Eye size={18} color="#94A3B8" />
          ) : (
            <EyeOff size={18} color="#94A3B8" />
          )}
        </TouchableOpacity>
      </View>

      {/* Balance */}
      <View style={styles.balanceSection}>
        <Text style={styles.label}>Saldo disponible</Text>
        <Text style={styles.amount}>
          {isVisible ? formatGTQ(amountCents) : "Q ••••••••"}
        </Text>
        <Text style={styles.accountText}>Cuenta Monetaria {accountNumber}</Text>
      </View>

      {/* Quick Actions */}
      <View style={styles.actionsRow}>
        <TouchableOpacity
          onPress={onTransferPress}
          style={styles.actionButton}
          activeOpacity={0.8}
        >
          <View style={[styles.actionIconBg, { backgroundColor: "#00A86B" }]}>
            <Send size={18} color="#FFFFFF" />
          </View>
          <Text style={styles.actionText}>Transferir</Text>
        </TouchableOpacity>

        <TouchableOpacity
          onPress={onReceivePress}
          style={styles.actionButton}
          activeOpacity={0.8}
        >
          <View
            style={[
              styles.actionIconBg,
              { backgroundColor: "rgba(255, 255, 255, 0.15)" },
            ]}
          >
            <ArrowDownLeft size={18} color="#FFFFFF" />
          </View>
          <Text style={styles.actionText}>Recibir</Text>
        </TouchableOpacity>
      </View>
    </LinearGradient>
  );
};

const styles = StyleSheet.create({
  container: {
    borderRadius: 20,
    padding: 20,
    shadowColor: "#0B1F3A",
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.25,
    shadowRadius: 16,
    elevation: 8,
  },
  topRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  badge: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "rgba(0, 168, 107, 0.15)",
    paddingVertical: 4,
    paddingHorizontal: 10,
    borderRadius: 20,
    gap: 6,
  },
  badgeText: {
    color: "#00D688",
    fontSize: 12,
    fontFamily: "Inter_500Medium",
  },
  eyeButton: {
    padding: 4,
  },
  balanceSection: {
    marginVertical: 18,
  },
  label: {
    color: "#94A3B8",
    fontSize: 13,
    fontFamily: "Inter_400Regular",
    marginBottom: 6,
  },
  amount: {
    color: "#FFFFFF",
    fontSize: 32,
    fontFamily: "Inter_700Bold",
    letterSpacing: -0.5,
  },
  accountText: {
    color: "#64748B",
    fontSize: 12,
    fontFamily: "Inter_400Regular",
    marginTop: 4,
  },
  actionsRow: {
    flexDirection: "row",
    gap: 12,
    marginTop: 4,
  },
  actionButton: {
    flex: 1,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "rgba(255, 255, 255, 0.1)",
    paddingVertical: 10,
    paddingHorizontal: 14,
    borderRadius: 12,
    gap: 8,
  },
  actionIconBg: {
    width: 28,
    height: 28,
    borderRadius: 14,
    alignItems: "center",
    justifyContent: "center",
  },
  actionText: {
    color: "#FFFFFF",
    fontSize: 13,
    fontFamily: "Inter_600SemiBold",
  },
});
