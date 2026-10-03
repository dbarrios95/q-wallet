import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
} from "react-native";
import {
  PieChart,
  AlertTriangle,
  CheckCircle,
  Plus,
  TrendingDown,
  Info,
} from "lucide-react-native";
import { useTheme } from "../../src/theme";
import { Header, Card, ProgressBar, Button } from "../../src/components";
import { formatGTQ } from "../../src/components/BalanceCard";
import { mockBudgets } from "../../src/mocks";

export default function BudgetsScreen() {
  const { colors, palette, isDark } = useTheme();

  const [budgets] = useState(mockBudgets);

  const totalLimitCents = budgets.reduce((acc, b) => acc + b.limitCents, 0);
  const totalSpentCents = budgets.reduce((acc, b) => acc + b.spentCents, 0);
  const totalPercentage = Math.round((totalSpentCents / (totalLimitCents || 1)) * 100);

  // Categorías en riesgo (> 80% o > 100%)
  const alertedBudgets = budgets.filter(
    (b) => b.spentCents >= b.limitCents * 0.8
  );

  return (
    <View style={[styles.container, { backgroundColor: colors.background }]}>
      <Header
        title="Control de Gastos"
        rightAction={
          <TouchableOpacity
            style={[
              styles.addIconButton,
              { backgroundColor: "rgba(0, 168, 107, 0.15)" },
            ]}
          >
            <Plus size={20} color={palette.accent} />
          </TouchableOpacity>
        }
      />

      <ScrollView
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Global Summary Card */}
        <Card style={styles.summaryCard}>
          <View style={styles.summaryHeader}>
            <View>
              <Text style={[styles.summaryLabel, { color: colors.textMuted }]}>
                Presupuesto mensual (Octubre)
              </Text>
              <Text style={[styles.summarySpent, { color: colors.text }]}>
                {formatGTQ(totalSpentCents)}
              </Text>
            </View>
            <View
              style={[
                styles.percentageBadge,
                {
                  backgroundColor:
                    totalPercentage > 90
                      ? "rgba(239, 68, 68, 0.15)"
                      : "rgba(0, 168, 107, 0.15)",
                },
              ]}
            >
              <Text
                style={[
                  styles.percentageText,
                  {
                    color:
                      totalPercentage > 90 ? palette.error : palette.accent,
                  },
                ]}
              >
                {totalPercentage}% usado
              </Text>
            </View>
          </View>

          <ProgressBar
            currentCents={totalSpentCents}
            totalCents={totalLimitCents}
            label="Gasto global acumulado"
          />

          <View style={styles.summaryFooter}>
            <View style={styles.footerItem}>
              <Text style={[styles.footerLabel, { color: colors.textMuted }]}>
                Disponible para gastar
              </Text>
              <Text style={[styles.footerValue, { color: palette.accent }]}>
                {formatGTQ(Math.max(totalLimitCents - totalSpentCents, 0))}
              </Text>
            </View>
            <View style={styles.footerItem}>
              <Text style={[styles.footerLabel, { color: colors.textMuted }]}>
                Límite total
              </Text>
              <Text style={[styles.footerValue, { color: colors.text }]}>
                {formatGTQ(totalLimitCents)}
              </Text>
            </View>
          </View>
        </Card>

        {/* Alertas de Presupuesto */}
        {alertedBudgets.length > 0 && (
          <View style={styles.alertSection}>
            <Text style={[styles.sectionTitle, { color: colors.text }]}>
              Alertas Activas ({alertedBudgets.length})
            </Text>

            {alertedBudgets.map((b) => {
              const isOver = b.spentCents >= b.limitCents;
              return (
                <View
                  key={b.id}
                  style={[
                    styles.alertBanner,
                    {
                      backgroundColor: isOver
                        ? isDark
                          ? "#331010"
                          : "#FEF2F2"
                        : isDark
                        ? "#2D2007"
                        : "#FFFBEB",
                      borderColor: isOver ? palette.error : palette.warning,
                    },
                  ]}
                >
                  <AlertTriangle
                    size={20}
                    color={isOver ? palette.error : palette.warning}
                    style={styles.alertIcon}
                  />
                  <View style={styles.alertTextContainer}>
                    <Text
                      style={[
                        styles.alertTitle,
                        { color: isOver ? palette.error : palette.warning },
                      ]}
                    >
                      {isOver ? "¡Límite superado!" : "Cerca del límite (≥ 80%)"}
                    </Text>
                    <Text
                      style={[styles.alertDescription, { color: colors.text }]}
                    >
                      {b.name}: has usado {formatGTQ(b.spentCents)} de {formatGTQ(b.limitCents)}.
                    </Text>
                  </View>
                </View>
              );
            })}
          </View>
        )}

        {/* Categorías detalladas */}
        <Text style={[styles.sectionTitle, { color: colors.text }]}>
          Presupuesto por Categorías
        </Text>

        <View style={styles.categoriesList}>
          {budgets.map((b) => (
            <Card key={b.id} style={styles.categoryCard}>
              <ProgressBar
                categoryName={b.name}
                currentCents={b.spentCents}
                totalCents={b.limitCents}
              />
            </Card>
          ))}
        </View>

        <View style={{ height: 16 }} />

        {/* Informative Note */}
        <View style={styles.infoBox}>
          <Info size={18} color={palette.info} />
          <Text style={[styles.infoText, { color: colors.textMuted }]}>
            Los presupuestos se reinician automáticamente el 1.° de cada mes conforme la política F6 de Q-Wallet.
          </Text>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  addIconButton: {
    width: 36,
    height: 36,
    borderRadius: 18,
    alignItems: "center",
    justifyContent: "center",
  },
  scrollContent: {
    paddingHorizontal: 20,
    paddingTop: 12,
    paddingBottom: 32,
  },
  summaryCard: {
    marginBottom: 20,
    padding: 18,
  },
  summaryHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-start",
    marginBottom: 12,
  },
  summaryLabel: {
    fontSize: 13,
    fontFamily: "Inter_400Regular",
    marginBottom: 4,
  },
  summarySpent: {
    fontSize: 26,
    fontFamily: "Inter_700Bold",
  },
  percentageBadge: {
    paddingVertical: 4,
    paddingHorizontal: 10,
    borderRadius: 12,
  },
  percentageText: {
    fontSize: 12,
    fontFamily: "Inter_600SemiBold",
  },
  summaryFooter: {
    flexDirection: "row",
    justifyContent: "space-between",
    borderTopWidth: 1,
    borderTopColor: "rgba(148, 163, 184, 0.2)",
    paddingTop: 12,
    marginTop: 8,
  },
  footerItem: {},
  footerLabel: {
    fontSize: 11,
    fontFamily: "Inter_400Regular",
    marginBottom: 2,
  },
  footerValue: {
    fontSize: 14,
    fontFamily: "Inter_600SemiBold",
  },
  sectionTitle: {
    fontSize: 16,
    fontFamily: "Inter_700Bold",
    marginTop: 8,
    marginBottom: 12,
  },
  alertSection: {
    marginBottom: 16,
  },
  alertBanner: {
    flexDirection: "row",
    padding: 12,
    borderRadius: 12,
    borderWidth: 1,
    marginBottom: 8,
  },
  alertIcon: {
    marginRight: 10,
    marginTop: 2,
  },
  alertTextContainer: {
    flex: 1,
  },
  alertTitle: {
    fontSize: 13,
    fontFamily: "Inter_600SemiBold",
    marginBottom: 2,
  },
  alertDescription: {
    fontSize: 12,
    fontFamily: "Inter_400Regular",
    lineHeight: 17,
  },
  categoriesList: {
    gap: 12,
  },
  categoryCard: {
    padding: 14,
  },
  infoBox: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    paddingHorizontal: 6,
  },
  infoText: {
    fontSize: 12,
    fontFamily: "Inter_400Regular",
    flex: 1,
    lineHeight: 17,
  },
});
