// svc-profile: CTRL-01, CTRL-02, CTRL-03, CTRL-04 y auditoría.
import { beforeEach, describe, expect, it } from "vitest";
import { ANA, BETO, auditoriaMemoria, cuerpo, evento, verificadorFalso } from "../../comun/test/apoyo";
import { crearManejador } from "../../comun/src/manejador";
import { rutas } from "../src/logica";
import type { Perfil, RepositorioPerfil } from "../src/repositorio";

function repoMemoria() {
  const perfiles = new Map<string, Perfil>();
  const pins = new Map<string, string>();
  const repo: RepositorioPerfil = {
    async obtener(id) {
      return perfiles.get(id) ?? null;
    },
    async crearInicial(id) {
      const p = { userId: id, tienePin: false, creado: "2026-10-30" };
      perfiles.set(id, p);
      return p;
    },
    async actualizar(id, cambios) {
      const p = { ...perfiles.get(id)!, ...cambios };
      perfiles.set(id, p);
      return p;
    },
    async buscarPorHuella(h) {
      return [...perfiles.values()].find((p) => p.telefonoHash === h)?.userId ?? null;
    },
    async crearPin(id, hash) {
      if (pins.has(id)) return false;
      pins.set(id, hash);
      perfiles.get(id)!.tienePin = true;
      return true;
    },
  };
  return { repo, perfiles, pins };
}

let mem: ReturnType<typeof repoMemoria>;
let aud: ReturnType<typeof auditoriaMemoria>;
let h: ReturnType<typeof crearManejador>;

beforeEach(() => {
  mem = repoMemoria();
  aud = auditoriaMemoria();
  h = crearManejador({ servicio: "svc-profile", verificador: () => verificadorFalso, salidaLog: () => {}, rutas: rutas({ repo: mem.repo, auditoria: aud }) });
});

describe("svc-profile", () => {
  it("GET /me crea el perfil del sub del token y responde un DTO mínimo", async () => {
    const r = await h(evento("GET", "/me"));
    expect(r.statusCode).toBe(200);
    expect(cuerpo(r)).toEqual({ nombre: null, telefono: null, tienePin: false });
    expect(mem.perfiles.has(ANA)).toBe(true);
  });

  it("PATCH /me guarda el teléfono y lo devuelve enmascarado (CTRL-03)", async () => {
    const r = await h(evento("PATCH", "/me", { cuerpo: { nombre: "Ana López", telefono: "5555-1234" } }));
    expect(r.statusCode).toBe(200);
    expect(cuerpo(r).telefono).toBe("****1234");
    expect(r.body).not.toContain("55551234");
    expect(r.body).not.toContain("telefonoHash");
  });

  it("PATCH /me rechaza mass assignment: tienePin, userId o saldo (CTRL-04, CA-04)", async () => {
    for (const extra of [{ tienePin: true }, { userId: BETO }, { saldoCentavos: 999999 }]) {
      const r = await h(evento("PATCH", "/me", { cuerpo: { nombre: "Ana", ...extra } }));
      expect(r.statusCode).toBe(400);
    }
    expect(mem.perfiles.get(ANA)?.tienePin ?? false).toBe(false);
  });

  it("PATCH /me no deja tomar el teléfono de otro usuario (409)", async () => {
    await h(evento("PATCH", "/me", { sub: BETO, cuerpo: { telefono: "55551234" } }));
    const r = await h(evento("PATCH", "/me", { cuerpo: { telefono: "55551234" } }));
    expect(r.statusCode).toBe(409);
  });

  it("PATCH /me rechaza texto con caracteres de script", async () => {
    const r = await h(evento("PATCH", "/me", { cuerpo: { nombre: "<script>alert(1)</script>" } }));
    expect(r.statusCode).toBe(400);
  });

  it("GET /users/search devuelve solo nombre corto y teléfono enmascarado", async () => {
    await h(evento("PATCH", "/me", { sub: BETO, cuerpo: { nombre: "Beto Pérez Gómez", telefono: "55559876" } }));
    const r = await h(evento("GET", "/users/search", { consulta: { phone: "+50255559876" } }));
    expect(r.statusCode).toBe(200);
    expect(cuerpo(r)).toEqual({ nombre: "Beto G.", telefono: "****9876" });
  });

  it("GET /users/search responde 404 igual si no existe", async () => {
    const r = await h(evento("GET", "/users/search", { consulta: { phone: "55550000" } }));
    expect(r.statusCode).toBe(404);
  });

  it("POST /pin guarda solo el hash scrypt y no deja cambiarlo sin el anterior (CTRL-02)", async () => {
    const r1 = await h(evento("POST", "/pin", { cuerpo: { pin: "482913" } }));
    expect(r1.statusCode).toBe(201);
    expect(mem.pins.get(ANA)).toMatch(/^scrypt\$/);
    expect(mem.pins.get(ANA)).not.toContain("482913");
    const r2 = await h(evento("POST", "/pin", { cuerpo: { pin: "739182" } }));
    expect(r2.statusCode).toBe(409);
    expect(aud.eventos.map((e) => e.resultado)).toEqual(["ok", "rechazado"]);
  });

  it("POST /pin rechaza PIN trivial", async () => {
    expect((await h(evento("POST", "/pin", { cuerpo: { pin: "111111" } }))).statusCode).toBe(400);
  });
});
