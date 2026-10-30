// svc-accounts: CTRL-01 (BOLA/IDOR) y CTRL-05 (paginación con tope).
import { describe, expect, it } from "vitest";
import { ANA, BETO, cuerpo, evento, verificadorFalso } from "../../comun/test/apoyo";
import { crearManejador } from "../../comun/src/manejador";
import { codificarCursor } from "../../comun/src/paginacion";
import { rutas } from "../src/logica";
import type { Cuenta, Movimiento, RepositorioCuentas } from "../src/repositorio";

const CUENTA_ANA = "aaaaaaaa-0000-4000-8000-000000000001";
const CUENTA_BETO = "bbbbbbbb-0000-4000-8000-000000000002";

const cuentas: Cuenta[] = [
  { userId: ANA, accountId: CUENTA_ANA, moneda: "GTQ", saldoCentavos: 100000, alias: "Principal" },
  { userId: BETO, accountId: CUENTA_BETO, moneda: "GTQ", saldoCentavos: 50000, alias: "Principal" },
];
const movs: Movimiento[] = Array.from({ length: 120 }, (_, i) => ({
  accountId: CUENTA_ANA,
  fechaId: `2026-10-${String((i % 28) + 1).padStart(2, "0")}#${i}`,
  fecha: "2026-10-01",
  tipo: "debito",
  montoCentavos: 100,
  categoria: "otros",
}));

let limitePedido = 0;
const repo: RepositorioCuentas = {
  async listarCuentas(u) {
    return cuentas.filter((c) => c.userId === u);
  },
  async obtenerCuenta(u, a) {
    return cuentas.find((c) => c.userId === u && c.accountId === a) ?? null;
  },
  async listarMovimientos(a, limite) {
    limitePedido = limite;
    const items = movs.filter((m) => m.accountId === a).slice(0, limite);
    const ultimo = items[items.length - 1];
    return { items, siguiente: ultimo ? { accountId: a, fechaId: ultimo.fechaId } : undefined };
  },
};

const h = crearManejador({ servicio: "svc-accounts", verificador: () => verificadorFalso, salidaLog: () => {}, rutas: rutas({ repo }) });
const mov = (o: Parameters<typeof evento>[2]) => evento("GET", "/accounts/{accountId}/transactions", o);

describe("svc-accounts", () => {
  it("GET /accounts lista solo las cuentas del sub, sin userId", async () => {
    const r = await h(evento("GET", "/accounts"));
    expect(cuerpo(r).cuentas).toEqual([{ accountId: CUENTA_ANA, alias: "Principal", moneda: "GTQ", saldoCentavos: 100000 }]);
    expect(r.body).not.toContain(ANA);
  });

  it("CA-01: pedir movimientos de una cuenta ajena responde 404 (no 200 ni 403)", async () => {
    const r = await h(mov({ ruta: { accountId: CUENTA_BETO } }));
    expect(r.statusCode).toBe(404);
  });

  it("accountId que no es UUID responde 400", async () => {
    expect((await h(mov({ ruta: { accountId: "../../perfiles" } }))).statusCode).toBe(400);
  });

  it("CA-05: limit por defecto 20 y máximo 50", async () => {
    const r = await h(mov({ ruta: { accountId: CUENTA_ANA } }));
    expect((cuerpo(r).movimientos as unknown[]).length).toBe(20);
    expect((await h(mov({ ruta: { accountId: CUENTA_ANA }, consulta: { limit: "51" } }))).statusCode).toBe(400);
    expect((await h(mov({ ruta: { accountId: CUENTA_ANA }, consulta: { limit: "50" } }))).statusCode).toBe(200);
    expect(limitePedido).toBe(50);
  });

  it("CA-05: un cursor armado con otra cuenta se rechaza", async () => {
    const c = codificarCursor({ accountId: CUENTA_BETO, fechaId: "2026-10-01#0" })!;
    expect((await h(mov({ ruta: { accountId: CUENTA_ANA }, consulta: { cursor: c } }))).statusCode).toBe(400);
  });

  it("parámetros de consulta no previstos se rechazan", async () => {
    expect((await h(mov({ ruta: { accountId: CUENTA_ANA }, consulta: { userId: BETO } }))).statusCode).toBe(400);
  });
});
