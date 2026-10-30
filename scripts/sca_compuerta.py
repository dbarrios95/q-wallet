#!/usr/bin/env python3
"""Compuerta de SCA (CTRL-10): falla si `npm audit` reporta un aviso High o Critical
que no esté en la lista de excepciones aprobadas o cuya excepción ya venció.

Uso: python3 scripts/sca_compuerta.py audit.json excepciones-sca.json [AAAA-MM-DD]
Escribe un resumen legible en la salida estándar (evidencia EVD-3-04).
"""
import datetime
import json
import sys

GRAVES = {"high", "critical"}


def main() -> int:
    auditoria = json.load(open(sys.argv[1], encoding="utf-8"))
    excepciones = {e["aviso"]: e for e in json.load(open(sys.argv[2], encoding="utf-8"))["excepciones"]}
    hoy = sys.argv[3] if len(sys.argv) > 3 else datetime.date.today().isoformat()

    avisos = {}
    for paquete, v in auditoria.get("vulnerabilities", {}).items():
        for via in v.get("via", []):
            if isinstance(via, dict):
                ghsa = via.get("url", "").rsplit("/", 1)[-1]
                a = avisos.setdefault(ghsa, {"paquete": via.get("name", paquete), "severidad": via.get("severity"), "titulo": via.get("title", ""), "rango": via.get("range", ""), "directa": False})
                a["directa"] = a["directa"] or bool(v.get("isDirect")) and paquete == via.get("name", paquete)

    conteo = auditoria.get("metadata", {}).get("vulnerabilities", {})
    print(f"npm audit: {conteo}")
    print(f"Avisos distintos: {len(avisos)}")
    bloqueantes = 0
    for ghsa, a in sorted(avisos.items(), key=lambda x: (x[1]["severidad"] not in GRAVES, x[0])):
        estado = "informativo"
        if a["severidad"] in GRAVES:
            e = excepciones.get(ghsa)
            if e is None:
                estado = "BLOQUEA (sin excepción)"
                bloqueantes += 1
            elif e.get("soloIndirecta") and a["directa"]:
                estado = "BLOQUEA (la excepción es solo para la copia indirecta y aparece como dependencia directa)"
                bloqueantes += 1
            elif e["revisarAntesDe"] < hoy:
                estado = f"BLOQUEA (excepción vencida el {e['revisarAntesDe']})"
                bloqueantes += 1
            else:
                estado = f"aceptado hasta {e['revisarAntesDe']}"
        print(f"  [{a['severidad']:8}] {ghsa} {a['paquete']} {a['rango']} -> {estado}")
        print(f"             {a['titulo'][:100]}")
    for ghsa in excepciones:
        if ghsa not in avisos:
            print(f"  Excepción sin uso (ya se puede quitar): {ghsa}")
    print(f"Resultado: {'FALLA' if bloqueantes else 'PASA'} ({bloqueantes} aviso(s) High/Critical sin excepción vigente)")
    return 1 if bloqueantes else 0


if __name__ == "__main__":
    sys.exit(main())
