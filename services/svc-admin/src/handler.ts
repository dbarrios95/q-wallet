// Punto de entrada de la Lambda svc-admin.
import { CognitoIdentityProviderClient } from "@aws-sdk/client-cognito-identity-provider";
import { auditoriaDynamo } from "../../comun/src/auditoria";
import { verificadorCognito } from "../../comun/src/identidad";
import { clienteDynamo, crearManejador, tabla } from "../../comun/src/manejador";
import { rutas } from "./logica";
import { repositorioAws } from "./repositorio";

const c = clienteDynamo();

export const handler = crearManejador({
  servicio: "svc-admin",
  verificador: verificadorCognito,
  rutas: rutas({
    repo: repositorioAws(new CognitoIdentityProviderClient({}), tabla("USER_POOL_ID"), c, tabla("TABLA_AUDITORIA")),
    auditoria: auditoriaDynamo(c, tabla("TABLA_AUDITORIA")),
  }),
});
