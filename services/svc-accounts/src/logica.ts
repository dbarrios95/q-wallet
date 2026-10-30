// svc-accounts: GET /accounts y GET /accounts/{accountId}/transactions.
// CTRL-01 (BOLA/IDOR): la cuenta se busca con la llave (sub del token, accountId);
//   una cuenta ajena responde 404, igual que una que no existe.
// CTRL-05: paginación por cursor con tope de 50; el cursor no puede apuntar a otra cuenta.
// CTRL-03: DTO mínimo (sin userId ni llaves internas).
import { z } from "zod";
import { ErrorHttp } from "../../comun/src/http";
import type { Contexto, Resultado, Ruta } from "../../comun/src/manejador";
import { codificarCursor, cursor, decodificarCursor, limite } from "../../comun/src/paginacion";
import { leerConsulta, leerRuta, uuid } from "../../comun/src/validacion";
import type { Cuenta, Movimiento, RepositorioCuentas } from "./repositorio";

export const cuentaDto = (c: Cuenta) => ({ accountId: c.accountId, alias: c.alias, moneda: c.moneda, saldoCentavos: c.saldoCentavos });

export const movimientoDto = (m: Movimiento) => ({
  id: Buffer.from(m.fechaId, "utf8").toString("base64url"),
  fecha: m.fecha,
  tipo: m.tipo,
  montoCentavos: m.montoCentavos,
  categoria: m.categoria,
  descripcion: m.descripcion ?? null,
  contraparte: m.contraparte ?? null,
  transferId: m.transferId ?? null,
});

const rutaMovimientos = z.object({ accountId: uuid }).strict();
const consultaMovimientos = z.object({ limit: limite, cursor }).strict();

export function rutas(d: { repo: RepositorioCuentas }): Record<string, Ruta> {
  const listar = async ({ identidad }: Contexto): Promise<Resultado> => {
    const cuentas = await d.repo.listarCuentas(identidad.sub);
    return { status: 200, cuerpo: { cuentas: cuentas.map(cuentaDto) } };
  };

  const movimientos = async ({ event, identidad }: Contexto): Promise<Resultado> => {
    const { accountId } = leerRuta(event, rutaMovimientos);
    const q = leerConsulta(event, consultaMovimientos);
    const cuenta = await d.repo.obtenerCuenta(identidad.sub, accountId);
    if (!cuenta) throw new ErrorHttp(404, "no_encontrado");
    const desde = decodificarCursor(q.cursor, ["accountId", "fechaId"], { campo: "accountId", valor: accountId });
    const pagina = await d.repo.listarMovimientos(accountId, q.limit, desde);
    return { status: 200, cuerpo: { movimientos: pagina.items.map(movimientoDto), cursor: codificarCursor(pagina.siguiente) } };
  };

  return {
    "GET /accounts": listar,
    "GET /accounts/{accountId}/transactions": movimientos,
  };
}
