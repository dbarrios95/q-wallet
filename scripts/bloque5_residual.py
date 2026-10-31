"""Riesgo residual VERIFICADO de Q-Wallet (bloque 5, sección 5.6).

Uso:
    python scripts/bloque5_residual.py                 # resumen en consola
    python scripts/bloque5_residual.py figura          # EVD-5-09 (antes y después, lado a lado)

Entradas:
  - docs/threat-model/T2_QWallet_ThreatModel.json: riesgo inherente (P e I desde DREAD) y
    residual proyectado ("Residual esperado P x I" del campo mitigation), igual que heatmap_riesgo.py.
  - docs/threat-model/verificacion_bloque5.json: estado de la verificación de cada amenaza.
Regla (también en el JSON): prueba y configuración conservan el residual proyectado; parcial
sube un nivel de probabilidad sin pasar del inherente; aceptado conserva el proyectado; un
"residual" explícito reemplaza el cálculo cuando la amenaza se re-evaluó (AME-31, AME-41).
"""
import collections
import json
import math
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
MODELO = RAIZ / "docs/threat-model/T2_QWallet_ThreatModel.json"
VERIF = RAIZ / "docs/threat-model/verificacion_bloque5.json"
SALIDA = RAIZ / "docs/evidencias/EVD-5-09_heatmap_antes_despues"


def nivel(s):
    return "Bajo" if s <= 4 else "Medio" if s <= 9 else "Alto" if s <= 14 else "Crítico"


def color(s):
    return "#10B981" if s <= 4 else "#F59E0B" if s <= 9 else "#F97316" if s <= 14 else "#EF4444"


def cargar():
    m = json.load(open(MODELO, encoding="utf-8"))
    v = json.load(open(VERIF, encoding="utf-8"))["amenazas"]
    filas = []
    for d in m["detail"]["diagrams"]:
        for c in d["cells"]:
            for t in (c.get("data", {}) or {}).get("threats", []) or []:
                if not t["title"].startswith("AME-"):
                    continue
                ds, mi = t["description"], t["mitigation"]
                D, R, E, A, Di = map(int, re.search(r"DREAD D(\d+) R(\d+) E(\d+) A(\d+) Di(\d+)", ds).groups())
                P, I = math.ceil(((R + E + Di) / 3) / 2), math.ceil(((D + A) / 2) / 2)
                pr, ir, _ = map(int, re.search(r"Residual esperado P(\d) x I(\d) = (\d+)", mi).groups())
                ame = t["title"][:6]
                ver = v[ame]
                estado = ver["estado"]
                if "residual" in ver:
                    pv, iv = ver["residual"]
                elif estado == "parcial":
                    pv, iv = min(pr + 1, P), ir
                else:
                    pv, iv = pr, ir
                trat = ver.get("tratamiento") or re.search(r"Tratamiento (\w+)", mi).group(1)
                filas.append(dict(
                    ame=ame, rsk="RSK-" + ame[4:], titulo=t["title"][7:], P=P, I=I, Pr=pr, Ir=ir, Pv=pv, Iv=iv,
                    estado=estado, trat=trat, evid=ver["evidencias"], nota=ver["nota"],
                    capa=re.search(r"Capa (\w+)", ds).group(1),
                    ctrls=sorted(set(re.findall(r"CTRL-\d+", mi)), key=lambda x: int(x[5:])),
                ))
    filas.sort(key=lambda f: f["ame"])
    assert len(filas) == 41, len(filas)
    return filas


def resumen(filas):
    cuenta = lambda clave: collections.Counter(nivel(f[clave[0]] * f[clave[1]]) for f in filas)
    return {
        "inherente": cuenta(("P", "I")),
        "proyectado": cuenta(("Pr", "Ir")),
        "verificado": cuenta(("Pv", "Iv")),
        "suma": (sum(f["P"] * f["I"] for f in filas), sum(f["Pr"] * f["Ir"] for f in filas),
                 sum(f["Pv"] * f["Iv"] for f in filas)),
        "estados": collections.Counter(f["estado"] for f in filas),
        "tratamiento": collections.Counter(f["trat"] for f in filas),
    }


F = 'font-family="Arial,Helvetica,sans-serif"'


def rejilla(o, x0, y0, celdas, titulo, subtitulo):
    lado, paso = 70, 76
    o.append(f'<text x="{x0 + 2.5 * paso:.0f}" y="{y0 - 52}" {F} font-size="17" font-weight="700" fill="#0B1F3A" text-anchor="middle">{titulo}</text>')
    o.append(f'<text x="{x0 + 2.5 * paso:.0f}" y="{y0 - 32}" {F} font-size="12" fill="#64748B" text-anchor="middle">{subtitulo}</text>')
    o.append(f'<text x="{x0 + 2.5 * paso:.0f}" y="{y0 - 10}" {F} font-size="12" font-weight="700" fill="#0F172A" text-anchor="middle">Impacto →</text>')
    for i in range(1, 6):
        o.append(f'<text x="{x0 + paso * (i - 1) + lado / 2:.0f}" y="{y0 + 5 * paso + 16}" {F} font-size="12" fill="#64748B" text-anchor="middle">{i}</text>')
    for p in range(5, 0, -1):
        y = y0 + paso * (5 - p)
        o.append(f'<text x="{x0 - 14}" y="{y + lado / 2 + 5:.0f}" {F} font-size="12" fill="#64748B" text-anchor="middle">{p}</text>')
        for i in range(1, 6):
            x = x0 + paso * (i - 1)
            n, s = celdas.get((p, i), 0), p * i
            op = 1 if n else 0.22
            o.append(f'<rect x="{x}" y="{y}" width="{lado}" height="{lado}" rx="6" fill="{color(s)}" opacity="{op}"/>')
            if n:
                o.append(f'<text x="{x + lado / 2:.0f}" y="{y + 38}" {F} font-size="22" font-weight="700" fill="#0F172A" text-anchor="middle">{n}</text>')
                o.append(f'<text x="{x + lado / 2:.0f}" y="{y + 56}" {F} font-size="9" fill="#0F172A" text-anchor="middle">{s}</text>')
    o.append(f'<text x="{x0 - 34}" y="{y0 + 2.5 * paso:.0f}" {F} font-size="12" font-weight="700" fill="#0F172A" text-anchor="middle" transform="rotate(-90 {x0 - 34} {y0 + 2.5 * paso:.0f})">Probabilidad →</text>')


def figura(filas):
    r = resumen(filas)
    antes = collections.Counter((f["P"], f["I"]) for f in filas)
    despues = collections.Counter((f["Pv"], f["Iv"]) for f in filas)
    o = ['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="560" viewBox="0 0 1000 560">',
         '<rect width="1000" height="560" fill="#FFFFFF"/>']
    rejilla(o, 70, 90, antes, "Antes: riesgo inherente", "41 amenazas sin controles (sección 2.5)")
    rejilla(o, 520, 90, despues, "Después: riesgo residual verificado", "con los controles desplegados y probados")
    y = 500
    x = 70
    for nom, rango in (("Crítico", "15–25"), ("Alto", "10–14"), ("Medio", "5–9"), ("Bajo", "1–4")):
        c = {"Crítico": "#EF4444", "Alto": "#F97316", "Medio": "#F59E0B", "Bajo": "#10B981"}[nom]
        o.append(f'<rect x="{x}" y="{y}" width="18" height="18" rx="4" fill="{c}"/>')
        o.append(f'<text x="{x + 26}" y="{y + 14}" {F} font-size="13" fill="#0F172A">{nom} ({rango}): '
                 f'{r["inherente"][nom]} → {r["verificado"][nom]}</text>')
        x += 225
    s0, _, s2 = r["suma"]
    o.append(f'<text x="70" y="545" {F} font-size="12" fill="#64748B">Cada celda: número de amenazas y P×I. '
             f'Suma de P×I de las 41 amenazas: {s0} antes, {s2} después ({round(100 * (s2 - s0) / s0)} %).</text>')
    o.append("</svg>")
    SALIDA.with_suffix(".svg").write_text("".join(o), encoding="utf-8")
    import cairosvg
    cairosvg.svg2png(url=str(SALIDA.with_suffix(".svg")), write_to=str(SALIDA.with_suffix(".png")), scale=2)
    print("Figura:", SALIDA.with_suffix(".png"))


if __name__ == "__main__":
    filas = cargar()
    r = resumen(filas)
    for k in ("inherente", "proyectado", "verificado"):
        print(k, {n: r[k][n] for n in ("Crítico", "Alto", "Medio", "Bajo")})
    print("suma P×I (inherente, proyectado, verificado):", r["suma"])
    print("estados:", dict(r["estados"]), "| tratamiento:", dict(r["tratamiento"]))
    for f in filas:
        if (f["Pv"], f["Iv"]) != (f["Pr"], f["Ir"]):
            print(f'  {f["ame"]} proyectado P{f["Pr"]}xI{f["Ir"]} -> verificado P{f["Pv"]}xI{f["Iv"]} ({f["estado"]})')
    if len(sys.argv) > 1 and sys.argv[1] == "figura":
        figura(filas)
