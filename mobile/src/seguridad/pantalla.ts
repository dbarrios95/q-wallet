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

export function useSinCapturas(pantalla: string): void {
  useFocusEffect(
    useCallback(() => {
      void preventScreenCaptureAsync(pantalla);
      return () => {
        void allowScreenCaptureAsync(pantalla);
      };
    }, [pantalla]),
  );
}
