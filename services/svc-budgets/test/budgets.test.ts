// svc-budgets: CTRL-01 (llave con el sub del token), CTRL-04 y alertas de F6.
import { describe, expect, it } from "vitest";
import { ANA, BETO, cuerpo, evento, verificadorFalso } from "../../comun/test/apoyo";
import { crearManejador } from "../../comun/src/manejador";
import { alerta, rutas } from "../src/logica";
import type { Presupuesto, RepositorioPresupuestos } from "../src/repositorio";

const guardados: Presupuesto[] = [];
const repo: RepositorioPresupuestos = {
  async listar(u, m) {
    return guardados.filter((p) => p.userId === u && p.mesCategoria.startsWith(`${m}#`));
  },
  async crear(p) {
    if (guardados.some((x) => x.userId === p.userId && x.mesCategoria === p.mesCategoria)) return false;
    guardados.push(p);
    return true;
  },
  async actualizar(p) {
    const x = guardados.find((g) => g.userId === p.userId && g.mesCategoria === p.mesCategoria);
    if (!x) return false;
    x.limiteCentavos = p.limiteCentavos;
    return true;
  },
  async gastosDelMes(u) {
    return u === ANA ? [{ categoria: "alimentacion", montoCentavos: 45_000 }, { categoria: "transporte", montoCentavos: 9_000 }] : [];
  },
};
const h = crearManejador({ servicio: "svc-budgets", verificador: () => verificadorFalso, salidaLog: () => {}, rutas: rutas({ repo, ahora: () => new Date("2026-10-30T12:00:00Z") }) });

describe("svc-budgets", () => {
  it("alertas: cerca al 80 % y superado al 100 %", () => {
    expect(alerta(79, 100)).toBeNull();
    expect(alerta(80, 100)).toBe("cerca");
    expect(alerta(100, 100)).toBe("superado");
  });

  it("crea, lista con gasto del mes y alerta", async () => {
    expect((await h(evento("POST", "/budgets", { cuerpo: { mes: "2026-10", categoria: "alimentacion", limiteCentavos: 40_000 } }))).statusCode).toBe(201);
    expect((await h(evento("POST", "/budgets", { cuerpo: { mes: "2026-10", categoria: "transporte", limiteCentavos: 10_000 } }))).statusCode).toBe(201);
    const r = cuerpo(await h(evento("GET", "/budgets")));
    expect(r.mes).toBe("2026-10");
    expect(r.presupuestos).toEqual([
      { categoria: "alimentacion", limiteCentavos: 40_000, gastadoCentavos: 45_000, alerta: "superado" },
      { categoria: "transporte", limiteCentavos: 10_000, gastadoCentavos: 9_000, alerta: "cerca" },
    ]);
  });

  it("CA-01: otro usuario no ve ni modifica los presupuestos ajenos", async () => {
    expect((cuerpo(await h(evento("GET", "/budgets", { sub: BETO, consulta: { mes: "2026-10" } }))).presupuestos as unknown[]).length).toBe(0);
    const r = await h(evento("PUT", "/budgets", { sub: BETO, cuerpo: { mes: "2026-10", categoria: "alimentacion", limiteCentavos: 1 } }));
    expect(r.statusCode).toBe(404);
    expect(guardados.find((g) => g.userId === ANA && g.mesCategoria === "2026-10#alimentacion")!.limiteCentavos).toBe(40_000);
  });

  it("CTRL-04: rechaza userId en el cuerpo, categorías inventadas y meses mal formados", async () => {
    const malos = [
      { mes: "2026-10", categoria: "alimentacion", limiteCentavos: 1, userId: BETO },
      { mes: "2026-10", categoria: "casino", limiteCentavos: 1 },
      { mes: "2026-13", categoria: "otros", limiteCentavos: 1 },
      { mes: "2026-10", categoria: "otros", limiteCentavos: 1.5 },
    ];
    for (const m of malos) expect((await h(evento("POST", "/budgets", { cuerpo: m }))).statusCode).toBe(400);
  });

  it("GET /categories devuelve la lista cerrada", async () => {
    expect((cuerpo(await h(evento("GET", "/categories"))).categorias as string[]).length).toBe(8);
  });
});
