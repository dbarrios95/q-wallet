// svc-transfers: POST /transfers, GET /transfers/{id} y beneficiarios (GET/POST/DELETE).
// CTRL-01: una transferencia solo la ve quien la envió o la recibió (si no, 404).
// CTRL-02: PIN con scrypt, reserva atómica del intento y bloqueo de 15 min al quinto fallo.
// CTRL-04: zod estricto; el monto es entero en centavos y tiene tope por operación.
// CTRL-06: Idempotency-Key obligatoria + transacción de DynamoDB con condición de saldo.
// CTRL-09: auditoría de cada transferencia y de cada PIN rechazado.
import { createHash, randomUUID } from "node:crypto";
import { z } from "zod";
import type { Auditoria } from "../../comun/src/auditoria";
import { enmascararTelefono, huellaTelefono, telefono } from "../../comun/src/datos_personales";
import { ErrorHttp } from "../../comun/src/http";
import type { Contexto, Resultado, Ruta } from "../../comun/src/manejador";
import { pinIngresado, verificarPin } from "../../comun/src/pin";
import { centavos, leerConsulta, leerCuerpo, leerRuta, texto, uuid } from "../../comun/src/validacion";
import { MAXIMO_BENEFICIARIOS, type Beneficiario, type RepositorioTransferencias, type Transferencia } from "./repositorio";

/** Tope por transferencia (dinero simulado): Q5,000.00. Decisión pendiente de Daniel (ESTADO). */
export const MONTO_MAXIMO_CENTAVOS = 500_000;

export const CATEGORIAS = ["alimentacion", "transporte", "servicios", "entretenimiento", "salud", "educacion", "transferencias", "otros"] as const;

export interface Dependencias {
  repo: RepositorioTransferencias;
  auditoria: Auditoria;
  ahora?: () => number;
}

const solicitudTransferencia = z
  .object({
    telefono: telefono.optional(),
    beneficiarioId: uuid.optional(),
    montoCentavos: centavos,
    pin: pinIngresado,
    categoria: z.enum(CATEGORIAS).default("transferencias"),
    descripcion: texto(1, 80).optional(),
  })
  .strict()
  .refine((s) => (s.telefono === undefined) !== (s.beneficiarioId === undefined), { message: "un solo destino", path: ["destino"] });

const nuevoBeneficiario = z.object({ telefono, alias: texto(1, 40) }).strict();
const conId = z.object({ id: uuid }).strict();

function claveIdempotencia(event: Contexto["event"]): string {
  const valor = Object.entries(event.headers ?? {}).find(([k]) => k.toLowerCase() === "idempotency-key")?.[1];
  const r = uuid.safeParse(valor);
  if (!r.success) throw new ErrorHttp(400, "solicitud_invalida", ["Idempotency-Key"]);
  return r.data.toLowerCase();
}

/** Huella de la solicitud sin el PIN: reusar la misma clave con otro contenido es un conflicto. */
function huellaSolicitud(s: Record<string, unknown>): string {
  const { pin: _pin, ...resto } = s;
  const orden = Object.fromEntries(Object.entries(resto).sort(([a], [b]) => a.localeCompare(b)));
  return createHash("sha256").update(JSON.stringify(orden)).digest("hex");
}

export function transferenciaDto(t: Transferencia, sub: string) {
  const enviada = t.origenUserId === sub;
  return {
    transferId: t.transferId,
    direccion: enviada ? "enviada" : "recibida",
    estado: t.estado,
    montoCentavos: t.montoCentavos,
    categoria: enviada ? t.categoria : "transferencias",
    descripcion: t.descripcion ?? null,
    contraparte: enviada ? t.destinoMascara : "Usuario Q-Wallet",
    fecha: t.fecha,
  };
}

const beneficiarioDto = (b: Beneficiario) => ({ beneficiarioId: b.beneficiarioId, alias: b.alias, telefono: b.telefonoMascara });

export function rutas(d: Dependencias): Record<string, Ruta> {
  const ahora = d.ahora ?? Date.now;

  const transferir = async ({ event, identidad, correlationId }: Contexto): Promise<Resultado> => {
    const sub = identidad.sub;
    const clave = claveIdempotencia(event);
    const s = leerCuerpo(event, solicitudTransferencia);
    const huella = huellaSolicitud(s);

    // 1. Reintento con la misma clave: se devuelve la respuesta guardada, sin mover dinero otra vez.
    const previa = await d.repo.leerIdempotencia(sub, clave);
    if (previa) {
      if (previa.huella !== huella) throw new ErrorHttp(409, "conflicto");
      return { status: previa.status, cuerpo: JSON.parse(previa.respuesta) };
    }

    // 2. Límite por operación.
    if (s.montoCentavos > MONTO_MAXIMO_CENTAVOS) throw new ErrorHttp(422, "limite_excedido");

    // 3. PIN de transacción.
    const t0 = ahora();
    const reserva = await d.repo.reservarIntentoPin(sub, t0);
    if (reserva.estado === "sin_pin") throw new ErrorHttp(409, "conflicto");
    if (reserva.estado === "bloqueado") {
      await d.auditoria.registrar({ actor: sub, accion: "transferencia.pin_bloqueado", recurso: `pin/${sub}`, resultado: "rechazado", correlationId });
      throw new ErrorHttp(423, "pin_bloqueado");
    }
    const correcto = await verificarPin(s.pin, reserva.hash);
    await d.repo.cerrarIntentoPin(sub, correcto, reserva.intentos, t0);
    if (!correcto) {
      await d.auditoria.registrar({
        actor: sub,
        accion: "transferencia.pin_incorrecto",
        recurso: `pin/${sub}`,
        resultado: "rechazado",
        correlationId,
        detalle: { intento: reserva.intentos },
      });
      throw new ErrorHttp(403, "pin_incorrecto");
    }

    // 4. Destino: por teléfono o por beneficiario guardado del mismo usuario.
    let destinoUserId: string | null;
    let destinoMascara: string;
    if (s.telefono !== undefined) {
      destinoUserId = await d.repo.usuarioPorHuella(huellaTelefono(s.telefono));
      destinoMascara = enmascararTelefono(s.telefono);
    } else {
      const b = await d.repo.obtenerBeneficiario(sub, s.beneficiarioId!);
      destinoUserId = b?.destinoUserId ?? null;
      destinoMascara = b?.telefonoMascara ?? "";
    }
    if (!destinoUserId) throw new ErrorHttp(404, "no_encontrado");
    if (destinoUserId === sub) throw new ErrorHttp(400, "solicitud_invalida", ["destino"]);

    const [origen, destino] = await Promise.all([d.repo.cuentaPrincipal(sub), d.repo.cuentaPrincipal(destinoUserId)]);
    if (!origen || !destino) throw new ErrorHttp(404, "no_encontrado");

    // 5. Movimiento atómico.
    const transferencia: Transferencia = {
      transferId: randomUUID(),
      origenUserId: sub,
      destinoUserId,
      montoCentavos: s.montoCentavos,
      categoria: s.categoria,
      ...(s.descripcion !== undefined ? { descripcion: s.descripcion } : {}),
      destinoMascara,
      fecha: new Date(t0).toISOString(),
      estado: "completada",
    };
    const r = await d.repo.ejecutar({
      claveIdempotencia: clave,
      huellaSolicitud: huella,
      respuesta: (t) => ({ status: 201, cuerpo: transferenciaDto(t, sub) }),
      origen,
      destino,
      transferencia,
    });
    if (r.estado === "saldo_insuficiente") throw new ErrorHttp(422, "saldo_insuficiente");
    if (r.estado === "duplicada") {
      // Otra solicitud con la misma clave ganó la carrera: se devuelve su resultado.
      const ganadora = await d.repo.leerIdempotencia(sub, clave);
      if (!ganadora || ganadora.huella !== huella) throw new ErrorHttp(409, "conflicto");
      return { status: ganadora.status, cuerpo: JSON.parse(ganadora.respuesta) };
    }
    await d.auditoria.registrar({
      actor: sub,
      accion: "transferencia.crear",
      recurso: `transferencia/${transferencia.transferId}`,
      resultado: "ok",
      correlationId,
      detalle: { montoCentavos: s.montoCentavos },
    });
    return { status: r.status, cuerpo: r.cuerpo };
  };

  const consultar = async ({ event, identidad }: Contexto): Promise<Resultado> => {
    const { id } = leerRuta(event, conId);
    const t = await d.repo.obtenerTransferencia(id);
    // BOLA: si no es del usuario, se responde igual que si no existiera.
    if (!t || (t.origenUserId !== identidad.sub && t.destinoUserId !== identidad.sub)) throw new ErrorHttp(404, "no_encontrado");
    return { status: 200, cuerpo: transferenciaDto(t, identidad.sub) };
  };

  const listarBeneficiarios = async ({ identidad }: Contexto): Promise<Resultado> => {
    const lista = await d.repo.listarBeneficiarios(identidad.sub);
    return { status: 200, cuerpo: { beneficiarios: lista.map(beneficiarioDto) } };
  };

  const crearBeneficiario = async ({ event, identidad, correlationId }: Contexto): Promise<Resultado> => {
    const b = leerCuerpo(event, nuevoBeneficiario);
    const destinoUserId = await d.repo.usuarioPorHuella(huellaTelefono(b.telefono));
    if (!destinoUserId) throw new ErrorHttp(404, "no_encontrado");
    if (destinoUserId === identidad.sub) throw new ErrorHttp(400, "solicitud_invalida", ["telefono"]);
    const existentes = await d.repo.listarBeneficiarios(identidad.sub);
    if (existentes.length >= MAXIMO_BENEFICIARIOS) throw new ErrorHttp(409, "conflicto");
    if (existentes.some((x) => x.destinoUserId === destinoUserId)) throw new ErrorHttp(409, "conflicto");
    const nuevo: Beneficiario = {
      userId: identidad.sub,
      beneficiarioId: randomUUID(),
      alias: b.alias,
      destinoUserId,
      telefonoMascara: enmascararTelefono(b.telefono),
      creado: new Date(ahora()).toISOString(),
    };
    await d.repo.crearBeneficiario(nuevo);
    await d.auditoria.registrar({
      actor: identidad.sub,
      accion: "beneficiario.crear",
      recurso: `beneficiario/${nuevo.beneficiarioId}`,
      resultado: "ok",
      correlationId,
    });
    return { status: 201, cuerpo: beneficiarioDto(nuevo) };
  };

  const eliminarBeneficiario = async ({ event, identidad, correlationId }: Contexto): Promise<Resultado> => {
    const { id } = leerConsulta(event, conId);
    // La llave lleva el sub del token: no se puede borrar el beneficiario de otra persona.
    const borrado = await d.repo.eliminarBeneficiario(identidad.sub, id);
    if (!borrado) throw new ErrorHttp(404, "no_encontrado");
    await d.auditoria.registrar({ actor: identidad.sub, accion: "beneficiario.eliminar", recurso: `beneficiario/${id}`, resultado: "ok", correlationId });
    return { status: 204, cuerpo: null };
  };

  return {
    "POST /transfers": transferir,
    "GET /transfers/{id}": consultar,
    "GET /beneficiaries": listarBeneficiarios,
    "POST /beneficiaries": crearBeneficiario,
    "DELETE /beneficiaries": eliminarBeneficiario,
  };
}
