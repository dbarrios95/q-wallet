import React, { useState } from "react";
import {
  View,
  Text,
  TextInput,
  TextInputProps,
  TouchableOpacity,
  StyleSheet,
  ViewStyle,
} from "react-native";
import { Eye, EyeOff } from "lucide-react-native";
import { useTheme } from "../theme";

export interface InputProps extends Omit<TextInputProps, "style"> {
  label?: string;
  error?: string;
  helper?: string;
  variant?: "default" | "pin";
  pinLength?: number;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  containerStyle?: ViewStyle;
}

export const Input: React.FC<InputProps> = ({
  label,
  error,
  helper,
  variant = "default",
  pinLength = 6,
  leftIcon,
  rightIcon,
  secureTextEntry,
  containerStyle,
  value = "",
  onChangeText,
  ...rest
}) => {
  const { colors, palette, isDark } = useTheme();
  const [isFocused, setIsFocused] = useState(false);
  const [isSecureVisible, setIsSecureVisible] = useState(false);

  const isActuallySecure = secureTextEntry && !isSecureVisible;

  if (variant === "pin") {
    const digits = (value || "").split("");

    return (
      <View style={[styles.container, containerStyle]}>
        {label && <Text style={[styles.label, { color: colors.text }]}>{label}</Text>}
        
        {/* Hidden text input capturing numbers */}
        <TextInput
          value={value}
          onChangeText={(text) => {
            const numeric = text.replace(/[^0-9]/g, "").slice(0, pinLength);
            onChangeText?.(numeric);
          }}
          keyboardType="number-pad"
          maxLength={pinLength}
          secureTextEntry={false}
          style={styles.hiddenInput}
          autoFocus={rest.autoFocus}
          testID="pin-input"
        />

        {/* Visual PIN boxes */}
        <View style={styles.pinContainer}>
          {Array.from({ length: pinLength }).map((_, index) => {
            const char = digits[index];
            const isCurrent = digits.length === index;

            return (
              <View
                key={index}
                style={[
                  styles.pinBox,
                  {
                    borderColor: error
                      ? palette.error
                      : isCurrent
                      ? palette.accent
                      : colors.border,
                    backgroundColor: isDark ? colors.surfaceSubtle : palette.gray[100],
                  },
                ]}
              >
                {char ? (
                  <View
                    style={[
                      styles.pinDot,
                      { backgroundColor: colors.text },
                    ]}
                  />
                ) : null}
              </View>
            );
          })}
        </View>

        {error && <Text style={[styles.error, { color: palette.error }]}>{error}</Text>}
        {helper && !error && (
          <Text style={[styles.helper, { color: colors.textMuted }]}>{helper}</Text>
        )}
      </View>
    );
  }

  return (
    <View style={[styles.container, containerStyle]}>
      {label && <Text style={[styles.label, { color: colors.text }]}>{label}</Text>}

      <View
        style={[
          styles.inputWrapper,
          {
            backgroundColor: isDark ? colors.surfaceSubtle : palette.gray[50],
            borderColor: error
              ? palette.error
              : isFocused
              ? palette.accent
              : colors.border,
          },
        ]}
      >
        {leftIcon && <View style={styles.leftIcon}>{leftIcon}</View>}

        <TextInput
          value={value}
          onChangeText={onChangeText}
          secureTextEntry={isActuallySecure}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholderTextColor={colors.textSubtle}
          style={[styles.input, { color: colors.text }]}
          {...rest}
        />

        {secureTextEntry ? (
          <TouchableOpacity
            onPress={() => setIsSecureVisible(!isSecureVisible)}
            style={styles.eyeButton}
            accessibilityLabel={isSecureVisible ? "Ocultar PIN" : "Mostrar PIN"}
          >
            {isSecureVisible ? (
              <EyeOff size={20} color={colors.textMuted} />
            ) : (
              <Eye size={20} color={colors.textMuted} />
            )}
          </TouchableOpacity>
        ) : rightIcon ? (
          <View style={styles.rightIcon}>{rightIcon}</View>
        ) : null}
      </View>

      {error && <Text style={[styles.error, { color: palette.error }]}>{error}</Text>}
      {helper && !error && (
        <Text style={[styles.helper, { color: colors.textMuted }]}>{helper}</Text>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginBottom: 16,
    width: "100%",
  },
  label: {
    fontSize: 14,
    fontFamily: "Inter_500Medium",
    marginBottom: 8,
  },
  inputWrapper: {
    flexDirection: "row",
    alignItems: "center",
    borderWidth: 1.5,
    borderRadius: 12,
    paddingHorizontal: 14,
    height: 52,
  },
  input: {
    flex: 1,
    fontSize: 16,
    fontFamily: "Inter_400Regular",
    height: "100%",
  },
  leftIcon: {
    marginRight: 10,
  },
  rightIcon: {
    marginLeft: 10,
  },
  eyeButton: {
    padding: 6,
    marginLeft: 4,
  },
  error: {
    fontSize: 12,
    fontFamily: "Inter_400Regular",
    marginTop: 6,
  },
  helper: {
    fontSize: 12,
    fontFamily: "Inter_400Regular",
    marginTop: 6,
  },
  pinContainer: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginVertical: 8,
  },
  pinBox: {
    width: 48,
    height: 56,
    borderRadius: 12,
    borderWidth: 2,
    alignItems: "center",
    justifyContent: "center",
  },
  pinDot: {
    width: 14,
    height: 14,
    borderRadius: 7,
  },
  hiddenInput: {
    position: "absolute",
    width: "100%",
    height: "100%",
    opacity: 0,
    zIndex: 10,
  },
});
