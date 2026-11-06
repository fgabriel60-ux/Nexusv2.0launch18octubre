"""Voz en off genérica (sin clonar) con Fish Audio, en partes para sincronizar con las escenas."""
import json, urllib.request
from pathlib import Path
AQUI = Path(__file__).resolve().parent
LLAVE = [l.split('=', 1)[1].strip().strip('"\'') for l in open('/workspaces/Nexusv2.0launch18octubre/.env') if l.startswith('FISH_API_KEY=')][0]
PARTES = {
    'V1': '¿Sigues llevando las cuentas de tu tienda en una libreta?',
    'V2': 'Con Anegocios tienes tu punto de venta completo: impresora de tickets y lector de códigos, todo por tres mil quinientos pesos.',
    'V3': 'Incluye un año de software, instalación, capacitación y soporte. Y pagas hasta que esté funcionando.',
    'V4': 'Escríbenos por WhatsApp.',
}
for k, t in PARTES.items():
    r = urllib.request.Request('https://api.fish.audio/v1/tts', method='POST',
        data=json.dumps({'text': t, 'format': 'wav', 'prosody': {'speed': 1.05}}).encode(),
        headers={'Authorization': 'Bearer ' + LLAVE, 'Content-Type': 'application/json', 'model': 's2-pro'})
    (AQUI / 'voz' / f'{k}.wav').write_bytes(urllib.request.urlopen(r, timeout=300).read()); print(k, 'ok')
