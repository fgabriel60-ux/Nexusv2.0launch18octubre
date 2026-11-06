"""Reenvía el TRAMO B corregido y el LEEME actualizado.

Por qué: el paquete se mandó el 15 sep 19:56, pero el arreglo del tramo B (cejas
nuevas en 10_sonrisa_feliz, video B con el fundido a la sonrisa) y el LEEME
quedaron 20:23-20:28, DESPUÉS del envío. Lo que trae Carlos en el teléfono para
el tramo B es la versión vieja. El tramo A no cambió, no hace falta reenviarlo.
"""
import base64, json, time, urllib.request
from datetime import datetime
from pathlib import Path

AQUI = Path(__file__).resolve().parent
env = {}
for line in Path('/workspaces/visionagenciaIAV2.0/visionagenciaIAv2.0-cripto-sim-y-corte-catania/VisionagenciaIAv2.0-main/.env').read_text().splitlines():
    if '=' in line and not line.lstrip().startswith('#'):
        k, v = line.split('=', 1); env[k.strip()] = v.strip().strip('"').strip("'")
BASE = 'https://waapi.app/api/v1/instances/' + env['WAAPI_INSTANCE'] + '/client/action/'
CARLOS = '5216312470486@c.us'


def llamar(accion, body):
    for i in range(3):
        try:
            req = urllib.request.Request(BASE + accion, data=json.dumps(body).encode(),
                                         headers={'Authorization': 'Bearer ' + env['WAAPI_TOKEN'],
                                                  'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=300) as r:
                return (json.load(r).get('data') or {}).get('status')
        except Exception as e:
            err = str(e)[:80]; time.sleep(30 * (i + 1))
    return 'error ' + err


def media(archivo, caption, documento=True):
    return llamar('send-media', {'chatId': CARLOS, 'mediaName': archivo.name, 'asDocument': documento,
                                 'mediaBase64': base64.b64encode(archivo.read_bytes()).decode(),
                                 'mediaCaption': caption})


rec = {}
rec['aviso'] = llamar('send-message', {'chatId': CARLOS, 'message':
    '🤖 Claude · 🦷 IMPLANTE / GENJUTSU — corrección del TRAMO B.\n\n'
    'El paquete del 15 sep se mandó a las 19:56, pero el arreglo del tramo B quedó a las 20:27. '
    'O sea: el tramo B que traes en el teléfono es el viejo (cejas anteriores en el cuadro 10 y el '
    'video sin el fundido final a la sonrisa). Aquí va el bueno. El tramo A no cambió, ése sirve tal cual.'})
time.sleep(6)
rec['B_video'] = media(AQUI / 'TRAMO_B' / '00_VIDEO_TRAMO_B.mp4',
                       'Tramo B CORREGIDO · video de movimiento (desde 32.8 s se funde al cuadro 10 y se queda en la sonrisa)')
time.sleep(8)
rec['B_zip'] = media(AQUI / 'TRAMO_B_IMAGENES.zip',
                     'Tramo B CORREGIDO · imágenes 05 a 10, con el cuadro 10 de cejas nuevas')
time.sleep(6)
texto = (AQUI / 'PROMPT_TRAMO_B.txt').read_text()
rec['B_prompt'] = llamar('send-message', {'chatId': CARLOS,
    'message': 'Tramo B · PROMPT (no cambió, copia todo este mensaje):\n\n'
               + texto.split('(desde aquí) ===========')[1].split('===========')[0].strip()})
time.sleep(6)
rec['leeme'] = media(AQUI / 'LEEME_PASO_A_PASO.txt',
                     'Paso a paso actualizado (20:23) — también es más nuevo que el envío de las 19:56')

(AQUI / 'recibo_reenvio_tramoB.json').write_text(json.dumps(
    {'motivo': 'tramo B y LEEME arreglados despues del envio original del 15 sep 19:56',
     'fecha': datetime.now().isoformat(timespec='seconds'), 'resultado': rec}, ensure_ascii=False, indent=1))
print(rec)
