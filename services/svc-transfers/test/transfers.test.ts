// svc-transfers: CTRL-01, CTRL-02, CTRL-04, CTRL-06 y auditoría.
import { beforeEach, describe, expect, it } from "vitest";
import { ANA, BETO, auditoriaMemoria, cuerpo, evento, verificadorFalso } from "../../comun/test/apoyo";
import { huellaTelefono } from "../../comun/src/datos_personales";
import { crearManejador } from "../../comun/src/manejador";
import { INTENTOS_MAXIMOS, MINUTOS_BLOQUEO, hashPin } from "../../comun/src/pin";
import { MONTO_MAXIMO_CENTAVOS, rutas } from "../src/logica";
import type { Beneficiario, Cuenta, RegistroIdempotencia, RepositorioTransferencias, Transferencia } from "../src/repositorio";

const CARLOS = "44444444-4444-4444-8444-444444444444";
const TEL_BETO = "+50255552222";
const TEL_CARLOS = "+50255553333";
let PIN_HASH = "";

/** Repositorio en memoria con la misma semántica de condiciones que DynamoDB. */
function repoMemoria() {
  const cuentas = new Map<string, Cuenta>([
    [ANA, { userId: ANA, accountId: "c-ana", saldoCentavos: 100_000 }],
    [BETO, { userId: BETO, accountId: "c-beto", saldoCentavos: 0 }],
    [CARLOS, { userId: CARLOS, accountId: "c-carlos", saldoCentavos: 0 }],
  ]);
  const telefonos = new Map([
    [huellaTelefono(TEL_BETO), BETO],
    [huellaTelefono(TEL_CARLOS), CARLOS],
  ]);
  const pin = new Map<string, { hash: string; intentos: number; bloqueadoHasta?: number }>([[ANA, { hash: PIN_HASH, intentos: 0 }]]);
  const idem = new Map<string, RegistroIdempotencia>();
  const transferencias = new Map<string, Transferencia>();
  const beneficiarios: Beneficiario[] = [];
  let ejecuciones = 0;

  const repo: RepositorioTransferencias = {
    async leerIdempotencia(u, k) {
      return idem.get(`${u}#${k}`) ?? null;
    },
    async reservarIntentoPin(u, ahora) {
      const p = pin.get(u);
      if (!p) return { estado: "sin_pin" };
      if ((p.bloqueadoHasta ?? 0) > ahora || p.intentos >= INTENTOS_MAXIMOS) return { estado: "bloqueado" };
      p.intentos += 1;
      return { estado: "ok", hash: p.hash, intentos: p.intentos };
    },
    async cerrarIntentoPin(u, ok, intentos, ahora) {
      const p = pin.get(u)!;
      if (ok) {
        p.intentos = 0;
        delete p.bloqueadoHasta;
      } else if (intentos >= INTENTOS_MAXIMOS) {
        p.intentos = 0;
        p.bloqueadoHasta = ahora + MINUTOS_BLOQUEO * 60_000;
      }
    },
    async usuarioPorHuella(h) {
      return telefonos.get(h) ?? null;
    },
    async cuentaPrincipal(u) {
      const c = cuentas.get(u);
      return c ? { ...c } : null;
    },
    async ejecutar(n) {
      const k = `${n.transferencia.origenUserId}#${n.claveIdempotencia}`;
      if (idem.has(k)) return { estado: "duplicada" };
      const origen = cuentas.get(n.origen.userId)!;
      if (origen.saldoCentavos < n.transferencia.montoCentavos) return { estado: "saldo_insuficiente" };
      const { status, cuerpo: c } = n.respuesta(n.transferencia);
      idem.set(k, { huella: n.huellaSolicitud, status, respuesta: JSON.stringify(c) });
      origen.saldoCentavos -= n.transferencia.montoCentavos;
      cuentas.get(n.destino.userId)!.saldoCentavos += n.transferencia.montoCentavos;
      transferencias.set(n.transferencia.transferId, n.transferencia);
      ejecuciones += 1;
      return { estado: "ok", status, cuerpo: c };
    },
    async obtenerTransferencia(id) {
      return transferencias.get(id) ?? null;
    },
    async listarBeneficiarios(u) {
      return beneficiarios.filter((b) => b.userId === u);
    },
    async obtenerBeneficiario(u, id) {
      return beneficiarios.find((b) => b.userId === u && b.beneficiarioId === id) ?? null;
    },
    async crearBeneficiario(b) {
      beneficiarios.push(b);
    },
    async eliminarBeneficiario(u, id) {
      const i = beneficiarios.findIndex((b) => b.userId === u && b.beneficiarioId === id);
      if (i < 0) return false;
      beneficiarios.splice(i, 1);
      return true;
    },
  };
  return { repo, cuentas, pin, transferencias, beneficiarios, ejecuciones: () => ejecuciones };
}

let mem: ReturnType<typeof repoMemoria>;
let aud: ReturnType<typeof auditoriaMemoria>;
let reloj = 1_800_000_000_000;
let h: ReturnType<typeof crearManejador>;

const clave = (n: number) => `00000000-0000-4000-8000-${String(n).padStart(12, "0")}`;
const transferir = (cuerpoSolicitud: Record<string, unknown>, k: string | null = clave(1), sub = ANA) =>
  h(evento("POST", "/transfers", { sub, cuerpo: cuerpoSolicitud, cabeceras: k ? { "Idempotency-Key": k } : {} }));
const base = { telefono: TEL_BETO, montoCentavos: 2_500, pin: "482913" };

beforeEach(async () => {
  PIN_HASH ||= await hashPin("482913");
  mem = repoMemoria();
  aud = auditoriaMemoria();
  h = crearManejador({
    servicio: "svc-transfers",
    verificador: () => verificadorFalso,
    salidaLog: () => {},
    rutas: rutas({ repo: mem.repo, auditoria: aud, ahora: () => reloj }),
  });
});

describe("POST /transfers", () => {
  it("transfiere, descuenta el saldo exacto y audita", async () => {
    const r = await transferir(base);
    expect(r.statusCode).toBe(201);
    expect(cuerpo(r)).toMatchObject({ direccion: "enviada", montoCentavos: 2_500, contraparte: "****2222" });
    expect(mem.cuentas.get(ANA)!.saldoCentavos).toBe(97_500);
    expect(mem.cuentas.get(BETO)!.saldoCentavos).toBe(2_500);
    expect(aud.eventos.at(-1)).toMatchObject({ accion: "transferencia.crear", resultado: "ok" });
  });

  it("sin Idempotency-Key (o con una que no es UUID) responde 400", async () => {
    expect((await transferir(base, null)).statusCode).toBe(400);
    expect((await transferir(base, "1")).statusCode).toBe(400);
  });

  it("CTRL-06: reintentar con la misma clave no vuelve a mover dinero", async () => {
    const r1 = await transferir(base);
    const r2 = await transferir(base);
    expect(r2.statusCode).toBe(201);
    expect(cuerpo(r2).transferId).toBe(cuerpo(r1).transferId);
    expect(mem.ejecuciones()).toBe(1);
    expect(mem.cuentas.get(ANA)!.saldoCentavos).toBe(97_500);
  });

  it("CTRL-06: misma clave con otro monto responde 409", async () => {
    await transferir(base);
    expect((await transferir({ ...base, montoCentavos: 9_000 })).statusCode).toBe(409);
  });

  it("CA-06: diez solicitudes simultáneas con la misma clave aplican una sola transferencia", async () => {
    const rs = await Promise.all(Array.from({ length: 10 }, () => transferir(base)));
    // Las que no alcanzan turno de PIN reciben 423 (reintentables); ninguna mueve dinero de más.
    expect(rs.every((r) => r.statusCode === 201 || r.statusCode === 423)).toBe(true);
    const exitosas = rs.filter((r) => r.statusCode === 201);
    expect(exitosas.length).toBeGreaterThan(0);
    expect(new Set(exitosas.map((r) => cuerpo(r).transferId)).size).toBe(1);
    expect(mem.cuentas.get(ANA)!.saldoCentavos).toBe(97_500);
    expect(mem.ejecuciones()).toBe(1);
  });

  it("CTRL-06: saldo insuficiente responde 422 y no cambia saldos", async () => {
    const r = await transferir({ ...base, montoCentavos: 100_001 }, clave(2));
    expect(r.statusCode).toBe(422);
    expect(mem.cuentas.get(ANA)!.saldoCentavos).toBe(100_000);
  });

  it("monto mayor al tope por operación responde 422 antes de pedir el PIN", async () => {
    const r = await transferir({ ...base, montoCentavos: MONTO_MAXIMO_CENTAVOS + 1 });
    expect(r.statusCode).toBe(422);
    expect(mem.pin.get(ANA)!.intentos).toBe(0);
  });

  it("CTRL-04: montos negativos, decimales o en texto se rechazan", async () => {
    for (const m of [-100, 10.5, "100", 0]) expect((await transferir({ ...base, montoCentavos: m })).statusCode).toBe(400);
  });

  it("CTRL-04: campos extra (por ejemplo origen) se rechazan", async () => {
    expect((await transferir({ ...base, origenUserId: BETO })).statusCode).toBe(400);
  });

  it("no se puede transferir a uno mismo ni a un teléfono inexistente", async () => {
    mem.cuentas.set(ANA, { userId: ANA, accountId: "c-ana", saldoCentavos: 100_000 });
    expect((await transferir({ ...base, telefono: "+50255559999" })).statusCode).toBe(404);
  });

  it("CA-02: cinco PIN incorrectos bloquean 15 minutos, aunque luego llegue el correcto", async () => {
    for (let i = 1; i <= 5; i++) expect((await transferir({ ...base, pin: "000001" }, clave(10 + i))).statusCode).toBe(403);
    const r = await transferir(base, clave(20));
    expect(r.statusCode).toBe(423);
    expect(mem.ejecuciones()).toBe(0);
    expect(aud.eventos.filter((e) => e.accion === "transferencia.pin_incorrecto")).toHaveLength(5);
    reloj += 16 * 60_000;
    expect((await transferir(base, clave(21))).statusCode).toBe(201);
  });

  it("CA-02: veinte intentos simultáneos con PIN incorrecto: solo 5 llegan a compararse", async () => {
    const rs = await Promise.all(Array.from({ length: 20 }, (_, i) => transferir({ ...base, pin: "000001" }, clave(100 + i))));
    expect(rs.filter((r) => r.statusCode === 403)).toHaveLength(5);
    expect(rs.filter((r) => r.statusCode === 423)).toHaveLength(15);
  });

  it("sin PIN creado responde 409", async () => {
    mem.pin.delete(ANA);
    expect((await transferir(base)).statusCode).toBe(409);
  });
});

describe("GET /transfers/{id}", () => {
  it("CA-01: quien no envió ni recibió la transferencia recibe 404", async () => {
    const id = cuerpo(await transferir(base)).transferId as string;
    expect((await h(evento("GET", "/transfers/{id}", { ruta: { id } }))).statusCode).toBe(200);
    const recibida = await h(evento("GET", "/transfers/{id}", { sub: BETO, ruta: { id } }));
    expect(cuerpo(recibida)).toMatchObject({ direccion: "recibida", contraparte: "Usuario Q-Wallet" });
    expect((await h(evento("GET", "/transfers/{id}", { sub: CARLOS, ruta: { id } }))).statusCode).toBe(404);
  });
});

describe("beneficiarios", () => {
  it("crear, listar enmascarado y transferir por beneficiarioId", async () => {
    const r = await h(evento("POST", "/beneficiaries", { cuerpo: { telefono: TEL_BETO, alias: "Beto" } }));
    expect(r.statusCode).toBe(201);
    const lista = cuerpo(await h(evento("GET", "/beneficiaries"))).beneficiarios as Record<string, unknown>[];
    expect(lista).toEqual([{ beneficiarioId: cuerpo(r).beneficiarioId, alias: "Beto", telefono: "****2222" }]);
    const t = await transferir({ beneficiarioId: cuerpo(r).beneficiarioId, montoCentavos: 100, pin: "482913" }, clave(3));
    expect(t.statusCode).toBe(201);
  });

  it("CA-01: no se puede usar ni borrar el beneficiario de otra persona", async () => {
    const r = await h(evento("POST", "/beneficiaries", { cuerpo: { telefono: TEL_BETO, alias: "Beto" } }));
    const id = cuerpo(r).beneficiarioId as string;
    expect((await h(evento("DELETE", "/beneficiaries", { sub: CARLOS, consulta: { id } }))).statusCode).toBe(404);
    expect(mem.beneficiarios).toHaveLength(1);
    expect((await h(evento("DELETE", "/beneficiaries", { consulta: { id } }))).statusCode).toBe(204);
  });

  it("no acepta dos destinos a la vez", async () => {
    const r = await transferir({ ...base, beneficiarioId: clave(9) });
    expect(r.statusCode).toBe(400);
  });
});
