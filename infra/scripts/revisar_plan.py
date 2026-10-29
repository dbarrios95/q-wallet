"""Detiene el despliegue si el plan de Terraform destruye o reemplaza recursos.

Uso: python revisar_plan.py plan.json destrucciones_aprobadas.txt
Sale con código 1 si hay destrucciones o reemplazos no aprobados.
Regla de borrado de CLAUDE.md: nada se borra sin aprobación de Daniel.
"""
import fnmatch
import json
import os
import sys


def aprobadas(ruta):
    with open(ruta, encoding="utf-8") as f:
        return [l.split("#")[0].strip() for l in f if l.split("#")[0].strip()]


def main():
    plan_path, lista_path = sys.argv[1], sys.argv[2]
    with open(plan_path, encoding="utf-8") as f:
        plan = json.load(f)
    permitidas = aprobadas(lista_path)

    bloqueadas, permitidas_vistas, resumen = [], [], {"create": 0, "update": 0, "delete": 0}
    for cambio in plan.get("resource_changes", []):
        acciones = cambio["change"]["actions"]
        for a in ("create", "update", "delete"):
            if a in acciones:
                resumen[a] += 1
        if "delete" not in acciones:
            continue
        tipo = "reemplazo" if "create" in acciones else "destrucción"
        direccion = cambio["address"]
        if any(fnmatch.fnmatch(direccion, p) for p in permitidas):
            permitidas_vistas.append(f"{tipo}: {direccion}")
        else:
            bloqueadas.append(f"{tipo}: {direccion}")

    lineas = [
        "## Revisión del plan de Terraform",
        f"Crear: {resumen['create']} · Modificar: {resumen['update']} · Destruir o reemplazar: {resumen['delete']}",
    ]
    if permitidas_vistas:
        lineas.append("\nDestrucciones aprobadas en `infra/destrucciones_aprobadas.txt`:")
        lineas += [f"- {x}" for x in permitidas_vistas]
    if bloqueadas:
        lineas.append("\n**Bloqueado:** el plan destruye o reemplaza recursos sin aprobación:")
        lineas += [f"- {x}" for x in bloqueadas]
        lineas.append("\nSi el cambio es correcto, agregar la dirección a `infra/destrucciones_aprobadas.txt` en un PR, con el motivo.")
    texto = "\n".join(lineas)
    print(texto)
    resumen_gh = os.environ.get("GITHUB_STEP_SUMMARY")
    if resumen_gh:
        with open(resumen_gh, "a", encoding="utf-8") as f:
            f.write(texto + "\n")
    sys.exit(1 if bloqueadas else 0)


if __name__ == "__main__":
    main()
