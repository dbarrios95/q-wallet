// Punto de entrada de la Lambda svc-transfers.
import { auditoriaDynamo } from "../../comun/src/auditoria";
import { verificadorCognito } from "../../comun/src/identidad";
import { clienteDynamo, crearManejador, tabla } from "../../comun/src/manejador";
import { rutas } from "./logica";
import { repositorioDynamo } from "./repositorio";

const c = clienteDynamo();

export const handler = crearManejador({
  servicio: "svc-transfers",
  verificador: verificadorCognito,
  rutas: rutas({
    repo: repositorioDynamo(c, {
      perfiles: tabla("TABLA_PERFILES"),
      pin: tabla("TABLA_PIN"),
      cuentas: tabla("TABLA_CUENTAS"),
      movimientos: tabla("TABLA_MOVIMIENTOS"),
      transferencias: tabla("TABLA_TRANSFERENCIAS"),
      beneficiarios: tabla("TABLA_BENEFICIARIOS"),
    }),
    auditoria: auditoriaDynamo(c, tabla("TABLA_AUDITORIA")),
  }),
});
