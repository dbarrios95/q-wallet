import { Redirect } from "expo-router";

export default function Index() {
  // Redirigir a pantalla de bienvenida inicial
  return <Redirect href="/(auth)/welcome" />;
}
