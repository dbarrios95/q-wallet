import React from "react";
import { View, Text, StyleSheet, ViewStyle } from "react-native";
import { Inbox } from "lucide-react-native";
import { useTheme } from "../theme";
import { Button } from "./Button";

export interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description: string;
  actionTitle?: string;
  onAction?: () => void;
  style?: ViewStyle;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  title,
  description,
  actionTitle,
  onAction,
  style,
}) => {
  const { colors, palette, isDark } = useTheme();

  return (
    <View style={[styles.container, style]}>
      <View
        style={[
          styles.iconCircle,
          {
            backgroundColor: isDark ? colors.surfaceSubtle : palette.gray[100],
          },
        ]}
      >
        {icon || <Inbox size={36} color={palette.accent} />}
      </View>

      <Text style={[styles.title, { color: colors.text }]}>{title}</Text>
      <Text style={[styles.description, { color: colors.textMuted }]}>
        {description}
      </Text>

      {actionTitle && onAction && (
        <View style={styles.actionContainer}>
          <Button
            title={actionTitle}
            onPress={onAction}
            variant="accent"
            size="sm"
            fullWidth={false}
          />
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: 32,
    paddingHorizontal: 24,
  },
  iconCircle: {
    width: 72,
    height: 72,
    borderRadius: 36,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 16,
  },
  title: {
    fontSize: 17,
    fontFamily: "Inter_600SemiBold",
    textAlign: "center",
    marginBottom: 6,
  },
  description: {
    fontSize: 13,
    fontFamily: "Inter_400Regular",
    textAlign: "center",
    lineHeight: 18,
    maxWidth: 280,
  },
  actionContainer: {
    marginTop: 18,
  },
});
