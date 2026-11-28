// FLAG_SECURE (MASVS-STORAGE): sin capturas ni grabación en las vistas sensibles.
//
// usePreventScreenCapture() de expo-screen-capture lo pone al montar y lo quita al
// desmontar. Las pestañas no se desmontan al cambiar de una a otra, así que después de
// abrir Transferir o Perfil la marca quedaba en TODA la app (hallado al proyectar el
// teléfono para la demo, 27-nov). Este hook la pone solo mientras la pantalla está a la
// vista, cada pantalla con su propia clave.

import { useCallback } from "react";
import { useFocusEffect } from "expo-router";
import { allowScreenCaptureAsync, preventScreenCaptureAsync } from "expo-screen-capture";

// Demo final (28-nov-2026), decisión de Daniel: la presentación es en línea compartiendo la
// pantalla del teléfono, y con FLAG_SECURE Desbloqueo, Transferir y Perfil salían en negro.
// Se apaga aquí, en un solo lugar, para toda la app. Para volver a activarlo: true.
const PROTECCION_CAPTURAS_ACTIVA = false;

export function useSinCapturas(pantalla: string): void {
  useFocusEffect(
    useCallback(() => {
      if (!PROTECCION_CAPTURAS_ACTIVA) return undefined;
      void preventScreenCaptureAsync(pantalla);
      return () => {
        void allowScreenCaptureAsync(pantalla);
      };
    }, [pantalla]),
  );
}
