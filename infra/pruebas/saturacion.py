#!/usr/bin/env python3
"""HAL-16: prueba de saturación más larga del throttling de API Gateway (CTRL-05, CA-06).

La etapa v1 tiene throttling por método: ráfaga 20 y 10 solicitudes por segundo
(infra/apigateway.tf). En el bloque 5, 40 solicitudes simultáneas con curl no
devolvieron ningún 429 (HAL-16). Esta prueba repite eso y agrega fases sostenidas.

Es una prueba de carga acotada contra la API propia, no una inundación: unas 2 500
solicitudes en total, nunca más de 60 por segundo, sin token (el authorizer responde
401, así que no corre ninguna Lambda ni se toca DynamoDB). Solo usa la biblioteca
estándar de Python.

Uso: python3 saturacion.py https://<api>/v1 carpeta-de-salida
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


def pedir(host: str, ruta: str, ctx: ssl.SSLContext) -> tuple[float, str]:
    """Una solicitud GET con conexión nueva. Devuelve (momento, código o error)."""
    inicio = time.monotonic()
    try:
        c = http.client.HTTPSConnection(host, timeout=15, context=ctx)
        c.request("GET", ruta, headers={"User-Agent": UA, "Accept": "application/json"})
        r = c.getresponse()
        r.read()
        c.close()
        return inicio, str(r.status)
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
        "con_429": conteo.get("429", 0),
        "por_segundo": {s: dict(v) for s, v in sorted(por_segundo.items())},
    }


def main() -> int:
    api, salida = sys.argv[1].rstrip("/"), sys.argv[2]
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
    resumen = []
    for nombre, desc, correr in fases:
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
        f"Objetivo: GET {u.path}/me sin token (el authorizer de Cognito responde 401; no corre ninguna Lambda).",
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
        if r["fase"] in ("F3", "F4"):
            lineas.append(f"{r['fase']} segundo a segundo (códigos por segundo desde el inicio de la fase):")
            for s, c in r["por_segundo"].items():
                lineas.append(f"   s{s:>3}: " + ", ".join(f"{k}={v}" for k, v in sorted(c.items())))
            lineas.append("")
    if total_429 > 0:
        lineas.append("Resultado: el throttling SÍ responde 429 cuando la carga pasa el límite. HAL-16 se cierra.")
    else:
        lineas.append("Resultado: ningún 429 ni con carga sostenida sobre el límite. HAL-16 sigue abierto (ver análisis).")
    texto = "\n".join(lineas) + "\n"
    with open(f"{salida}/EVD-7-05_saturacion.txt", "w", encoding="utf-8") as f:
        f.write(texto)
    print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
