import React, { useEffect } from "react";
import { ActivityIndicator, View } from "react-native";
import { useRouter } from "expo-router";

// Destino del regreso de /logout de Cognito (qwallet://auth/logout). Lo procesa
// cerrarSesion(); esta ruta solo evita la pantalla de "ruta no encontrada" y lleva a Bienvenida.
export default function RetornoLogout() {
  const router = useRouter();
  useEffect(() => {
    router.replace("/(auth)/welcome");
  }, [router]);
  return (
    <View style={{ flex: 1, alignItems: "center", justifyContent: "center" }}>
      <ActivityIndicator />
    </View>
  );
}
