#!/bin/bash
echo "=== ACL detallada de Descargas ==="; ls -le ~/Downloads | head -5

echo; echo "=== Flags especiales del archivo (uchg, restricted, etc) ==="; ls -lO ~/Downloads

echo; echo "=== Preferencia de carpeta de descargas configurada en Safari ==="; defaults read com.apple.Safari DownloadsPath 2>/dev/null || echo "no configurada / valor por defecto"

echo; echo "=== Cuarentena / Gatekeeper status ==="; spctl --status

echo; echo "=== Espacio real disponible (por si el df -h de antes se veia raro) ==="; df -h ~/Downloads

echo; echo "=== FIN ==="
