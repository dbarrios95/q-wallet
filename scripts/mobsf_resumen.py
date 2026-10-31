#!/usr/bin/env python3
"""EVD-3-07: analiza el APK con MobSF (contenedor local) por su API REST y resume.

Uso: python3 scripts/mobsf_resumen.py app-release.apk salida.txt [http://localhost:8000]
Necesita la variable MOBSF_API_KEY (la misma que recibe el contenedor).
Solo biblioteca estándar de Python.
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request
import uuid

APK, SALIDA = sys.argv[1], sys.argv[2]
BASE = sys.argv[3] if len(sys.argv) > 3 else "http://localhost:8000"
CLAVE = os.environ["MOBSF_API_KEY"]


def pedir(ruta, datos=None, archivo=None, timeout=900):
    cab = {"Authorization": CLAVE}
    if archivo:
        frontera = uuid.uuid4().hex
        with open(archivo, "rb") as f:
            contenido = f.read()
        cuerpo = (
            f"--{frontera}\r\nContent-Disposition: form-data; name=\"file\"; "
            f"filename=\"{os.path.basename(archivo)}\"\r\nContent-Type: application/octet-stream\r\n\r\n"
        ).encode() + contenido + f"\r\n--{frontera}--\r\n".encode()
        cab["Content-Type"] = f"multipart/form-data; boundary={frontera}"
    else:
        cuerpo = urllib.parse.urlencode(datos or {}).encode()
        cab["Content-Type"] = "application/x-www-form-urlencoded"
    req = urllib.request.Request(BASE + ruta, data=cuerpo, headers=cab, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


for _ in range(60):  # espera a que el contenedor responda
    try:
        urllib.request.urlopen(BASE + "/api_docs", timeout=5)
        break
    except Exception:
        time.sleep(5)

subida = pedir("/api/v1/upload", archivo=APK)
h = subida["hash"]
pedir("/api/v1/scan", {"hash": h})
tarjeta = pedir("/api/v1/scorecard", {"hash": h})
informe = pedir("/api/v1/report_json", {"hash": h})

lineas = [
    "EVD-3-07 MobSF 4.5.3: análisis estático del APK de producción",
    f"Fecha: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}",
    f"App: {informe.get('app_name')} · paquete {informe.get('package_name')} · "
    f"versión {informe.get('version_name')} · minSdk {informe.get('min_sdk')} · targetSdk {informe.get('target_sdk')}",
    "",
    f"Puntaje de seguridad de MobSF: {tarjeta.get('security_score')}/100",
    "Hallazgos por nivel: " + ", ".join(
        f"{k} {len(tarjeta.get(k, []))}" for k in ("high", "warning", "info", "secure", "hotspot")
    ),
    "",
]
for nivel in ("high", "warning"):
    elementos = tarjeta.get(nivel, [])
    lineas.append(f"{nivel.upper()} ({len(elementos)}):")
    for e in elementos:
        titulo = e.get("title", "") if isinstance(e, dict) else str(e)
        seccion = e.get("section", "") if isinstance(e, dict) else ""
        lineas.append(f"   - [{seccion}] {titulo}")
    lineas.append("")

# Solo el conteo: MobSF lista cadenas largas (tablas hexadecimales, símbolos de C++) que no son
# secretos y que harían saltar a gitleaks si se copian. La búsqueda real de secretos es EVD-4-11.
secretos = informe.get("secrets") or []
lineas.append(f"Cadenas que MobSF marca como posibles secretos: {len(secretos)} "
              "(tablas y símbolos de librerías; ver EVD-4-11 para la búsqueda con gitleaks)")
lineas.append("")
lineas.append("Dominios que contacta la app (análisis de cadenas):")
dominios = informe.get("domains") or {}
lineas.extend([f"   - {d}" for d in list(dominios)[:20]] or ["   (ninguno)"])

with open(SALIDA, "w", encoding="utf-8") as f:
    f.write("\n".join(lineas) + "\n")
with open(os.path.splitext(SALIDA)[0] + ".json", "w", encoding="utf-8") as f:
    json.dump({"scorecard": tarjeta}, f, ensure_ascii=False, indent=1)
print("\n".join(lineas))
