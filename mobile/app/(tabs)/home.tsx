import React from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
} from "react-native";
import { useRouter } from "expo-router";
import {
  Send,
  ArrowDownLeft,
  PieChart,
  Zap,
  Bell,
  ChevronRight,
} from "lucide-react-native";
import { useTheme } from "../../src/theme";
import {
  BalanceCard,
  TransactionItem,
  Card,
} from "../../src/components";
import { mockAccount, mockTransactions, mockUser } from "../../src/mocks";

export default function HomeScreen() {
  const router = useRouter();
  const { colors, palette, isDark } = useTheme();

  const recentTransactions = mockTransactions.slice(0, 4);

  return (
    <View style={[styles.container, { backgroundColor: colors.background }]}>
      {/* Top Bar */}
      <View style={[styles.topBar, { backgroundColor: colors.surface }]}>
        <View style={styles.userInfo}>
          <View
            style={[
              styles.avatar,
              { backgroundColor: palette.primary },
            ]}
          >
            <Text style={styles.avatarText}>MM</Text>
          </View>
          <View>
            <Text style={[styles.greeting, { color: colors.textMuted }]}>
              Hola, bienvenida
            </Text>
            <Text style={[styles.userName, { color: colors.text }]}>
              {mockUser.name}
            </Text>
          </View>
        </View>

        <TouchableOpacity
          style={[
            styles.iconButton,
            {
              backgroundColor: isDark
                ? colors.surfaceSubtle
                : palette.gray[100],
            },
          ]}
          accessibilityLabel="Notificaciones"
        >
          <Bell size={20} color={colors.text} />
        </TouchableOpacity>
      </View>

      <ScrollView
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Balance Card */}
        <View style={styles.cardContainer}>
          <BalanceCard
            amountCents={mockAccount.balanceCents}
            accountNumber={mockAccount.accountNumber}
            onTransferPress={() => router.push("/(tabs)/transfer")}
            onReceivePress={() => router.push("/(tabs)/activity")}
          />
        </View>

        {/* Quick Actions */}
        <View style={styles.sectionHeader}>
          <Text style={[styles.sectionTitle, { color: colors.text }]}>
            Acciones Rápidas
          </Text>
        </View>

        <View style={styles.quickActionsGrid}>
          <TouchableOpacity
            style={[
              styles.actionItem,
              {
                backgroundColor: colors.card,
                borderColor: colors.cardBorder,
              },
            ]}
            onPress={() => router.push("/(tabs)/transfer")}
            activeOpacity={0.7}
          >
            <View
              style={[
                styles.actionIconCircle,
                { backgroundColor: "rgba(0, 168, 107, 0.15)" },
              ]}
            >
              <Send size={22} color={palette.accent} />
            </View>
            <Text style={[styles.actionLabel, { color: colors.text }]}>
              Transferir
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[
              styles.actionItem,
              {
                backgroundColor: colors.card,
                borderColor: colors.cardBorder,
              },
            ]}
            onPress={() => router.push("/(tabs)/budgets")}
            activeOpacity={0.7}
          >
            <View
              style={[
                styles.actionIconCircle,
                { backgroundColor: "rgba(59, 130, 246, 0.15)" },
              ]}
            >
              <PieChart size={22} color="#3B82F6" />
            </View>
            <Text style={[styles.actionLabel, { color: colors.text }]}>
              Presupuestos
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[
              styles.actionItem,
              {
                backgroundColor: colors.card,
                borderColor: colors.cardBorder,
              },
            ]}
            onPress={() => router.push("/(tabs)/activity")}
            activeOpacity={0.7}
          >
            <View
              style={[
                styles.actionIconCircle,
                { backgroundColor: "rgba(245, 158, 11, 0.15)" },
              ]}
            >
              <ArrowDownLeft size={22} color="#F59E0B" />
            </View>
            <Text style={[styles.actionLabel, { color: colors.text }]}>
              Movimientos
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[
              styles.actionItem,
              {
                backgroundColor: colors.card,
                borderColor: colors.cardBorder,
              },
            ]}
            onPress={() => router.push("/(tabs)/profile")}
            activeOpacity={0.7}
          >
            <View
              style={[
                styles.actionIconCircle,
                { backgroundColor: "rgba(139, 92, 246, 0.15)" },
              ]}
            >
              <Zap size={22} color="#8B5CF6" />
            </View>
            <Text style={[styles.actionLabel, { color: colors.text }]}>
              Servicios
            </Text>
          </TouchableOpacity>
        </View>

        {/* Recent Transactions */}
        <View style={styles.sectionHeader}>
          <Text style={[styles.sectionTitle, { color: colors.text }]}>
            Últimos Movimientos
          </Text>
          <TouchableOpacity
            onPress={() => router.push("/(tabs)/activity")}
            style={styles.seeAllButton}
          >
            <Text style={[styles.seeAllText, { color: palette.accent }]}>
              Ver todos
            </Text>
            <ChevronRight size={16} color={palette.accent} />
          </TouchableOpacity>
        </View>

        <View style={styles.transactionsList}>
          {recentTransactions.map((tx) => (
            <TransactionItem key={tx.id} transaction={tx} />
          ))}
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  topBar: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: 20,
    paddingTop: 48,
    paddingBottom: 16,
  },
  userInfo: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
  },
  avatar: {
    width: 44,
    height: 44,
    borderRadius: 22,
    alignItems: "center",
    justifyContent: "center",
  },
  avatarText: {
    color: "#FFFFFF",
    fontSize: 16,
    fontFamily: "Inter_700Bold",
  },
  greeting: {
    fontSize: 12,
    fontFamily: "Inter_400Regular",
  },
  userName: {
    fontSize: 16,
    fontFamily: "Inter_700Bold",
  },
  iconButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: "center",
    justifyContent: "center",
  },
  scrollContent: {
    paddingHorizontal: 20,
    paddingTop: 16,
    paddingBottom: 32,
  },
  cardContainer: {
    marginBottom: 24,
  },
  sectionHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 14,
    marginTop: 8,
  },
  sectionTitle: {
    fontSize: 17,
    fontFamily: "Inter_700Bold",
  },
  seeAllButton: {
    flexDirection: "row",
    alignItems: "center",
    gap: 2,
  },
  seeAllText: {
    fontSize: 13,
    fontFamily: "Inter_600SemiBold",
  },
  quickActionsGrid: {
    flexDirection: "row",
    gap: 12,
    marginBottom: 20,
  },
  actionItem: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: 14,
    borderRadius: 16,
    borderWidth: 1,
  },
  actionIconCircle: {
    width: 46,
    height: 46,
    borderRadius: 23,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 8,
  },
  actionLabel: {
    fontSize: 12,
    fontFamily: "Inter_600SemiBold",
  },
  transactionsList: {
    gap: 6,
  },
});
