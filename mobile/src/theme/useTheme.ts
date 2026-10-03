import { useColorScheme } from "react-native";
import { theme, palette } from "./colors";

export function useTheme() {
  const scheme = useColorScheme();
  const isDark = scheme === "dark";
  const colors = isDark ? theme.dark : theme.light;

  return {
    isDark,
    colors,
    palette,
    scheme,
  };
}
