"""Manda a Mariano sus 6 flyers animados (Carlos, 16 sep: «mándaselos a Mariano pero corrige el audio en los que
están mal primero»). Van las versiones con el audio corregido en el 1, 2 y 3.

Antes de mandar nada revisa que los 6 archivos existan y traigan audio; si falta uno, no manda nada.
Uno por uno con pausa, para que WhatsApp no rebote los envíos grandes. Si se vuelve a correr, no repite: lleva recibo.
Uso: python3 enviar_a_mariano.py
"""
import base64, json, random, subprocess, time, urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent
MARIANO = '27337584279694@lid'
env = {}
for line in Path('/workspaces/visionagenciaIAV2.0/visionagenciaIAv2.0-cripto-sim-y-corte-catania/VisionagenciaIAv2.0-main/.env').read_text().splitlines():
    if '=' in line and not line.lstrip().startswith('#'):
        k, v = line.split('=', 1); env[k.strip()] = v.strip().strip('"').strip("'")
BASE = 'https://waapi.app/api/v1/instances/' + env['WAAPI_INSTANCE'] + '/client/action/'
CAB = {'Authorization': 'Bearer ' + env['WAAPI_TOKEN'], 'Content-Type': 'application/json'}

CLIPS = [
    ('1', 'FLYER1_5S_TEXTO_ANIMADO_CON_SFX_v2.mp4', 'Vivir bien empieza por el entorno'),
    ('2', 'FLYER2_5S_TEXTO_ANIMADO_CON_SFX_v2.mp4', '3 formas de vivir en San Marino'),
    ('3', 'FLYER3_5S_TEXTO_ANIMADO_CON_SFX_v2.mp4', 'Tarde Mexicana del 27 de septiembre'),
    ('4', 'FLYER4_5S_TEXTO_ANIMADO_CON_SFX.mp4', 'Últimos lotes'),
    ('5', 'FLYER5_5S_TEXTO_ANIMADO_CON_SFX.mp4', 'El mar pone la vista'),
    ('6', 'FLYER6_5S_TEXTO_ANIMADO_CON_SFX.mp4', 'Lotes en zona costa'),
]
INTRO = ('Buenas, le mando sus 6 flyers convertidos en video de 5 segundos 🎬\n\n'
         'Cada uno arranca con la foto sola y el texto va apareciendo, y el último cuadro queda idéntico al flyer '
         'original, así que sirve tal cual para publicar. Llevan sonido propio: el de la Tarde Mexicana con papel '
         'picado y confeti, y los de lotes con viento y mar.\n\n'
         'Dígame si le muevo el orden en que aparecen los textos o el sonido de alguno 👌')


def llamar(accion, body, intentos=3):
    for i in range(intentos):
        try:
            req = urllib.request.Request(BASE + accion, data=json.dumps(body).encode(), headers=CAB)
            with urllib.request.urlopen(req, timeout=300) as r:
                return (json.load(r).get('data') or {}).get('status')
        except Exception as e:
            err = str(e)[:90]; time.sleep(30 * (i + 1))
    return 'error ' + err


def con_audio(p):
    salida = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type', '-of', 'csv=p=0', str(p)],
                            capture_output=True, text=True).stdout
    return 'audio' in salida and 'video' in salida


faltan = [f for _, f, _ in CLIPS if not (AQUI / f).exists() or not con_audio(AQUI / f)]
if faltan:
    raise SystemExit('No se manda nada, falta o no trae audio: ' + ', '.join(faltan))

recibos_path = AQUI / 'recibos_mariano.json'
rec = json.loads(recibos_path.read_text()) if recibos_path.exists() else {}
if rec.get('intro') != 'success':
    rec['intro'] = llamar('send-message', {'chatId': MARIANO, 'message': INTRO})
    print('[mariano] intro', rec['intro'], flush=True)
    recibos_path.write_text(json.dumps(rec, ensure_ascii=False, indent=1))
    time.sleep(10)

for i, (n, archivo, titulo) in enumerate(CLIPS):
    if rec.get(n) == 'success':
        continue
    rec[n] = llamar('send-media', {'chatId': MARIANO, 'asDocument': False, 'mediaName': archivo,
                                   'mediaBase64': base64.b64encode((AQUI / archivo).read_bytes()).decode(),
                                   'mediaCaption': '%s. %s' % (n, titulo)})
    print('[mariano] flyer', n, rec[n], flush=True)
    recibos_path.write_text(json.dumps(rec, ensure_ascii=False, indent=1))
    if i < len(CLIPS) - 1:
        time.sleep(random.randint(45, 90))
print(rec)
