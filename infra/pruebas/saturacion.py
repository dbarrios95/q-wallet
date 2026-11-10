#!/usr/bin/env python3
"""HAL-16: prueba de saturación más larga del throttling de API Gateway (CTRL-05, CA-06).

La etapa v1 tiene throttling por método: ráfaga 20 y 10 solicitudes por segundo
(infra/apigateway.tf). En el bloque 5, 40 solicitudes simultáneas con curl no
devolvieron ningún 429 (HAL-16). Esta prueba repite eso y agrega fases sostenidas.

Es una prueba de carga acotada contra la API propia, no una inundación: unas 2 500
solicitudes en total, nunca más de 60 por segundo, sin token (el authorizer responde
401, así que no corre ninguna Lambda ni se toca DynamoDB). Solo usa la biblioteca
estándar de Python.

Bloque 7 (segunda corrida): si se da un archivo con un access token real del usuario de prueba
(infra/pruebas/token_prueba.py), se agregan fases AUTENTICADAS: ahí sí corre la Lambda de
GET /me (unas 900 invocaciones, costo despreciable). Así se ve si el throttling cuenta solo las
solicitudes que pasan el authorizer. El token nunca se escribe en la evidencia.

Uso: python3 saturacion.py https://<api>/v1 carpeta-de-salida [archivo-con-token]
"""
from __future__ import annotations

import collections
import concurrent.futures as cf
import http.client
import json
import ssl
import sys
import threading
import time
import urllib.parse
from datetime import datetime, timezone

UA = "qwallet-prueba-saturacion/1.0 (HAL-16)"


TOKEN = ""


def pedir(host: str, ruta: str, ctx: ssl.SSLContext) -> tuple[float, str]:
    """Una solicitud GET con conexión nueva. Devuelve (momento, código o error).
    En los 429 agrega el tipo de error de API Gateway (x-amzn-ErrorType) para saber quién limitó."""
    inicio = time.monotonic()
    try:
        c = http.client.HTTPSConnection(host, timeout=15, context=ctx)
        cab = {"User-Agent": UA, "Accept": "application/json"}
        if TOKEN:
            cab["Authorization"] = f"Bearer {TOKEN}"
        c.request("GET", ruta, headers=cab)
        r = c.getresponse()
        r.read()
        tipo = (r.getheader("x-amzn-ErrorType") or "").split(":")[0]
        c.close()
        return inicio, f"{r.status}" + (f" {tipo}" if r.status >= 429 and tipo else "")
    except Exception as e:  # noqa: BLE001 - se registra el tipo de error tal cual
        return inicio, type(e).__name__


def fase_simultanea(host: str, ruta: str, ctx: ssl.SSLContext, n: int) -> list[tuple[float, str]]:
    """n solicitudes que salen juntas (una barrera las suelta al mismo tiempo)."""
    barrera = threading.Barrier(n)

    def una(_: int) -> tuple[float, str]:
        barrera.wait()
        return pedir(host, ruta, ctx)

    with cf.ThreadPoolExecutor(max_workers=n) as ex:
        return list(ex.map(una, range(n)))


def fase_sostenida(host: str, ruta: str, ctx: ssl.SSLContext, rps: int, segundos: int) -> list[tuple[float, str]]:
    """rps solicitudes por segundo, repartidas parejo, durante 'segundos'."""
    resultados: list[cf.Future] = []
    intervalo = 1.0 / rps
    with cf.ThreadPoolExecutor(max_workers=min(200, rps * 3)) as ex:
        t0 = time.monotonic()
        for i in range(rps * segundos):
            espera = t0 + i * intervalo - time.monotonic()
            if espera > 0:
                time.sleep(espera)
            resultados.append(ex.submit(pedir, host, ruta, ctx))
        return [f.result() for f in resultados]


def resumir(nombre: str, descripcion: str, datos: list[tuple[float, str]]) -> dict:
    conteo = collections.Counter(c for _, c in datos)
    t0 = min(t for t, _ in datos)
    por_segundo: dict[int, collections.Counter] = collections.defaultdict(collections.Counter)
    for t, c in datos:
        por_segundo[int(t - t0)][c] += 1
    return {
        "fase": nombre,
        "descripcion": descripcion,
        "total": len(datos),
        "codigos": dict(sorted(conteo.items())),
        "con_429": sum(v for k, v in conteo.items() if k.startswith("429")),
        "por_segundo": {s: dict(v) for s, v in sorted(por_segundo.items())},
    }


def main() -> int:
    global TOKEN
    api, salida = sys.argv[1].rstrip("/"), sys.argv[2]
    archivo_token = sys.argv[3] if len(sys.argv) > 3 else ""
    u = urllib.parse.urlparse(api)
    host, ruta = u.netloc, f"{u.path}/me"
    ctx = ssl.create_default_context()
    fecha = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    fases = [
        ("F1", "40 simultáneas (repite C09 del bloque 5)", lambda: fase_simultanea(host, ruta, ctx, 40)),
        ("F2", "10 por segundo durante 30 s (justo en el límite)", lambda: fase_sostenida(host, ruta, ctx, 10, 30)),
        ("F3", "30 por segundo durante 30 s (3 veces el límite)", lambda: fase_sostenida(host, ruta, ctx, 30, 30)),
        ("F4", "60 por segundo durante 20 s (6 veces el límite)", lambda: fase_sostenida(host, ruta, ctx, 60, 20)),
        ("F5", "100 simultáneas (5 veces la ráfaga)", lambda: fase_simultanea(host, ruta, ctx, 100)),
    ]
    if archivo_token:
        fases += [
            ("A1", "CON TOKEN: 40 simultáneas", lambda: fase_simultanea(host, ruta, ctx, 40)),
            ("A2", "CON TOKEN: 30 por segundo durante 20 s (3 veces el límite)", lambda: fase_sostenida(host, ruta, ctx, 30, 20)),
            ("A3", "CON TOKEN: 100 simultáneas (5 veces la ráfaga)", lambda: fase_simultanea(host, ruta, ctx, 100)),
        ]
    resumen = []
    for nombre, desc, correr in fases:
        if nombre.startswith("A") and not TOKEN:
            with open(archivo_token, encoding="utf-8") as f:
                TOKEN = f.read().strip()
        print(f"{nombre}: {desc}", flush=True)
        r = resumir(nombre, desc, correr())
        print(f"   {r['codigos']}", flush=True)
        resumen.append(r)
        time.sleep(15)  # deja que el cubo de fichas se llene de nuevo entre fases

    total = sum(r["total"] for r in resumen)
    total_429 = sum(r["con_429"] for r in resumen)
    with open(f"{salida}/EVD-7-05_saturacion.json", "w", encoding="utf-8") as f:
        json.dump({"fecha": fecha, "endpoint": f"GET {u.path}/me sin token", "fases": resumen}, f, indent=1)

    lineas = [
        "EVD-7-05 HAL-16: prueba de saturación del throttling de API Gateway (CTRL-05, CA-06)",
        f"Fecha: {fecha}",
        f"Objetivo: GET {u.path}/me. Fases F sin token (el authorizer de Cognito responde 401; no corre ninguna Lambda).",
        "Fases A (si están): con un access token real del usuario de prueba (PKCE + MFA); responde la Lambda.",
        "Límite configurado en la etapa v1 (aws_api_gateway_method_settings, */*): ráfaga 20, 10 por segundo.",
        "Prueba de carga acotada (no inundación): pausas de 15 s entre fases.",
        "",
        f"{'Fase':<5}{'Solicitudes':>12}{'429':>7}   Códigos             Descripción",
    ]
    for r in resumen:
        codigos = ", ".join(f"{k}: {v}" for k, v in r["codigos"].items())
        lineas.append(f"{r['fase']:<5}{r['total']:>12}{r['con_429']:>7}   {codigos:<20}{r['descripcion']}")
    lineas += ["", f"Total: {total} solicitudes, {total_429} con 429.", ""]
    for r in resumen:
        if r["fase"] in ("F4", "A2"):
            lineas.append(f"{r['fase']} segundo a segundo (códigos por segundo desde el inicio de la fase):")
            for s, c in r["por_segundo"].items():
                lineas.append(f"   s{s:>3}: " + ", ".join(f"{k}={v}" for k, v in sorted(c.items())))
            lineas.append("")
    sin = sum(r["con_429"] for r in resumen if r["fase"].startswith("F"))
    con = sum(r["con_429"] for r in resumen if r["fase"].startswith("A"))
    hay_a = any(r["fase"].startswith("A") for r in resumen)
    lineas.append(f"Sin token: {sin} respuestas 429." + (f" Con token: {con} respuestas 429." if hay_a else ""))
    if hay_a and con > 0 and sin == 0:
        lineas.append("Resultado: el throttling SÍ limita las solicitudes autenticadas; las que rechaza el authorizer")
        lineas.append("(401) no cuentan para el límite. HAL-16 se explica y se cierra; el freno para tráfico sin")
        lineas.append("token es el WAF con regla de tasa (RSK-11).")
    elif total_429 > 0:
        lineas.append("Resultado: el throttling SÍ responde 429 cuando la carga pasa el límite.")
    else:
        lineas.append("Resultado: ningún 429 en ninguna fase. HAL-16 sigue abierto (ver análisis).")
    texto = "\n".join(lineas) + "\n"
    with open(f"{salida}/EVD-7-05_saturacion.txt", "w", encoding="utf-8") as f:
        f.write(texto)
    print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
