// Punto de entrada de la Lambda svc-budgets.
import { verificadorCognito } from "../../comun/src/identidad";
import { clienteDynamo, crearManejador, tabla } from "../../comun/src/manejador";
import { rutas } from "./logica";
import { repositorioDynamo } from "./repositorio";

export const handler = crearManejador({
  servicio: "svc-budgets",
  verificador: verificadorCognito,
  rutas: rutas({
    repo: repositorioDynamo(clienteDynamo(), {
      presupuestos: tabla("TABLA_PRESUPUESTOS"),
      cuentas: tabla("TABLA_CUENTAS"),
      movimientos: tabla("TABLA_MOVIMIENTOS"),
    }),
  }),
});
