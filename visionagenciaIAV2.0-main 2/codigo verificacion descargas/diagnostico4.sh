#!/bin/bash
echo "=== Prueba 1: escritura LOCAL pura (sin red, 50MB de ceros) ==="
dd if=/dev/zero of=~/Downloads/TEST-local.bin bs=1m count=50 2>&1
ls -lh ~/Downloads/TEST-local.bin
rm -f ~/Downloads/TEST-local.bin

echo
echo "=== Prueba 2: descargar un archivo de texto plano grande (no ejecutable) ==="
curl -w "\nHTTP_CODE=%{http_code}\nBYTES=%{size_download}\n" --max-time 30 -o ~/Downloads/TEST-texto.txt "https://ftp.mozilla.org/pub/firefox/releases/115.40.0esr/SHA512SUMS"
ls -lh ~/Downloads/TEST-texto.txt
rm -f ~/Downloads/TEST-texto.txt

echo
echo "=== Software de seguridad / control parental / MDM detectado ==="
ls /Library/LaunchDaemons/ /Library/LaunchAgents/ 2>/dev/null | grep -iE "screentime|parental|mdm|kandji|jamf|sophos|avast|mcafee|norton|bitdefender|malwarebytes|littlesnitch|crowdstrike"
echo "(si no aparece nada arriba, no se detecto ninguno de los nombres comunes)"

echo
echo "=== Screen Time / restricciones de contenido activas ==="
defaults read com.apple.familycontrols 2>/dev/null || echo "no hay configuracion de Screen Time visible para este usuario"

echo
echo "=== FIN ==="
