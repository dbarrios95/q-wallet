import React, { useEffect } from "react";
import { View, Text, StyleSheet, ViewStyle } from "react-native";
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withTiming,
} from "react-native-reanimated";
import { useTheme } from "../theme";
import { formatGTQ } from "./BalanceCard";

export interface ProgressBarProps {
  currentCents: number;
  totalCents: number;
  label?: string;
  categoryName?: string;
  style?: ViewStyle;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  currentCents,
  totalCents,
  label,
  categoryName,
  style,
}) => {
  const { colors, palette, isDark } = useTheme();

  const ratio = totalCents > 0 ? Math.min(currentCents / totalCents, 1.2) : 0;
  const percentage = Math.round((currentCents / (totalCents || 1)) * 100);

  const animatedWidth = useSharedValue(0);

  useEffect(() => {
    animatedWidth.value = withTiming(Math.min(ratio, 1) * 100, {
      duration: 600,
    });
  }, [ratio]);

  const animatedStyle = useAnimatedStyle(() => ({
    width: `${animatedWidth.value}%`,
  }));

  // Color according to percentage spent
  let barColor: string = palette.accent;
  if (percentage >= 100) {
    barColor = palette.error;
  } else if (percentage >= 80) {
    barColor = palette.warning;
  }

  return (
    <View style={[styles.container, style]}>
      <View style={styles.headerRow}>
        <Text style={[styles.label, { color: colors.text }]}>
          {categoryName || label || "Presupuesto"}
        </Text>
        <Text
          style={[
            styles.percentage,
            {
              color:
                percentage >= 100
                  ? palette.error
                  : percentage >= 80
                  ? palette.warning
                  : palette.accent,
            },
          ]}
        >
          {percentage}%
        </Text>
      </View>

      <View
        style={[
          styles.track,
          {
            backgroundColor: isDark ? colors.surfaceSubtle : palette.gray[200],
          },
        ]}
      >
        <Animated.View
          style={[styles.fill, { backgroundColor: barColor }, animatedStyle]}
        />
      </View>

      <View style={styles.footerRow}>
        <Text style={[styles.amountText, { color: colors.textMuted }]}>
          Gastado: {formatGTQ(currentCents)}
        </Text>
        <Text style={[styles.amountText, { color: colors.textSubtle }]}>
          Límite: {formatGTQ(totalCents)}
        </Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginVertical: 8,
    width: "100%",
  },
  headerRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 6,
  },
  label: {
    fontSize: 14,
    fontFamily: "Inter_600SemiBold",
  },
  percentage: {
    fontSize: 13,
    fontFamily: "Inter_600SemiBold",
  },
  track: {
    height: 10,
    borderRadius: 5,
    overflow: "hidden",
    width: "100%",
  },
  fill: {
    height: "100%",
    borderRadius: 5,
  },
  footerRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginTop: 6,
  },
  amountText: {
    fontSize: 12,
    fontFamily: "Inter_400Regular",
  },
});
