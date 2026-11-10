import React, { useEffect, useState } from "react";
import { Redirect } from "expo-router";
import { haySesionGuardada } from "../src/seguridad/sesion";

export default function Index() {
  // Con una sesión guardada se pide desbloqueo; si no, la bienvenida.
  const [destino, setDestino] = useState<"/(auth)/unlock" | "/(auth)/welcome" | null>(null);
  useEffect(() => {
    haySesionGuardada()
      .then((hay) => setDestino(hay ? "/(auth)/unlock" : "/(auth)/welcome"))
      .catch(() => setDestino("/(auth)/welcome"));
  }, []);
  return destino ? <Redirect href={destino} /> : null;
}
