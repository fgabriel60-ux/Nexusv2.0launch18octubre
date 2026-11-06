#!/usr/bin/env bash
# PUENTE entre el Claude del codespace y el Claude de Modal (nexus2).
#
# El problema que resuelve: son DOS máquinas distintas. Lo que se escribe en el
# buzón del codespace NO llega solo al sandbox de Modal (ni al revés), porque el
# sandbox lee el volumen `nexus-workspace` de su cuenta. Antes del 3 nov 2026 los
# encargos se quedaban aquí sin que nexus2 los viera nunca.
#
#   ./herramientas/puente_modal.sh enviar    # codespace -> Modal (encargos)
#   ./herramientas/puente_modal.sh traer     # Modal -> codespace (reportes)
#   ./herramientas/puente_modal.sh ver       # qué hay de cada lado
#
# Cuenta: charlyfavela666 (3 nov 2026, Carlos mudó Claude y el gasto ahí).
set -euo pipefail

PERFIL="${MODAL_PROFILE:-charlyfavela666}"
VOL="nexus-workspace"
RAIZ="/workspaces/Nexusv2.0launch18octubre"
REMOTO="workspaces/Nexusv2.0launch18octubre"
cd "$RAIZ"
export MODAL_PROFILE="$PERFIL"

enviar() {
  echo "== Enviando encargos a Modal ($PERFIL)"
  # -f sobrescribe: el buzón es la fuente de verdad del codespace.
  for f in buzon/para_nexus2/*.md; do
    [ -e "$f" ] || continue
    modal volume put -f "$VOL" "$f" "$REMOTO/$f" >/dev/null && echo "  -> $(basename "$f")"
  done
  for f in AGENTS.md buzon/LEEME.md buzon/tomados.md; do
    [ -e "$f" ] || continue
    modal volume put -f "$VOL" "$f" "$REMOTO/$f" >/dev/null && echo "  -> $f"
  done
  echo "Listo. nexus2 ya puede leerlos en /vol/$REMOTO/buzon/para_nexus2/"
}

traer() {
  echo "== Trayendo reportes de Modal ($PERFIL)"
  tmp="$(mktemp -d)"
  if modal volume get "$VOL" "$REMOTO/buzon/para_nexus" "$tmp" >/dev/null 2>&1; then
    # Solo trae lo que no tengamos: nunca pisa un reporte local.
    cp -rn "$tmp/para_nexus/." buzon/para_nexus/ 2>/dev/null || true
    echo "  reportes nuevos en buzon/para_nexus/"
  else
    echo "  (todavía no hay buzon/para_nexus en el volumen)"
  fi
  rm -rf "$tmp"
}

ver() {
  echo "== Aquí (codespace): $(ls -1 buzon/para_nexus2/*.md 2>/dev/null | wc -l) encargos"
  ls -1t buzon/para_nexus2/*.md 2>/dev/null | head -3 | sed 's/^/   /'
  echo "== Allá (Modal $PERFIL):"
  modal volume ls "$VOL" "$REMOTO/buzon/para_nexus2" 2>/dev/null | tail -4 | sed 's/^/   /' \
    || echo "   (sin buzón todavía: corre 'enviar')"
}

case "${1:-ver}" in
  enviar) enviar ;;
  traer)  traer ;;
  ver)    ver ;;
  *) echo "Uso: $0 {enviar|traer|ver}"; exit 1 ;;
esac
