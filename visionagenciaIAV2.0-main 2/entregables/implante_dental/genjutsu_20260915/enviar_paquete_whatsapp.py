"""Manda a Carlos (su WhatsApp) el paquete del implante para Genjutsu, cuando la cola de WhatsApp ya terminó
(los envíos grandes encimados daban 520/524). Uso: python3 enviar_paquete_whatsapp.py"""
import base64, json, subprocess, time, urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent
env = {}
for line in Path('/workspaces/visionagenciaIAV2.0/visionagenciaIAv2.0-cripto-sim-y-corte-catania/VisionagenciaIAv2.0-main/.env').read_text().splitlines():
    if '=' in line and not line.lstrip().startswith('#'):
        k, v = line.split('=', 1); env[k.strip()] = v.strip().strip('"').strip("'")
BASE = 'https://waapi.app/api/v1/instances/' + env['WAAPI_INSTANCE'] + '/client/action/'
CARLOS = '5216312470486@c.us'

while subprocess.run(['pgrep', '-f', 'cola_whatsapp.py|enviar_poco_a_poco.py'], capture_output=True).stdout.strip():
    time.sleep(20)


def llamar(accion, body):
    for i in range(3):
        try:
            req = urllib.request.Request(BASE + accion, data=json.dumps(body).encode(),
                                         headers={'Authorization': 'Bearer ' + env['WAAPI_TOKEN'], 'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=300) as r:
                return (json.load(r).get('data') or {}).get('status')
        except Exception as e:
            err = str(e)[:80]; time.sleep(30 * (i + 1))
    return 'error ' + err


def media(archivo, caption=None, documento=False):
    body = {'chatId': CARLOS, 'mediaBase64': base64.b64encode(archivo.read_bytes()).decode(), 'mediaName': archivo.name,
            'asDocument': documento}
    if caption:
        body['mediaCaption'] = caption
    return llamar('send-media', body)


rec = {}
rec['intro'] = llamar('send-message', {'chatId': CARLOS, 'message':
    '🤖 Claude · 🦷 IMPLANTE · PAQUETE PARA GENJUTSU (look de la hoja de Alberto, al final morph a la sonrisa feliz).\n'
    'Por tramo: Motion Transfer, 9:16, sube el video, las imágenes del ZIP en orden y pega el prompt. '
    'Tramo A 0–18 s (imágenes 01–05) y tramo B 17–35 s (imágenes 05–10).'})
time.sleep(5)
rec['hoja'] = media(AQUI / 'HOJA_CUADROS.jpg', 'Los 10 cuadros GPT Image 2')
for letra in 'AB':
    time.sleep(8)
    rec[letra + '_video'] = media(AQUI / ('TRAMO_' + letra) / ('00_VIDEO_TRAMO_%s.mp4' % letra), 'Tramo %s · video de movimiento para Genjutsu' % letra, documento=True)
    time.sleep(8)
    rec[letra + '_zip'] = media(AQUI / ('TRAMO_%s_IMAGENES.zip' % letra), 'Tramo %s · imágenes numeradas' % letra, documento=True)
    time.sleep(5)
    texto = (AQUI / ('PROMPT_TRAMO_%s.txt' % letra)).read_text()
    rec[letra + '_prompt'] = llamar('send-message', {'chatId': CARLOS, 'message': 'Tramo %s · PROMPT (copia todo este mensaje):\n\n' % letra +
                                     texto.split('(desde aquí) ===========')[1].split('===========')[0].strip()})
(AQUI / 'recibo_whatsapp.json').write_text(json.dumps(rec, indent=1))
print(rec)
