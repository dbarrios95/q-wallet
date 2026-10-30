// svc-budgets: GET /categories, GET/POST/PUT /budgets (F6, control de gastos).
// CTRL-01: la llave de cada presupuesto empieza con el sub del token (nunca viene del cliente).
// CTRL-04: zod estricto, categorías cerradas, montos enteros en centavos.
// Alertas: "cerca" al 80 % del límite y "superado" al 100 %.
import { z } from "zod";
import { ErrorHttp } from "../../comun/src/http";
import type { Contexto, Resultado, Ruta } from "../../comun/src/manejador";
import { centavos, leerConsulta, leerCuerpo, mes } from "../../comun/src/validacion";
import type { RepositorioPresupuestos } from "./repositorio";

export const CATEGORIAS = ["alimentacion", "transporte", "servicios", "entretenimiento", "salud", "educacion", "transferencias", "otros"] as const;

const presupuesto = z.object({ mes, categoria: z.enum(CATEGORIAS), limiteCentavos: centavos }).strict();
const consulta = z.object({ mes: mes.optional() }).strict();

export function alerta(gastado: number, limite: number): "superado" | "cerca" | null {
  if (gastado >= limite) return "superado";
  if (gastado * 100 >= limite * 80) return "cerca";
  return null;
}

export function rutas(d: { repo: RepositorioPresupuestos; ahora?: () => Date }): Record<string, Ruta> {
  const ahora = d.ahora ?? (() => new Date());

  const categorias = async (): Promise<Resultado> => ({ status: 200, cuerpo: { categorias: CATEGORIAS } });

  const listar = async ({ event, identidad }: Contexto): Promise<Resultado> => {
    const q = leerConsulta(event, consulta);
    const m = q.mes ?? ahora().toISOString().slice(0, 7);
    const [lista, gastos] = await Promise.all([d.repo.listar(identidad.sub, m), d.repo.gastosDelMes(identidad.sub, m)]);
    const porCategoria = new Map<string, number>();
    for (const g of gastos) porCategoria.set(g.categoria, (porCategoria.get(g.categoria) ?? 0) + g.montoCentavos);
    const presupuestos = lista.map((p) => {
      const categoria = p.mesCategoria.split("#")[1] ?? "";
      const gastado = porCategoria.get(categoria) ?? 0;
      return { categoria, limiteCentavos: p.limiteCentavos, gastadoCentavos: gastado, alerta: alerta(gastado, p.limiteCentavos) };
    });
    return { status: 200, cuerpo: { mes: m, presupuestos } };
  };

  const guardar = (nuevo: boolean) => async ({ event, identidad }: Contexto): Promise<Resultado> => {
    const p = leerCuerpo(event, presupuesto);
    const item = { userId: identidad.sub, mesCategoria: `${p.mes}#${p.categoria}`, limiteCentavos: p.limiteCentavos };
    const ok = nuevo ? await d.repo.crear(item) : await d.repo.actualizar(item);
    if (!ok) throw nuevo ? new ErrorHttp(409, "conflicto") : new ErrorHttp(404, "no_encontrado");
    return { status: nuevo ? 201 : 200, cuerpo: p };
  };

  return {
    "GET /categories": categorias,
    "GET /budgets": listar,
    "POST /budgets": guardar(true),
    "PUT /budgets": guardar(false),
  };
}
