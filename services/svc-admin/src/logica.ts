// svc-admin: GET /admin/users, POST /admin/users/{id}/block, GET /admin/audit (F7).
// CTRL-14 (BFLA): además del authorizer, cada operación exige el grupo "admins" del token
//   verificado; un cliente recibe 403 y el intento queda auditado.
// CTRL-23: bloquear exige motivo y el canal por el que se verificó la identidad del cliente.
// CTRL-03: correos enmascarados; CTRL-05: listas paginadas con tope.
import { z } from "zod";
import type { Auditoria } from "../../comun/src/auditoria";
import { enmascararCorreo } from "../../comun/src/datos_personales";
import { ErrorHttp } from "../../comun/src/http";
import { exigirAdmin } from "../../comun/src/identidad";
import type { Contexto, Resultado, Ruta } from "../../comun/src/manejador";
import { codificarCursor, cursor, decodificarCursor, limite } from "../../comun/src/paginacion";
import { dia, leerConsulta, leerCuerpo, leerRuta, texto, uuid } from "../../comun/src/validacion";
import type { RepositorioAdmin } from "./repositorio";

const consultaUsuarios = z
  .object({ limit: limite, cursor: z.string().max(2048).regex(/^[A-Za-z0-9+/=_-]+$/).optional() })
  .strict();
const rutaUsuario = z.object({ id: uuid }).strict();
const bloqueo = z
  .object({ motivo: texto(10, 200), verificacion: z.enum(["llamada_registrada", "correo_registrado", "presencial"]) })
  .strict();
const consultaAuditoria = z.object({ dia: dia.optional(), limit: limite, cursor }).strict();

/** Campos de auditoría que se muestran (el detalle completo queda en la tabla). */
const auditoriaDto = (a: Record<string, unknown>) => ({
  ts: a.ts,
  actor: a.actor,
  accion: a.accion,
  recurso: a.recurso,
  resultado: a.resultado,
  correlationId: a.correlationId,
});

export function rutas(d: { repo: RepositorioAdmin; auditoria: Auditoria; ahora?: () => Date }): Record<string, Ruta> {
  const ahora = d.ahora ?? (() => new Date());

  /** Envuelve cada ruta: si no es admin, audita el intento y responde 403. */
  const soloAdmin = (ruta: Ruta): Ruta => async (ctx) => {
    try {
      exigirAdmin(ctx.identidad);
    } catch (e) {
      await d.auditoria.registrar({
        actor: ctx.identidad.sub,
        accion: "admin.acceso_denegado",
        recurso: `${ctx.event.httpMethod} ${ctx.event.resource}`,
        resultado: "rechazado",
        correlationId: ctx.correlationId,
      });
      throw e;
    }
    return ruta(ctx);
  };

  const usuarios: Ruta = async ({ event }) => {
    const q = leerConsulta(event, consultaUsuarios);
    const r = await d.repo.listarUsuarios(q.limit, q.cursor);
    return {
      status: 200,
      cuerpo: {
        usuarios: r.usuarios.map((u) => ({ ...u, correo: u.correo ? enmascararCorreo(u.correo) : null })),
        cursor: r.siguiente ?? null,
      },
    };
  };

  const bloquear: Ruta = async ({ event, identidad, correlationId }): Promise<Resultado> => {
    const { id } = leerRuta(event, rutaUsuario);
    const b = leerCuerpo(event, bloqueo);
    if (id === identidad.sub) throw new ErrorHttp(400, "solicitud_invalida", ["id"]);
    const grupos = await d.repo.gruposDe(id);
    if (grupos === null) throw new ErrorHttp(404, "no_encontrado");
    // Un admin no bloquea a otro admin desde la API (eso se hace con dos personas, fuera de la app).
    if (grupos.includes("admins")) throw new ErrorHttp(403, "prohibido");
    await d.repo.bloquear(id);
    await d.auditoria.registrar({
      actor: identidad.sub,
      accion: "admin.bloquear_usuario",
      recurso: `usuario/${id}`,
      resultado: "ok",
      correlationId,
      detalle: { motivo: b.motivo, verificacion: b.verificacion },
    });
    return { status: 200, cuerpo: { id, habilitado: false } };
  };

  const auditoria: Ruta = async ({ event }) => {
    const q = leerConsulta(event, consultaAuditoria);
    const elDia = q.dia ?? ahora().toISOString().slice(0, 10);
    const desde = decodificarCursor(q.cursor, ["dia", "tsId"], { campo: "dia", valor: elDia });
    const r = await d.repo.auditoria(elDia, q.limit, desde);
    return { status: 200, cuerpo: { dia: elDia, eventos: r.items.map(auditoriaDto), cursor: codificarCursor(r.siguiente) } };
  };

  return {
    "GET /admin/users": soloAdmin(usuarios),
    "POST /admin/users/{id}/block": soloAdmin(bloquear),
    "GET /admin/audit": soloAdmin(auditoria),
  };
}
