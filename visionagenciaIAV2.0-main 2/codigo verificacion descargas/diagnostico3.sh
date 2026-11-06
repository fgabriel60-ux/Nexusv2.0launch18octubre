#!/bin/bash
echo "=== Prueba aislada: descarga real de Firefox via Terminal ==="
curl -w "\nHTTP_CODE=%{http_code}\nBYTES_DESCARGADOS=%{size_download}\n" --max-time 30 -o ~/Downloads/TEST-firefox.dmg "https://ftp.mozilla.org/pub/firefox/releases/115.40.0esr/mac/en-US/Firefox%20115.40.0esr.dmg"

echo
echo "=== Prueba aislada: descarga real de Pale Moon via Terminal ==="
curl -L -w "\nHTTP_CODE=%{http_code}\nBYTES_DESCARGADOS=%{size_download}\n" --max-time 30 -o ~/Downloads/TEST-palemoon.dmg "https://www.palemoon.org/download.php?mirror=us&bits=64&type=macintel"

echo
echo "=== Archivos de prueba en Descargas (deben pesar decenas de MB si funciono) ==="
ls -lh ~/Downloads/TEST-*.dmg

echo
echo "=== FIN ==="
