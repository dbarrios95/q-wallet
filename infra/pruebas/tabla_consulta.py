"""Imprime el resultado de una consulta de Logs Insights como líneas de texto (siem.sh)."""
import json
import sys

filas = json.load(open(sys.argv[1], encoding="utf-8")).get("results", [])
if not filas:
    print("   (sin resultados)")
for fila in filas:
    print("   " + " | ".join(f"{c['field']}={c['value']}" for c in fila if not c["field"].startswith("@ptr")))
