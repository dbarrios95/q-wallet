import React from "react";
import {
  Text,
  ActivityIndicator,
  Pressable,
  StyleSheet,
  ViewStyle,
  TextStyle,
} from "react-native";
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
} from "react-native-reanimated";
import { useTheme } from "../theme";

const AnimatedPressable = Animated.createAnimatedComponent(Pressable);

export interface ButtonProps {
  title: string;
  onPress: () => void;
  variant?: "primary" | "secondary" | "accent" | "outline" | "ghost" | "danger";
  size?: "sm" | "md" | "lg";
  loading?: boolean;
  disabled?: boolean;
  icon?: React.ReactNode;
  iconPosition?: "left" | "right";
  fullWidth?: boolean;
  style?: ViewStyle;
}

export const Button: React.FC<ButtonProps> = ({
  title,
  onPress,
  variant = "primary",
  size = "md",
  loading = false,
  disabled = false,
  icon,
  iconPosition = "left",
  fullWidth = true,
  style,
}) => {
  const { colors, palette, isDark } = useTheme();
  const scale = useSharedValue(1);

  const handlePressIn = () => {
    if (!disabled && !loading) {
      scale.value = withSpring(0.97, { damping: 15, stiffness: 300 });
    }
  };

  const handlePressOut = () => {
    scale.value = withSpring(1, { damping: 15, stiffness: 300 });
  };

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  // Background colors per variant
  let bg: string = palette.primary;
  let textColor: string = palette.white;
  let borderColor: string = "transparent";

  if (variant === "accent") {
    bg = palette.accent;
    textColor = palette.white;
  } else if (variant === "secondary") {
    bg = isDark ? colors.surfaceSubtle : palette.gray[200];
    textColor = colors.text;
  } else if (variant === "outline") {
    bg = "transparent";
    borderColor = isDark ? palette.gray[700] : palette.gray[300];
    textColor = colors.text;
  } else if (variant === "ghost") {
    bg = "transparent";
    textColor = palette.accent;
  } else if (variant === "danger") {
    bg = palette.error;
    textColor = palette.white;
  }

  // Sizing
  let height = 48;
  let paddingHorizontal = 20;
  let fontSize = 16;

  if (size === "sm") {
    height = 38;
    paddingHorizontal = 14;
    fontSize = 14;
  } else if (size === "lg") {
    height = 56;
    paddingHorizontal = 24;
    fontSize = 17;
  }

  const containerStyle: ViewStyle = {
    height,
    paddingHorizontal,
    backgroundColor: bg,
    borderColor,
    borderWidth: variant === "outline" ? 1.5 : 0,
    borderRadius: 14,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    opacity: disabled ? 0.5 : 1,
    width: fullWidth ? "100%" : undefined,
    ...style,
  };

  const textStyle: TextStyle = {
    color: textColor,
    fontSize,
    fontFamily: "Inter_600SemiBold",
    letterSpacing: 0.2,
  };

  return (
    <AnimatedPressable
      onPress={onPress}
      onPressIn={handlePressIn}
      onPressOut={handlePressOut}
      disabled={disabled || loading}
      style={[containerStyle, animatedStyle]}
    >
      {loading ? (
        <ActivityIndicator
          size="small"
          color={textColor}
          style={{ marginRight: 8 }}
        />
      ) : (
        <>
          {icon && iconPosition === "left" ? (
            <Animated.View style={{ marginRight: 8 }}>{icon}</Animated.View>
          ) : null}
          <Text style={textStyle}>{title}</Text>
          {icon && iconPosition === "right" ? (
            <Animated.View style={{ marginLeft: 8 }}>{icon}</Animated.View>
          ) : null}
        </>
      )}
    </AnimatedPressable>
  );
};
