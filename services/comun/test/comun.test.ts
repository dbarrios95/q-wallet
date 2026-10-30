// Pruebas de los controles comunes: CTRL-02, CTRL-04, CTRL-05, CTRL-09, CTRL-13, CTRL-18.
import { describe, expect, it } from "vitest";
import { z } from "zod";
import { enmascararCorreo, enmascararTelefono, nombreCorto, telefono } from "../src/datos_personales";
import { ErrorHttp } from "../src/http";
import { crearManejador } from "../src/manejador";
import { codificarCursor, decodificarCursor } from "../src/paginacion";
import { estaBloqueado, hashPin, pinNuevo, trasFallo, verificarPin } from "../src/pin";
import { redactar } from "../src/registro";
import { leerCuerpo } from "../src/validacion";
import { ANA, BETO, cuerpo, evento, verificadorFalso } from "./apoyo";

function manejadorDePrueba(lineas: string[] = []) {
  return crearManejador({
    servicio: "prueba",
    verificador: () => verificadorFalso,
    salidaLog: (l) => lineas.push(l),
    rutas: {
      "GET /ok": async ({ identidad }) => ({ status: 200, cuerpo: { sub: identidad.sub } }),
      "GET /falla": async () => {
        throw new Error("detalle interno: tabla qwallet-pin, llave 123");
      },
      "POST /eco": async ({ event }) => ({ status: 200, cuerpo: leerCuerpo(event, z.object({ a: z.string() }).strict()) }),
    },
  });
}

describe("CTRL-18 / JWT: identidad verificada en la Lambda", () => {
  it("sin Authorization responde 401", async () => {
    const r = await manejadorDePrueba()(evento("GET", "/ok", { sub: null }));
    expect(r.statusCode).toBe(401);
  });

  it("token con firma alterada responde 401 (CA-13)", async () => {
    const e = evento("GET", "/ok");
    e.headers.Authorization = e.headers.Authorization!.replace(".firma", ".otra");
    expect((await manejadorDePrueba()(e)).statusCode).toBe(401);
  });

  it("sub del authorizer distinto al del token responde 401", async () => {
    const e = evento("GET", "/ok");
    (e.requestContext as unknown as { authorizer: { claims: { sub: string } } }).authorizer.claims.sub = BETO;
    expect((await manejadorDePrueba()(e)).statusCode).toBe(401);
  });

  it("token válido llega a la ruta con el sub verificado", async () => {
    const r = await manejadorDePrueba()(evento("GET", "/ok"));
    expect(r.statusCode).toBe(200);
    expect(cuerpo(r).sub).toBe(ANA);
  });
});

describe("CTRL-13: errores genéricos y cabeceras de seguridad", () => {
  it("un error interno no filtra el mensaje ni la pila", async () => {
    const lineas: string[] = [];
    const r = await manejadorDePrueba(lineas)(evento("GET", "/falla"));
    expect(r.statusCode).toBe(500);
    expect(r.body).not.toContain("qwallet-pin");
    expect(cuerpo(r)).toMatchObject({ error: "error_interno", correlationId: "prueba-123" });
    expect(lineas.join("\n")).not.toContain("llave 123");
  });

  it("todas las respuestas llevan cabeceras de seguridad y ninguna de CORS", async () => {
    const r = await manejadorDePrueba()(evento("GET", "/ok"));
    expect(r.headers).toMatchObject({ "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff", "X-Frame-Options": "DENY" });
    expect(Object.keys(r.headers ?? {}).some((k) => k.toLowerCase().startsWith("access-control"))).toBe(false);
  });

  it("ruta no prevista responde 404 genérico", async () => {
    expect((await manejadorDePrueba()(evento("DELETE", "/ok"))).statusCode).toBe(404);
  });
});

describe("CTRL-04: validación estricta", () => {
  it("rechaza campos no permitidos (mass assignment)", async () => {
    const r = await manejadorDePrueba()(evento("POST", "/eco", { cuerpo: { a: "x", esAdmin: true } }));
    expect(r.statusCode).toBe(400);
    expect(r.body).not.toContain("true");
  });

  it("rechaza JSON mal formado y cuerpos de más de 8 KB", async () => {
    expect((await manejadorDePrueba()(evento("POST", "/eco", { cuerpoCrudo: "{a:" }))).statusCode).toBe(400);
    expect((await manejadorDePrueba()(evento("POST", "/eco", { cuerpo: { a: "x".repeat(9000) } }))).statusCode).toBe(413);
  });

  it("normaliza teléfonos de Guatemala y rechaza otros", () => {
    expect(telefono.parse("5555-1234")).toBe("+50255551234");
    expect(telefono.safeParse("+15551234567").success).toBe(false);
    expect(telefono.safeParse("12345678").success).toBe(false);
  });
});

describe("CTRL-03: enmascarado", () => {
  it("teléfono, correo y nombre", () => {
    expect(enmascararTelefono("+50255551234")).toBe("****1234");
    expect(enmascararCorreo("daniel@ejemplo.com")).toBe("d***@ejemplo.com");
    expect(nombreCorto("Daniel Edivin Barrios")).toBe("Daniel B.");
  });
});

describe("CTRL-09: redacción en logs", () => {
  it("quita PIN, tokens, teléfonos y correos aunque estén anidados", () => {
    const r = JSON.stringify(
      redactar({ pin: "123987", datos: { telefono: "+50255551234", Authorization: "Bearer x" }, nota: "eyJhbGciOi.eyJzdWIiOi.abcdef" }),
    );
    expect(r).not.toContain("123987");
    expect(r).not.toContain("55551234");
    expect(r).not.toContain("eyJhbGciOi");
    expect(r).not.toContain("Bearer");
  });
});

describe("CTRL-05: cursor de paginación", () => {
  it("rechaza un cursor que apunta a otra cuenta", () => {
    const ajeno = codificarCursor({ accountId: "otra", fechaId: "2026-10-01" })!;
    expect(() => decodificarCursor(ajeno, ["accountId", "fechaId"], { campo: "accountId", valor: "mia" })).toThrow(ErrorHttp);
  });

  it("rechaza cursores con campos de más o basura", () => {
    const extra = codificarCursor({ accountId: "mia", fechaId: "x", userId: ANA })!;
    expect(() => decodificarCursor(extra, ["accountId", "fechaId"], { campo: "accountId", valor: "mia" })).toThrow(ErrorHttp);
    expect(() => decodificarCursor("no-es-json", ["accountId", "fechaId"], { campo: "accountId", valor: "mia" })).toThrow(ErrorHttp);
  });
});

describe("CTRL-02: PIN", () => {
  it("guarda scrypt con sal y verifica en tiempo constante", async () => {
    const h1 = await hashPin("482913");
    const h2 = await hashPin("482913");
    expect(h1).toMatch(/^scrypt\$32768\$8\$1\$/);
    expect(h1).not.toBe(h2); // sal distinta
    expect(h1).not.toContain("482913");
    expect(await verificarPin("482913", h1)).toBe(true);
    expect(await verificarPin("482914", h1)).toBe(false);
  });

  it("rechaza PIN triviales", () => {
    for (const p of ["000000", "123456", "654321", "890123"]) expect(pinNuevo.safeParse(p).success).toBe(false);
    expect(pinNuevo.safeParse("482913").success).toBe(true);
  });

  it("bloquea 15 minutos al quinto fallo", () => {
    const ahora = 1_000_000;
    expect(trasFallo(3, ahora)).toEqual({ intentos: 4 });
    const r = trasFallo(4, ahora);
    expect(r.bloqueadoHasta).toBe(ahora + 15 * 60_000);
    expect(estaBloqueado({ hash: "", intentos: 0, bloqueadoHasta: r.bloqueadoHasta! }, ahora + 60_000)).toBe(true);
    expect(estaBloqueado({ hash: "", intentos: 0, bloqueadoHasta: r.bloqueadoHasta! }, ahora + 16 * 60_000)).toBe(false);
  });
});
