#!/usr/bin/env python3
"""Compuerta de SAST: resume uno o más archivos SARIF y falla si hay hallazgos graves.

Grave = nivel "error" o "security-severity" >= 7.0 (escala CVSS que usan CodeQL y Semgrep).
Uso: python3 scripts/sarif_compuerta.py <herramienta> archivo.sarif [más.sarif ...]
"""
import json
import sys


def severidad(regla: dict) -> float:
    try:
        return float(regla.get("properties", {}).get("security-severity", 0))
    except (TypeError, ValueError):
        return 0.0


def main() -> int:
    herramienta, archivos = sys.argv[1], sys.argv[2:]
    total = graves = 0
    reglas_ejecutadas = 0
    for ruta in archivos:
        sarif = json.load(open(ruta, encoding="utf-8"))
        for corrida in sarif.get("runs", []):
            reglas = {}
            driver = corrida.get("tool", {}).get("driver", {})
            for r in driver.get("rules", []):
                reglas[r.get("id")] = r
            for ext in corrida.get("tool", {}).get("extensions", []):
                for r in ext.get("rules", []):
                    reglas[r.get("id")] = r
            reglas_ejecutadas += len(reglas)
            for res in corrida.get("results", []):
                total += 1
                regla = reglas.get(res.get("ruleId"), {})
                nivel = res.get("level") or regla.get("defaultConfiguration", {}).get("level", "warning")
                sev = severidad(regla)
                es_grave = nivel == "error" or sev >= 7.0
                graves += es_grave
                loc = res.get("locations", [{}])[0].get("physicalLocation", {})
                archivo = loc.get("artifactLocation", {}).get("uri", "?")
                linea = loc.get("region", {}).get("startLine", "?")
                marca = "GRAVE" if es_grave else "aviso"
                print(f"  [{marca}] {res.get('ruleId')} (nivel {nivel}, severidad {sev}) {archivo}:{linea}")
                print(f"          {res.get('message', {}).get('text', '')[:160]}")
    print(f"{herramienta}: {reglas_ejecutadas} reglas, {total} hallazgos, {graves} graves")
    print(f"Resultado: {'FALLA' if graves else 'PASA'}")
    return 1 if graves else 0


if __name__ == "__main__":
    sys.exit(main())
