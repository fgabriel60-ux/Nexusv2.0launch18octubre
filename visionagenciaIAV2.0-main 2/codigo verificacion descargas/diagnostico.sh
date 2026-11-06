#!/bin/bash
echo "=== macOS version ==="; sw_vers

echo; echo "=== Fecha y hora del sistema (clave para que funcione HTTPS) ==="; date

echo; echo "=== Espacio libre en disco ==="; df -h /

echo; echo "=== Version de Safari instalada ==="; defaults read /Applications/Safari.app/Contents/Info CFBundleShortVersionString 2>/dev/null || echo "no se pudo leer"

echo; echo "=== Permisos de la carpeta Descargas ==="; ls -ld ~/Downloads

echo; echo "=== Conectividad basica (DNS + HTTPS) ==="; curl -sI --max-time 10 https://www.apple.com | head -5

echo; echo "=== Prueba de descarga: Firefox (Mozilla) ==="; curl -v --max-time 15 -o /dev/null "https://ftp.mozilla.org/pub/firefox/releases/115.40.0esr/mac/en-US/Firefox%20115.40.0esr.dmg" 2>&1 | tail -30

echo; echo "=== Prueba de descarga: Pale Moon ==="; curl -v --max-time 15 -o /dev/null "https://www.palemoon.org/download.php?mirror=us&bits=64&type=macintel" 2>&1 | tail -30

echo; echo "=== Prueba de descarga: GitHub (Chromium-legacy) ==="; curl -v --max-time 15 -o /dev/null "https://github.com/blueboxd/chromium-legacy/releases/download/stable/124.0.6367.207.1.zip" 2>&1 | tail -30

echo; echo "=== FIN DEL DIAGNOSTICO ==="
