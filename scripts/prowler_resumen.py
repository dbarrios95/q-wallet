#!/usr/bin/env python3
"""Resumen de los hallazgos de Prowler para la evidencia EVD-3-09 (informe 3.6).

Lee los CSV que deja Prowler en un directorio y arma un resumen en texto: totales por
estado, fallos por severidad y los controles con fallo agrupados (check, severidad,
servicio y un recurso de ejemplo). No imprime secretos; el flujo tapa el número de cuenta
y los ARN después. Es tolerante a cambios de esquema entre versiones de Prowler: si no
encuentra las columnas esperadas, sale con error y el flujo adjunta la consola.

Uso: python3 scripts/prowler_resumen.py <directorio-con-csv>
"""
import csv
import glob
import os
import sys
from collections import Counter, defaultdict

ORDEN_SEV = {"critical": 0, "high": 1, "medium": 2, "low": 3, "informational": 4}


def columna(campos, *candidatas):
    bajo = {c.lower(): c for c in campos}
    for cand in candidatas:
        if cand in bajo:
            return bajo[cand]
    return None


def main(directorio):
    csvs = sorted(glob.glob(os.path.join(directorio, "*.csv")))
    if not csvs:
        print("No se encontraron CSV de Prowler.", file=sys.stderr)
        return 2

    filas = []
    campos = []
    for ruta in csvs:
        with open(ruta, newline="", encoding="utf-8", errors="replace") as f:
            muestra = f.read(4096)
            f.seek(0)
            delim = ";" if muestra.count(";") > muestra.count(",") else ","
            lector = csv.DictReader(f, delimiter=delim)
            campos = lector.fieldnames or []
            filas.extend(lector)

    c_estado = columna(campos, "status", "status_code", "result")
    c_sev = columna(campos, "severity")
    c_check = columna(campos, "check_id", "checkid")
    c_titulo = columna(campos, "check_title", "title", "check_title_id")
    c_serv = columna(campos, "service_name", "service")
    c_rec = columna(campos, "resource_uid", "resource_arn", "resource_id", "resource")
    c_reg = columna(campos, "region", "location")
    if not c_estado or not c_check:
        print(f"Esquema de CSV inesperado. Columnas: {campos}", file=sys.stderr)
        return 3

    def norm(v):
        return (v or "").strip().lower()

    total = len(filas)
    estados = Counter(norm(r.get(c_estado)) for r in filas)
    n_pass = estados.get("pass", 0)
    n_fail = estados.get("fail", 0)

    fallos = [r for r in filas if norm(r.get(c_estado)) == "fail"]
    sev_fail = Counter(norm(r.get(c_sev)) if c_sev else "desconocida" for r in fallos)

    por_check = defaultdict(lambda: {"n": 0, "sev": "", "serv": "", "titulo": "", "rec": "", "reg": ""})
    for r in fallos:
        k = r.get(c_check, "")
        d = por_check[k]
        d["n"] += 1
        d["sev"] = norm(r.get(c_sev)) if c_sev else ""
        d["serv"] = r.get(c_serv, "") if c_serv else ""
        d["titulo"] = (r.get(c_titulo, "") if c_titulo else "")[:70]
        if not d["rec"]:
            d["rec"] = (r.get(c_rec, "") if c_rec else "")[:80]
            d["reg"] = r.get(c_reg, "") if c_reg else ""

    print("EVD-3-09 Prowler: evaluación de la arquitectura cloud (informe 3.6)")
    print(f"Servicios revisados: apigateway, lambda, dynamodb, kms, cloudtrail, iam, s3, cognito, wafv2")
    print(f"Comprobaciones totales: {total}  |  PASS: {n_pass}  |  FAIL: {n_fail}")
    print()
    print("Fallos por severidad:")
    for sev in sorted(sev_fail, key=lambda s: ORDEN_SEV.get(s, 9)):
        print(f"   {sev:<14} {sev_fail[sev]}")
    print()
    if not fallos:
        print("Sin hallazgos con estado FAIL en los servicios revisados.")
        return 0

    print("Controles con fallo (agrupados; recurso de ejemplo, el ARN y la cuenta van tapados):")
    ordenados = sorted(por_check.items(), key=lambda kv: (ORDEN_SEV.get(kv[1]["sev"], 9), -kv[1]["n"]))
    for check, d in ordenados:
        print(f"   [{d['sev'] or 's/sev':<8}] {check}  (x{d['n']}, {d['serv']})")
        print(f"        {d['titulo']}")
        if d["rec"]:
            print(f"        ej: {d['rec']} {('(' + d['reg'] + ')') if d['reg'] else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "prowler-out"))
