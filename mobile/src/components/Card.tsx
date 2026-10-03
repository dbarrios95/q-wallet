import React from "react";
import { View, StyleSheet, ViewStyle, ViewProps } from "react-native";
import { useTheme } from "../theme";

export interface CardProps extends ViewProps {
  children: React.ReactNode;
  style?: ViewStyle;
  variant?: "elevated" | "outlined" | "flat";
}

export const Card: React.FC<CardProps> = ({
  children,
  style,
  variant = "elevated",
  ...rest
}) => {
  const { colors, isDark } = useTheme();

  return (
    <View
      style={[
        styles.card,
        {
          backgroundColor: colors.card,
          borderColor: colors.cardBorder,
          borderWidth: variant === "outlined" || isDark ? 1 : 0.5,
        },
        variant === "elevated" && !isDark && styles.shadow,
        style,
      ]}
      {...rest}
    >
      {children}
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    borderRadius: 16,
    padding: 16,
  },
  shadow: {
    shadowColor: "#0B1F3A",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.06,
    shadowRadius: 12,
    elevation: 3,
  },
});
