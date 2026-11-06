"""Manda los 3 videos de Rar~Amore armados con los clips de MiniMax H3 al chat de Jesús (360 Salud)."""
import base64, json, os, time, urllib.error, urllib.request
from datetime import datetime
from pathlib import Path

AQUI = Path(__file__).resolve().parent
JESUS = '31606932787332@lid'
DESTINO = '6312470486@c.us'  # instancia de prueba: solo puede mandar al número de Carlos, él los reenvía
TOKEN = os.environ['WAAPI_TOKEN']
INSTANCIA = os.environ.get('WAAPI_INSTANCE', '105840')
PIEZAS = [
    ('RarAmore_A_Estudio.mp4', 'Rar~Amore A · Estudio'),
    ('RarAmore_B_LuzCalida.mp4', 'Rar~Amore B · Luz cálida'),
    ('RarAmore_C_Naturaleza.mp4', 'Rar~Amore C · Naturaleza'),
]


def accion(nombre, payload):
    req = urllib.request.Request(
        f'https://waapi.app/api/v1/instances/{INSTANCIA}/client/action/{nombre}',
        data=json.dumps(payload).encode(), method='POST',
        headers={'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'})
    for intento in range(8):
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
            time.sleep(int(e.headers.get('Retry-After') or 0) or 5 * 2 ** intento)
    raise RuntimeError('WaAPI sigue limitando peticiones (429)')


recibos = []
for archivo, pie in PIEZAS:
    r = accion('send-media', {
        'chatId': DESTINO,
        'mediaBase64': base64.b64encode((AQUI / 'final' / archivo).read_bytes()).decode(),
        'mediaName': archivo, 'mediaCaption': pie})
    estado = ((r.get('data') or {}).get('data') or {}).get('status', (r.get('data') or {}).get('status'))
    print(archivo, '->', estado, flush=True)
    recibos.append({'pieza': archivo, 'status': estado})
    time.sleep(3)

(AQUI / 'recibo_envio.json').write_text(json.dumps(
    {'enviado_a': f'Carlos ({DESTINO}) para reenviar a Jesús ({JESUS})', 'fecha': datetime.now().isoformat(timespec='seconds'),
     'piezas': recibos}, ensure_ascii=False, indent=2))
