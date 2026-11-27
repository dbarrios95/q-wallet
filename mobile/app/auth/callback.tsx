import React, { useEffect } from "react";
import { ActivityIndicator, View } from "react-native";
import { useRouter } from "expo-router";
import { useUsuario } from "../../src/seguridad/sesion";

// Destino del retorno del login de Cognito (qwallet://auth/callback). El código lo procesa
// iniciarSesion() en la pantalla de login; esta ruta solo evita la pantalla de "ruta no encontrada".
//
// Demo final (27-nov): en un teléfono real el enlace de regreso puede abrir esta pantalla
// después de que el login ya llevó a Inicio, y quedaba encima con la rueda de carga. Ahora:
// - si la sesión ya está abierta, se cierra esta pantalla (queda Inicio, o el login termina
//   de llevar a Inicio);
// - si en 20 s no hay sesión, también se cierra, para que se vea el mensaje de error del login.
const ESPERA_MAXIMA_MS = 20_000;

export default function RetornoLogin() {
  const router = useRouter();
  const usuario = useUsuario();

  useEffect(() => {
    const salir = () => {
      if (router.canGoBack()) router.back();
      else router.replace(usuario ? "/(tabs)/home" : "/");
    };
    if (usuario) {
      salir();
      return;
    }
    const t = setTimeout(salir, ESPERA_MAXIMA_MS);
    return () => clearTimeout(t);
  }, [usuario, router]);

  return (
    <View style={{ flex: 1, alignItems: "center", justifyContent: "center" }}>
      <ActivityIndicator />
    </View>
  );
}
