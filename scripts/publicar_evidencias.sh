#!/usr/bin/env bash
# Publica las evidencias de un flujo de GitHub Actions (bloque 5).
# Uso: bash scripts/publicar_evidencias.sh <carpeta> "<título del issue>" <subcarpeta> [resultado]
#   1. Comentario en el issue "<título>" (lo crea si no existe) con los .txt de la carpeta.
#   2. Si el evento es un pull request, el mismo comentario en el PR.
#   3. Copia de la carpeta (.txt, .png, .json) a la rama evidencias-ci, en
#      <subcarpeta>/<fecha>_<run_id>/. Así Claude lee las imágenes con git, porque
#      los artefactos de Actions no se pueden descargar desde sus sesiones.
# Antes de publicar, reemplaza el número de cuenta de AWS ($CUENTA, si existe).
# Necesita GH_TOKEN y permisos contents: write, issues: write (y pull-requests: write).
set -uo pipefail

DIR="$1"
TITULO="$2"
SUB="$3"
RESULTADO="${4:-}"
REPO="${GITHUB_REPOSITORY}"
RUN_URL="${GITHUB_SERVER_URL}/${REPO}/actions/runs/${GITHUB_RUN_ID}"

if [ -n "${CUENTA:-}" ]; then
  find "$DIR" -type f \( -name '*.txt' -o -name '*.json' \) -exec sed -i "s/${CUENTA}/************/g" {} +
fi

RAMA="evidencias-ci"
DESTINO="${SUB}/$(date -u +%Y-%m-%d_%H%M)_${GITHUB_RUN_ID}"
{
  echo "## ${TITULO} ${RESULTADO:+· ${RESULTADO} }· commit ${GITHUB_SHA::7} · $(date -u '+%Y-%m-%d %H:%M UTC')"
  echo "Ejecución: ${RUN_URL}"
  echo "Archivos completos (incluye imágenes): rama \`${RAMA}\`, carpeta \`${DESTINO}\`"
  for f in "$DIR"/*.txt; do
    [ -f "$f" ] || continue
    echo; echo "<details><summary>$(basename "$f")</summary>"; echo; echo '```'
    tail -c 6000 "$f"; echo '```'; echo "</details>"
  done
} > /tmp/comentario.md
head -c 64000 /tmp/comentario.md > /tmp/c.md

n=$(gh issue list --repo "$REPO" --state open --search "\"${TITULO}\" in:title" --json number,title \
  --jq "map(select(.title == \"${TITULO}\"))[0].number")
if [ -z "$n" ] || [ "$n" = "null" ]; then
  n=$(gh issue create --repo "$REPO" --title "$TITULO" \
    --body "Resultados automáticos (sin número de cuenta, ARN ni correos)." | grep -o '[0-9]*$')
fi
gh issue comment "$n" --repo "$REPO" --body-file /tmp/c.md || echo "::warning::No se pudo comentar el issue"

if [ "${GITHUB_EVENT_NAME}" = "pull_request" ]; then
  pr=$(jq -r '.pull_request.number' "$GITHUB_EVENT_PATH")
  gh pr comment "$pr" --repo "$REPO" --body-file /tmp/c.md || echo "::warning::No se pudo comentar el PR"
fi

# Copia a la rama evidencias-ci (sin historial del proyecto: rama huérfana).
TMPR="$(mktemp -d)"
git -C "$TMPR" init -q
git -C "$TMPR" config user.name "github-actions[bot]"
git -C "$TMPR" config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git -C "$TMPR" remote add origin "https://x-access-token:${GH_TOKEN}@github.com/${REPO}.git"
if git -C "$TMPR" fetch -q --depth 1 origin "$RAMA" 2>/dev/null; then
  git -C "$TMPR" checkout -q -b "$RAMA" FETCH_HEAD
else
  git -C "$TMPR" checkout -q --orphan "$RAMA"
  printf '# Evidencias de CI\n\nRama generada por los flujos de GitHub Actions (bloque 5). No se hace merge a main.\n' > "$TMPR/README.md"
fi
mkdir -p "$TMPR/$DESTINO"
find "$DIR" -maxdepth 1 -type f \( -name '*.txt' -o -name '*.png' -o -name '*.json' \) -size -5M -exec cp {} "$TMPR/$DESTINO/" \;
git -C "$TMPR" add -A
git -C "$TMPR" commit -q -m "evidencias: ${SUB} ${GITHUB_RUN_ID}" || { echo "Sin cambios que publicar"; exit 0; }
for i in 1 2 3; do
  git -C "$TMPR" push -q origin "HEAD:${RAMA}" && { echo "Evidencias en ${RAMA}/${DESTINO}"; exit 0; }
  sleep $((i * 5))
  git -C "$TMPR" fetch -q --depth 1 origin "$RAMA" && git -C "$TMPR" rebase -q FETCH_HEAD
done
echo "::warning::No se pudo subir a la rama ${RAMA}"
