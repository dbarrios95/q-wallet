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
import { mockAccount, mockTransactions } from "../../src/mocks";
import { useUsuario } from "../../src/seguridad/sesion";

type RutaAccion = "/(tabs)/transfer" | "/(tabs)/budgets" | "/(tabs)/activity" | "/(tabs)/profile";

// color undefined = verde de la marca (palette.accent)
const accionesRapidas: {
  etiqueta: string;
  Icono: typeof Send;
  color?: string;
  fondo: string;
  ruta: RutaAccion;
}[] = [
  { etiqueta: "Transferir", Icono: Send, fondo: "rgba(0, 168, 107, 0.15)", ruta: "/(tabs)/transfer" },
  { etiqueta: "Presupuestos", Icono: PieChart, color: "#3B82F6", fondo: "rgba(59, 130, 246, 0.15)", ruta: "/(tabs)/budgets" },
  { etiqueta: "Movimientos", Icono: ArrowDownLeft, color: "#F59E0B", fondo: "rgba(245, 158, 11, 0.15)", ruta: "/(tabs)/activity" },
  { etiqueta: "Servicios", Icono: Zap, color: "#8B5CF6", fondo: "rgba(139, 92, 246, 0.15)", ruta: "/(tabs)/profile" },
];

export default function HomeScreen() {
  const router = useRouter();
  const { colors, palette, isDark } = useTheme();
  const usuario = useUsuario();
  const alias = (usuario?.correo ?? "").split("@")[0] || "Q-Wallet";

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
            <Text style={styles.avatarText}>{alias.slice(0, 2).toUpperCase()}</Text>
          </View>
          <View>
            <Text style={[styles.greeting, { color: colors.textMuted }]}>
              Hola, bienvenido(a)
            </Text>
            <Text style={[styles.userName, { color: colors.text }]}>
              {alias}
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

        {/* Acciones rápidas: una sola tarjeta con cuatro accesos */}
        <View style={styles.sectionHeader}>
          <Text style={[styles.sectionTitle, { color: colors.text }]}>
            Acciones rápidas
          </Text>
        </View>

        <View
          style={[
            styles.quickActionsCard,
            { backgroundColor: colors.card, borderColor: colors.cardBorder },
          ]}
        >
          {accionesRapidas.map(({ etiqueta, Icono, color, fondo, ruta }) => (
            <TouchableOpacity
              key={etiqueta}
              style={styles.actionItem}
              onPress={() => router.push(ruta)}
              activeOpacity={0.7}
              accessibilityRole="button"
              accessibilityLabel={etiqueta}
            >
              <View style={[styles.actionIconCircle, { backgroundColor: fondo }]}>
                <Icono size={22} color={color ?? palette.accent} />
              </View>
              <Text
                style={[styles.actionLabel, { color: colors.text }]}
                numberOfLines={1}
                adjustsFontSizeToFit
                minimumFontScale={0.75}
                maxFontSizeMultiplier={1.2}
              >
                {etiqueta}
              </Text>
            </TouchableOpacity>
          ))}
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
  quickActionsCard: {
    flexDirection: "row",
    justifyContent: "space-between",
    paddingVertical: 16,
    paddingHorizontal: 8,
    borderRadius: 16,
    borderWidth: 1,
    marginBottom: 20,
  },
  actionItem: {
    flex: 1,
    alignItems: "center",
    paddingHorizontal: 2,
  },
  actionIconCircle: {
    width: 48,
    height: 48,
    borderRadius: 24,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 8,
  },
  actionLabel: {
    fontSize: 12,
    fontFamily: "Inter_600SemiBold",
    textAlign: "center",
  },
  transactionsList: {
    gap: 6,
  },
});
