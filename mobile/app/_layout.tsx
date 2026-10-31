import "../global.css";
import React, { useEffect } from "react";
import { Stack } from "expo-router";
import * as SplashScreen from "expo-splash-screen";
import { StatusBar } from "expo-status-bar";
import {
  useFonts,
  Inter_400Regular,
  Inter_500Medium,
  Inter_600SemiBold,
  Inter_700Bold,
} from "@expo-google-fonts/inter";
import { useColorScheme } from "react-native";
import { theme } from "../src/theme/colors";
import { useProteccionRasp } from "../src/seguridad/rasp";
import { sondaApi } from "../src/seguridad/red";
import { PantallaBloqueo } from "../src/seguridad/PantallaBloqueo";

// Prevent auto-hiding splash screen until fonts are loaded
SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  const scheme = useColorScheme();
  const isDark = scheme === "dark";
  const colors = isDark ? theme.dark : theme.light;

  // CTRL-15: freeRASP corre desde el arranque. CTRL-08: pinning + sonda a la API.
  const rasp = useProteccionRasp();
  useEffect(() => {
    void sondaApi();
  }, []);

  const [fontsLoaded, fontError] = useFonts({
    Inter_400Regular,
    Inter_500Medium,
    Inter_600SemiBold,
    Inter_700Bold,
  });

  useEffect(() => {
    if (fontsLoaded || fontError) {
      SplashScreen.hideAsync();
    }
  }, [fontsLoaded, fontError]);

  if (!fontsLoaded && !fontError) {
    return null;
  }

  if (rasp.bloqueada) {
    return (
      <>
        <StatusBar style="light" />
        <PantallaBloqueo amenazas={rasp.amenazas} />
      </>
    );
  }

  return (
    <>
      <StatusBar style={isDark ? "light" : "dark"} />
      <Stack
        screenOptions={{
          headerShown: false,
          contentStyle: { backgroundColor: colors.background },
          animation: "slide_from_right",
        }}
      >
        <Stack.Screen name="index" />
        <Stack.Screen name="(auth)" options={{ headerShown: false }} />
        <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
      </Stack>
    </>
  );
}
