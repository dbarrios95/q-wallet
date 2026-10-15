"""Riesgo inherente y residual proyectado de Q-Wallet desde el threat model (Threat Dragon).
Uso: python scripts/heatmap_riesgo.py docs/threat-model/T2_QWallet_ThreatModel.json [inh|res] [salida.svg]
- Inherente: P e I recalculados desde DREAD (CONTEXTO, sección 6) y comparados con la descripción.
- Residual: "Residual esperado P x I" del campo mitigation de cada amenaza.
Con "inh" genera EVD-2-05; con "res", EVD-2-07. PNG: cairosvg a escala 2.
15-oct-2026 (revisión de Paco): sin título incrustado (el rótulo APA va en el Word, Figuras 5 y 6)
y la escala se refiere a la sección 2.5.1 del informe, no a CONTEXTO.
"""
import json,re,math,sys,collections
m=json.load(open(sys.argv[1]))
mode=sys.argv[2] if len(sys.argv)>2 else None; out=sys.argv[3] if len(sys.argv)>3 else None
rows=[]
for d in m['detail']['diagrams']:
  for c in d['cells']:
    for t in (c.get('data',{}) or {}).get('threats',[]) or []:
      if not t['title'].startswith('AME-'): continue
      ds=t['description']; mi=t['mitigation']
      D,R,E,A,Di=map(int,re.search(r'DREAD D(\d+) R(\d+) E(\d+) A(\d+) Di(\d+)',ds).groups())
      P=math.ceil(((R+E+Di)/3)/2); I=math.ceil(((D+A)/2)/2)
      pi,ii=map(int,re.search(r'inherente P(\d) x I(\d)',ds).groups())
      pr,ir,sr=re.search(r'Residual esperado P(\d) x I(\d) = (\d+)',mi).groups()
      trat=re.search(r'Tratamiento (\w+)',mi).group(1)
      capa=re.search(r'Capa (\w+)',ds).group(1)
      ctrls=re.findall(r'CTRL-\d+',mi)
      rows.append(dict(ame=t['title'][:6],title=t['title'][7:],P=pi,I=ii,Pc=P,Ic=I,Pr=int(pr),Ir=int(ir),Sr=int(sr),trat=trat,capa=capa,ctrls=sorted(set(ctrls)),mit=mi,sev=t['severity'],score=t['score'],type=t['type']))
rows.sort(key=lambda r:r['ame'])
def lvl(s): return 'Bajo' if s<=4 else 'Medio' if s<=9 else 'Alto' if s<=14 else 'Crítico'
print(len(rows),'AME; dif P/I calculado vs texto:',sum((r['P'],r['I'])!=(r['Pc'],r['Ic']) for r in rows))
print('dif residual P*I vs texto:',sum(r['Pr']*r['Ir']!=r['Sr'] for r in rows))
print('inh',collections.Counter(lvl(r['P']*r['I']) for r in rows))
print('res',collections.Counter(lvl(r['Sr']) for r in rows))
print('trat',collections.Counter(r['trat'] for r in rows))
print('I cambia:',[r['ame'] for r in rows if r['Ir']!=r['I']])
print('P sube:',[r['ame'] for r in rows if r['Pr']>r['P']])
print('sin cambio:',[(r['ame'],r['P']*r['I']) for r in rows if r['Pr']==r['P'] and r['Ir']==r['I']])
print('sin CTRL:',[r['ame'] for r in rows if not r['ctrls']])
for r in rows:
  if lvl(r['Sr']) in('Alto',) or r['trat']!='Mitigar': print(r['ame'],r['title'],r['P'],r['I'],'->',r['Pr'],r['Ir'],r['trat'],'|',r['mit'])
grid=collections.Counter((r['Pr'],r['Ir']) for r in rows); print('celdas res',dict(grid))
if not mode: sys.exit(0)
F='font-family="Inter,Arial,sans-serif"'
def col(s): return '#10B981' if s<=4 else '#F59E0B' if s<=9 else '#F97316' if s<=14 else '#EF4444'
def lvl(s): return 'Bajo' if s<=4 else 'Medio' if s<=9 else 'Alto' if s<=14 else 'Crítico'
if mode=='inh':
  cells=collections.Counter((r['P'],r['I']) for r in rows)
  title='Mapa de calor de riesgo inherente (antes)'
  sub='Q-Wallet — 41 amenazas STRIDE sin controles. Cada celda indica cuántas amenazas tienen esa combinación Probabilidad x Impacto.'
else:
  cells=collections.Counter((r['Pr'],r['Ir']) for r in rows)
  title='Mapa de calor de riesgo residual proyectado (después)'
  sub='Q-Wallet — 41 amenazas con los controles previstos (CTRL-01 a CTRL-23). Proyección, no medición.'
lv=collections.Counter()
for (p,i),n in cells.items(): lv[lvl(p*i)]+=n
o=[f'<svg xmlns="http://www.w3.org/2000/svg" width="940" height="490" viewBox="0 76 940 490"><rect x="0" y="76" width="940" height="490" fill="#FFFFFF"/>',
f'<text x="385.0" y="92" {F} font-size="15" font-weight="700" fill="#0F172A" text-anchor="middle">Impacto →</text>',
f'<text x="78" y="335.0" {F} font-size="15" font-weight="700" fill="#0F172A" text-anchor="middle" transform="rotate(-90 78 335.0)">Probabilidad →</text>']
for i in range(1,6): o.append(f'<text x="{173+86*(i-1)+40:.1f}" y="112" {F} font-size="14" font-weight="600" fill="#64748B" text-anchor="middle">{i}</text>')
for p in range(5,0,-1):
  y=123+86*(5-p); cy=y+45
  o.append(f'<text x="152" y="{cy:.1f}" {F} font-size="14" font-weight="600" fill="#64748B" text-anchor="middle">{p}</text>')
  for i in range(1,6):
    x=173+86*(i-1); cx=x+40; n=cells.get((p,i),0); s=p*i
    if n:
      o.append(f'<rect x="{x}" y="{y}" width="80" height="80" rx="7" fill="{col(s)}" opacity="1" stroke="#FFFFFF" stroke-width="2"/>')
      o.append(f'<text x="{cx:.1f}" y="{y+42:.1f}" {F} font-size="26" font-weight="800" fill="#FFFFFF" text-anchor="middle">{n}</text>')
      o.append(f'<text x="{cx:.1f}" y="{y+62:.1f}" {F} font-size="10" font-weight="600" fill="#FFFFFF" text-anchor="middle" opacity="0.9">P{p}xI{i}={s}</text>')
    else:
      o.append(f'<rect x="{x}" y="{y}" width="80" height="80" rx="7" fill="{col(s)}" opacity="0.28" stroke="#FFFFFF" stroke-width="2"/>')
      o.append(f'<text x="{cx:.1f}" y="{cy:.1f}" {F} font-size="14" fill="#FFFFFF" text-anchor="middle" opacity="0.8">0</text>')
o.append(f'<text x="640" y="126" {F} font-size="15" font-weight="700" fill="#0B1F3A">Nivel de riesgo</text>')
inh=collections.Counter(lvl(r['P']*r['I']) for r in rows)
for k,(name,rng,c) in enumerate([('Crítico','15–25','#EF4444'),('Alto','10–14','#F97316'),('Medio','5–9','#F59E0B'),('Bajo','1–4','#10B981')]):
  y=140+42*k
  o.append(f'<rect x="640" y="{y}" width="26" height="26" rx="6" fill="{c}"/>')
  o.append(f'<text x="676" y="{y+19}" {F} font-size="14" font-weight="600" fill="#0F172A">{name} ({rng})</text>')
  extra='' if mode=='inh' else f' (antes: {inh[name]})'
  o.append(f'<text x="676" y="{y+36}" {F} font-size="12" fill="#64748B">{lv[name]} amenaza{'' if lv[name]==1 else 's'}{extra}</text>')
o.append(f'<text x="640" y="330" {F} font-size="11" fill="#64748B">Total: 41 amenazas</text>')
o.append(f'<text x="640" y="348" {F} font-size="11" fill="#64748B">Escala P×I de la</text>')
o.append(f'<text x="640" y="364" {F} font-size="11" fill="#64748B">sección 2.5.1.</text>')
if mode!='inh':
  for k,t in enumerate(['Fuente: campo "mitigation" de','cada amenaza en el threat model','(Residual esperado P x I).','Pendiente de verificación.']):
    o.append(f'<text x="640" y="{392+16*k}" {F} font-size="11" fill="#64748B">{t}</text>')
o.append('</svg>')
open(out,'w').write(''.join(o)); print(dict(lv))
