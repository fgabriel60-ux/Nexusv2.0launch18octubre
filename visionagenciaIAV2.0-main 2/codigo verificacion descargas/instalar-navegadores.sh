#!/bin/bash
echo "=== Prueba: escritura local en el Escritorio ==="
dd if=/dev/zero of=~/Desktop/TEST-local.bin bs=1m count=50 2>&1
if [ -f ~/Desktop/TEST-local.bin ]; then
  echo "OK: el Escritorio SI permite escribir archivos."
  rm -f ~/Desktop/TEST-local.bin
else
  echo "FALLO: el Escritorio tampoco permite escribir. Avisa a Claude con este resultado antes de seguir."
  exit 1
fi

echo
echo "=== Creando carpeta navegadores en el Escritorio ==="
mkdir -p ~/Desktop/navegadores-high-sierra
cd ~/Desktop/navegadores-high-sierra || exit 1

echo
echo "=== Descargando Firefox ESR 115.40 ==="
curl -w "HTTP_CODE=%{http_code} BYTES=%{size_download}\n" --max-time 300 -o Firefox-115.40.0esr.dmg "https://ftp.mozilla.org/pub/firefox/releases/115.40.0esr/mac/en-US/Firefox%20115.40.0esr.dmg"

echo
echo "=== Descargando Pale Moon 34.3.2 ==="
curl -L -w "HTTP_CODE=%{http_code} BYTES=%{size_download}\n" --max-time 300 -o PaleMoon-34.3.2.intel64.dmg "https://www.palemoon.org/download.php?mirror=us&bits=64&type=macintel"

echo
echo "=== Descargando Chromium-legacy 124.0.6367.207.1 ==="
curl -L -w "HTTP_CODE=%{http_code} BYTES=%{size_download}\n" --max-time 300 -o Chromium-legacy-124.0.6367.207.1.zip "https://github.com/blueboxd/chromium-legacy/releases/download/stable/124.0.6367.207.1.zip"

echo
echo "=== Resultado final: deberian pesar decenas/cientos de MB cada uno ==="
ls -lh ~/Desktop/navegadores-high-sierra/

echo
echo "=== FIN ==="
