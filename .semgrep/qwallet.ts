// Pruebas de las reglas propias (semgrep --test .semgrep). Cada "ruleid" marca una línea
// que la regla DEBE detectar; cada "ok" una que NO debe marcar. No es código del producto.
import { z } from "zod";

declare const c: { send(x: unknown): Promise<unknown> };
declare const event: { body: string; headers: Record<string, string> };
declare const guardado: { pin: string; hash: string };
declare class ScanCommand { constructor(x: unknown) }
declare class QueryCommand { constructor(x: unknown) }
declare function llamarApi(ruta: string): Promise<unknown>;

export async function pruebas(pin: string) {
  // ruleid: qwallet-dynamodb-scan
  await c.send(new ScanCommand({ TableName: "qwallet-cuentas" }));
  // ok: qwallet-dynamodb-scan
  await c.send(new QueryCommand({ TableName: "qwallet-cuentas" }));

  // ruleid: qwallet-log-cuerpo-solicitud
  console.log("solicitud", event.body);
  // ruleid: qwallet-log-cuerpo-solicitud
  console.info(event.headers);
  // ok: qwallet-log-cuerpo-solicitud
  console.log("solicitud recibida");

  // ruleid: qwallet-comparacion-pin-directa
  if (guardado.pin === pin) return true;
  // ruleid: qwallet-comparacion-pin-directa
  if (pin === guardado.hash) return true;

  // ruleid: qwallet-aleatorio-inseguro
  const id = Math.random();

  // ruleid: qwallet-cuerpo-sin-zod
  const datos = JSON.parse(event.body);

  // ruleid: qwallet-zod-sin-strict
  const flojo = z.object({ monto: z.number() });
  // ok: qwallet-zod-sin-strict
  const estricto = z.object({ monto: z.number() }).strict();

  // ruleid: qwallet-access-control-allow-origin
  const cabeceras = { "Access-Control-Allow-Origin": "*" };
  return { id, datos, flojo, estricto, cabeceras };

  // ruleid: qwallet-fetch-sin-pinning
  await fetch("https://api.example/me");
  // ok: qwallet-fetch-sin-pinning
  await llamarApi("/me");
}
