import React from "react";
import { ActivityIndicator, View } from "react-native";

// Destino del retorno del login de Cognito (qwallet://auth/callback). El código lo procesa
// iniciarSesion() en la pantalla de login; esta ruta solo evita la pantalla de "ruta no encontrada".
export default function RetornoLogin() {
  return (
    <View style={{ flex: 1, alignItems: "center", justifyContent: "center" }}>
      <ActivityIndicator />
    </View>
  );
}
