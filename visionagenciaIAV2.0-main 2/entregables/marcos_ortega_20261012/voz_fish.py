"""Genera la voz en off de Ortega con Fish Audio (voz clonada) a partir de GUION_VOZ.txt."""
import json, os, sys, urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent
VOZ = sys.argv[1] if len(sys.argv) > 1 else '240304037b7a4207a4876c82280a84c4'  # Carlos Vision narracion
texto = ' '.join(l.strip() for l in (AQUI / 'GUION_VOZ.txt').read_text().splitlines()[4:8] if l.strip())
req = urllib.request.Request('https://api.fish.audio/v1/tts', method='POST',
                             data=json.dumps({'text': texto, 'format': 'mp3', 'reference_id': VOZ}).encode(),
                             headers={'Authorization': 'Bearer ' + os.environ['FISH_API_KEY'],
                                      'Content-Type': 'application/json', 'model': 's1'})
(AQUI / 'Ortega_voz.mp3').write_bytes(urllib.request.urlopen(req, timeout=300).read())
print(texto)
