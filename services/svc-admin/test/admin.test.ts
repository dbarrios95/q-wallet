// svc-admin: CTRL-14 (BFLA), CTRL-23, CTRL-03 y CTRL-05.
import { describe, expect, it } from "vitest";
import { ADMIN, ANA, BETO, auditoriaMemoria, cuerpo, evento, verificadorFalso } from "../../comun/test/apoyo";
import { crearManejador } from "../../comun/src/manejador";
import { rutas } from "../src/logica";
import type { RepositorioAdmin } from "../src/repositorio";

const bloqueados: string[] = [];
const repo: RepositorioAdmin = {
  async listarUsuarios(limite) {
    return { usuarios: [{ id: ANA, correo: "ana@ejemplo.com", habilitado: true, estado: "CONFIRMED", creado: null }].slice(0, limite) };
  },
  async gruposDe(id) {
    return id === ADMIN ? ["admins"] : id === ANA || id === BETO ? [] : null;
  },
  async bloquear(id) {
    bloqueados.push(id);
  },
  async auditoria(dia) {
    return { items: [{ dia, tsId: "x", ts: `${dia}T00:00:00Z`, actor: ANA, accion: "pin.crear", recurso: "pin", resultado: "ok", correlationId: "c", detalle: { motivo: "x" } }] };
  },
};
const aud = auditoriaMemoria();
const h = crearManejador({ servicio: "svc-admin", verificador: () => verificadorFalso, salidaLog: () => {}, rutas: rutas({ repo, auditoria: aud }) });
const comoAdmin = { sub: ADMIN, grupos: ["admins"] };
const bloqueo = { motivo: "Reporte de robo del teléfono", verificacion: "llamada_registrada" };

describe("svc-admin", () => {
  it("CA-09: un cliente recibe 403 en cada ruta /admin y queda auditado", async () => {
    const intentos = [
      evento("GET", "/admin/users"),
      evento("POST", "/admin/users/{id}/block", { ruta: { id: BETO }, cuerpo: bloqueo }),
      evento("GET", "/admin/audit"),
    ];
    for (const e of intentos) expect((await h(e)).statusCode).toBe(403);
    expect(bloqueados).toEqual([]);
    expect(aud.eventos.filter((e) => e.accion === "admin.acceso_denegado")).toHaveLength(3);
  });

  it("un grupo parecido (admins-test) no sirve", async () => {
    expect((await h(evento("GET", "/admin/users", { grupos: ["admins-test", "Admins"] }))).statusCode).toBe(403);
  });

  it("admin lista usuarios con el correo enmascarado", async () => {
    const r = await h(evento("GET", "/admin/users", comoAdmin));
    expect(r.statusCode).toBe(200);
    expect(r.body).toContain("a***@ejemplo.com");
    expect(r.body).not.toContain("ana@ejemplo.com");
  });

  it("CTRL-23: bloquear exige motivo y canal de verificación", async () => {
    expect((await h(evento("POST", "/admin/users/{id}/block", { ...comoAdmin, ruta: { id: BETO }, cuerpo: { motivo: "porque sí" } }))).statusCode).toBe(400);
    const r = await h(evento("POST", "/admin/users/{id}/block", { ...comoAdmin, ruta: { id: BETO }, cuerpo: bloqueo }));
    expect(r.statusCode).toBe(200);
    expect(bloqueados).toEqual([BETO]);
    expect(aud.eventos.at(-1)).toMatchObject({ accion: "admin.bloquear_usuario", detalle: { verificacion: "llamada_registrada" } });
  });

  it("no se puede bloquear a otro admin ni a uno mismo; usuario inexistente da 404", async () => {
    const otroAdmin = { sub: ANA, grupos: ["admins"] };
    expect((await h(evento("POST", "/admin/users/{id}/block", { ...otroAdmin, ruta: { id: ADMIN }, cuerpo: bloqueo }))).statusCode).toBe(403);
    expect((await h(evento("POST", "/admin/users/{id}/block", { ...comoAdmin, ruta: { id: ADMIN }, cuerpo: bloqueo }))).statusCode).toBe(400);
    expect((await h(evento("POST", "/admin/users/{id}/block", { ...comoAdmin, ruta: { id: "55555555-5555-4555-8555-555555555555" }, cuerpo: bloqueo }))).statusCode).toBe(404);
  });

  it("auditoría: devuelve solo campos de resumen y valida el día", async () => {
    const r = await h(evento("GET", "/admin/audit", { ...comoAdmin, consulta: { dia: "2026-10-30" } }));
    expect(r.statusCode).toBe(200);
    expect(r.body).not.toContain("motivo");
    expect((await h(evento("GET", "/admin/audit", { ...comoAdmin, consulta: { dia: "2026-10-30' OR 1=1" } }))).statusCode).toBe(400);
    expect((await h(evento("GET", "/admin/audit", { ...comoAdmin, consulta: { limit: "500" } }))).statusCode).toBe(400);
  });
});
