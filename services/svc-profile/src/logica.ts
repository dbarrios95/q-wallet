// svc-profile: GET /me, PATCH /me, GET /users/search, POST /pin.
// Controles: CTRL-01 (cada operación usa solo el sub del token), CTRL-02 (PIN con scrypt),
// CTRL-03 (respuestas mínimas y enmascaradas), CTRL-04 (zod estricto), CTRL-09 (auditoría).
import { z } from "zod";
import type { Auditoria } from "../../comun/src/auditoria";
import { enmascararTelefono, huellaTelefono, nombreCorto, telefono } from "../../comun/src/datos_personales";
import { ErrorHttp } from "../../comun/src/http";
import type { Contexto, Resultado, Ruta } from "../../comun/src/manejador";
import { hashPin, pinNuevo } from "../../comun/src/pin";
import { leerConsulta, leerCuerpo, texto } from "../../comun/src/validacion";
import type { Perfil, RepositorioPerfil } from "./repositorio";

export interface Dependencias {
  repo: RepositorioPerfil;
  auditoria: Auditoria;
}

/** DTO mínimo (CTRL-03): ni huella, ni teléfono completo, ni fechas internas. */
export function perfilDto(p: Perfil) {
  return {
    nombre: p.nombre ?? null,
    telefono: p.telefono ? enmascararTelefono(p.telefono) : null,
    tienePin: p.tienePin,
  };
}

const cambiosPerfil = z
  .object({ nombre: texto(2, 60).optional(), telefono: telefono.optional() })
  .strict()
  .refine((c) => c.nombre !== undefined || c.telefono !== undefined, { message: "sin cambios" });

const busqueda = z.object({ phone: telefono }).strict();

const nuevoPin = z.object({ pin: pinNuevo }).strict();

export function rutas(d: Dependencias): Record<string, Ruta> {
  const leerMe = async ({ identidad }: Contexto): Promise<Resultado> => {
    const perfil = (await d.repo.obtener(identidad.sub)) ?? (await d.repo.crearInicial(identidad.sub));
    return { status: 200, cuerpo: perfilDto(perfil) };
  };

  const cambiarMe = async ({ event, identidad, correlationId }: Contexto): Promise<Resultado> => {
    const cambios = leerCuerpo(event, cambiosPerfil);
    if (!(await d.repo.obtener(identidad.sub))) await d.repo.crearInicial(identidad.sub);
    const actualizar: Partial<Perfil> = {};
    if (cambios.nombre !== undefined) actualizar.nombre = cambios.nombre;
    if (cambios.telefono !== undefined) {
      const huella = huellaTelefono(cambios.telefono);
      const dueno = await d.repo.buscarPorHuella(huella);
      if (dueno && dueno !== identidad.sub) throw new ErrorHttp(409, "conflicto");
      actualizar.telefono = cambios.telefono;
      actualizar.telefonoHash = huella;
    }
    const perfil = await d.repo.actualizar(identidad.sub, actualizar);
    await d.auditoria.registrar({
      actor: identidad.sub,
      accion: "perfil.actualizar",
      recurso: `perfil/${identidad.sub}`,
      resultado: "ok",
      correlationId,
      detalle: { campos: Object.keys(cambios).join(",") },
    });
    return { status: 200, cuerpo: perfilDto(perfil) };
  };

  const buscar = async ({ event }: Contexto): Promise<Resultado> => {
    const { phone } = leerConsulta(event, busqueda);
    const userId = await d.repo.buscarPorHuella(huellaTelefono(phone));
    const perfil = userId ? await d.repo.obtener(userId) : null;
    // Mismo 404 si no existe o si no completó su perfil: no se distingue un caso del otro.
    if (!perfil?.nombre || !perfil.telefono) throw new ErrorHttp(404, "no_encontrado");
    return { status: 200, cuerpo: { nombre: nombreCorto(perfil.nombre), telefono: enmascararTelefono(perfil.telefono) } };
  };

  const crearPin = async ({ event, identidad, correlationId }: Contexto): Promise<Resultado> => {
    const { pin } = leerCuerpo(event, nuevoPin);
    if (!(await d.repo.obtener(identidad.sub))) await d.repo.crearInicial(identidad.sub);
    const creado = await d.repo.crearPin(identidad.sub, await hashPin(pin));
    await d.auditoria.registrar({
      actor: identidad.sub,
      accion: "pin.crear",
      recurso: `pin/${identidad.sub}`,
      resultado: creado ? "ok" : "rechazado",
      correlationId,
    });
    // Cambiar un PIN existente exige verificar el anterior: fuera del MVP, por eso 409.
    if (!creado) throw new ErrorHttp(409, "conflicto");
    return { status: 201, cuerpo: { tienePin: true } };
  };

  return {
    "GET /me": leerMe,
    "PATCH /me": cambiarMe,
    "GET /users/search": buscar,
    "POST /pin": crearPin,
  };
}
