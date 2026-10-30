#!/usr/bin/env python3
"""Resume reportes JSON de Trivy (una imagen por archivo) y aplica la compuerta.

Compuerta (CTRL-10 / CTRL-11): falla si hay vulnerabilidades HIGH o CRITICAL que ya
tienen versión corregida publicada. Las que no tienen corrección se listan (informativas).
Uso: python3 scripts/trivy_resumen.py trivy-*.json
"""
import json
import sys
from collections import defaultdict

GRAVES = {"HIGH", "CRITICAL"}


def main() -> int:
    hallazgos = defaultdict(set)  # (severidad, paquete, instalada, corregida, id, destino) -> imágenes
    secretos = []
    conteo_imagen = {}
    for ruta in sys.argv[1:]:
        r = json.load(open(ruta, encoding="utf-8"))
        imagen = r.get("ArtifactName", ruta)
        conteo = defaultdict(int)
        for res in r.get("Results", []) or []:
            destino = res.get("Target", "?")
            for v in res.get("Vulnerabilities", []) or []:
                sev = v.get("Severity", "UNKNOWN")
                conteo[sev] += 1
                lugar = v.get("PkgPath") or destino
                clave = (sev, v.get("PkgName"), v.get("InstalledVersion"), v.get("FixedVersion") or "", v.get("VulnerabilityID"), lugar)
                hallazgos[clave].add(imagen)
            for s in res.get("Secrets", []) or []:
                secretos.append((imagen, destino, s.get("RuleID"), s.get("Severity")))
        conteo_imagen[imagen] = dict(conteo)

    print("Conteo por imagen (todas las severidades):")
    for img, c in conteo_imagen.items():
        print(f"  {img}: {c if c else 'sin vulnerabilidades'}")
    print(f"Secretos encontrados en las imágenes: {len(secretos)}")
    for s in secretos:
        print(f"  {s}")

    orden = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "UNKNOWN": 4}
    bloquean = 0
    print("\nVulnerabilidades distintas (severidad | paquete instalada -> corregida | id | dónde | imágenes):")
    for (sev, pkg, inst, fix, vid, destino), imgs in sorted(hallazgos.items(), key=lambda x: (orden.get(x[0][0], 9), x[0][1] or "")):
        grave = sev in GRAVES and fix
        bloquean += 1 if grave else 0
        marca = "BLOQUEA" if grave else ("sin corrección" if not fix else "informativo")
        print(f"  [{sev:8}] {pkg} {inst} -> {fix or '(sin corrección)'} | {vid} | {destino} | {len(imgs)} imagen(es) | {marca}")
    print(f"\nResultado de la compuerta: {'FALLA' if bloquean else 'PASA'} ({bloquean} vulnerabilidad(es) HIGH/CRITICAL con corrección disponible)")
    return 1 if bloquean else 0


if __name__ == "__main__":
    sys.exit(main())
