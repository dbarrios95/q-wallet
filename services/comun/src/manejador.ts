// Envoltura común de cada Lambda: enrutamiento, identidad, logs y errores.
// - Cada ruta declara su método y recurso exactos; lo demás responde 404 genérico.
// - El JWT se verifica antes de llegar a la lógica (ver identidad.ts).
// - Los errores no previstos se registran del lado del servidor y el cliente solo
//   recibe "error_interno" con su correlationId (CTRL-13).
import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient } from "@aws-sdk/lib-dynamodb";
import type { APIGatewayProxyEvent, APIGatewayProxyResult } from "aws-lambda";
import { ErrorHttp, responder, responderError } from "./http";
import { obtenerIdentidad, type Identidad, type VerificadorJwt } from "./identidad";
import { crearRegistro, type Registro } from "./registro";

export interface Contexto {
  event: APIGatewayProxyEvent;
  identidad: Identidad;
  correlationId: string;
  registro: Registro;
}

export interface Resultado {
  status: number;
  cuerpo: unknown;
}

export type Ruta = (ctx: Contexto) => Promise<Resultado>;

export interface OpcionesManejador {
  servicio: string;
  rutas: Record<string, Ruta>;
  verificador: () => VerificadorJwt;
  salidaLog?: (linea: string) => void;
}

export function crearManejador(op: OpcionesManejador) {
  return async (event: APIGatewayProxyEvent): Promise<APIGatewayProxyResult> => {
    const correlationId = event.requestContext?.requestId ?? "sin-id";
    const registro = crearRegistro(op.servicio, correlationId, op.salidaLog);
    const clave = `${event.httpMethod} ${event.resource}`;
    const inicio = Date.now();
    // Nunca se registra el cuerpo ni las cabeceras: solo método, recurso y resultado.
    try {
      const identidad = await obtenerIdentidad(event, op.verificador());
      const ruta = op.rutas[clave];
      if (!ruta) throw new ErrorHttp(404, "ruta_no_soportada");
      const r = await ruta({ event, identidad, correlationId, registro });
      registro.info("solicitud", { ruta: clave, status: r.status, ms: Date.now() - inicio, usuario: identidad.sub });
      return responder(r.status, r.cuerpo, correlationId);
    } catch (e) {
      if (e instanceof ErrorHttp) {
        registro.aviso("solicitud_rechazada", { ruta: clave, status: e.status, codigo: e.codigo, ms: Date.now() - inicio });
        return responderError(e, correlationId);
      }
      const nombre = e instanceof Error ? e.name : "desconocido";
      registro.error("error_no_controlado", { ruta: clave, tipo: nombre, ms: Date.now() - inicio });
      return responderError(new ErrorHttp(500, "error_interno"), correlationId);
    }
  };
}

let documentos: DynamoDBDocumentClient | undefined;

/** Cliente de DynamoDB reutilizado entre invocaciones (TLS 1.2+ del SDK, región de la Lambda). */
export function clienteDynamo(): DynamoDBDocumentClient {
  documentos ??= DynamoDBDocumentClient.from(new DynamoDBClient({}), {
    marshallOptions: { removeUndefinedValues: true },
  });
  return documentos;
}

export function tabla(nombre: string): string {
  const valor = process.env[nombre];
  if (!valor) throw new Error(`Falta la variable ${nombre}`);
  return valor;
}
