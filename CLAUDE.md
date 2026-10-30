# CLAUDE.md — Q-Wallet

Proyecto final de Seguridad en Aplicaciones (UMG). Desde el 28-oct-2026 Daniel lleva el resto del proyecto solo, con Claude haciendo el trabajo y Daniel tomando decisiones.

## Arranque (en este orden, sin leer más de lo necesario)
1. `docs/ESTADO.md` — una página: qué está hecho, qué sigue, decisiones pendientes. **Siempre primero.**
2. Solo lo que pida el bloque en curso: la sección puntual de `docs/CONTEXTO.md` (fuente de verdad de decisiones, stack, versiones e IDs), `docs/PLAN_FASES.md` o el código.
3. `docs/BITACORA.md` solo si hace falta el historial (entradas nuevas arriba).
4. Lo que pide el catedrático: `docs/enunciado/README.md` (estructura del informe y ponderación); el detalle de cada fase en `docs/enunciado/ENUNCIADO.md`. Leer solo la parte que toca.

## Forma de trabajo
- **Un bloque por chat.** Daniel abre un chat con "Q-Wallet: sigue con el bloque X". Claude trabaja de corrido hasta terminar el bloque, sin pedir confirmaciones intermedias, salvo decisiones que solo Daniel puede tomar (se agrupan y se preguntan con opción múltiple).
- **Claude hace las ramas, los commits, el push y el PR** (con `gh api repos/dbarrios95/q-wallet/pulls ...`; `gh pr create` no funciona en estas sesiones). Daniel solo revisa y da clic en "Merge". `main` está protegida: nunca commits directos a `main`, nunca `push --force`, nunca `npm audit fix --force`.
- **Al cerrar cada bloque**, en el mismo PR: reescribir `docs/ESTADO.md`, actualizar CONTEXTO sección 11 y agregar una entrada en BITÁCORA. Daniel no tiene que subir archivos ni hacer commits.
- Las evidencias de AWS se generan en GitHub Actions (despliegue con OIDC, pruebas y escaneos) y Claude las lee con `gh`. Solo se piden capturas de consola cuando la rúbrica lo exige.
- El Word se arma **una vez por entrega**, al final, con los scripts de `scripts/`.

## Regla de borrado (pedida por Daniel, 28-oct-2026)
**Claude no borra nada sin preguntar.** Antes de eliminar o sobrescribir de forma irreversible cualquier cosa (archivos, carpetas, ramas, PR, tags, recursos de AWS, `terraform destroy`, reemplazos forzados en el plan de Terraform, tablas o datos):
1. Pregunta a Daniel qué se borra y **por qué**, con la justificación concreta.
2. Si Daniel aprueba, primero hace **respaldo**: archivos a `docs/_respaldo/AAAA-MM-DD/` o una rama `respaldo/<nombre>`; datos de AWS con exportación o snapshot cuando aplique.
3. Lo anota en BITÁCORA (qué, por qué, dónde quedó el respaldo).
- Editar un archivo versionado en git no es borrar (queda en el historial). Borrar archivos versionados sí requiere el paso 1.
- El flujo de despliegue debe fallar si el plan de Terraform trae destrucciones o reemplazos, hasta que Daniel los apruebe.

## Reglas de contenido
- Responde en español de Guatemala, breve y directo. Si algo está mal planteado, dilo claro.
- Si Daniel tiene que hacer algo a mano: está en **Windows con PowerShell 5.1**; dar comandos exactos, en orden, y el resultado esperado.
- Versiones exactas de CONTEXTO sección 3.1. Las reglas de código de `GEMINI.md` aplican igual.
- Nunca inventar fuentes ni cifras. Lo no verificable se marca `[VERIFICAR]`.
- El repo es público: en capturas y logs tapar número de cuenta AWS, ARN, correos y tokens.
- Costos: presupuesto de US$5. Prohibido RDS, NAT Gateway, EC2 encendido o EKS. El WAF se enciende solo para pruebas y capturas.
- Formato del Word: CONTEXTO sección 9 (Arial 12, interlineado 1.5).

## Regla de escritura
No usar el signo de sección (Unicode U+00A7) en ningún archivo, texto, código ni respuesta. Escribir "sección" (ejemplo: "CONTEXTO, sección 11").
