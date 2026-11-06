"""Alternativa barata a Genjutsu (Higgsfield), que está tardando mucho.

`decart/lucy-restyle` en WaveSpeed cuesta $0.01 por generación, es texto sobre video (conserva movimiento, cámara y
consistencia temporal) y NO tiene tope de 30 s, así que el tramo A de 18 s entra completo.
Diferencia con Genjutsu: no acepta imágenes de referencia, el look va solo por prompt.

El esquema pide `video` como string. Se intenta primero data URI en base64 (como aceptó el modelo de SFX);
si lo rechaza, lo reporta claro para subir el archivo a una URL pública.

Uso: python3 prueba_lucy_restyle.py [ruta_video]
"""
import base64, json, os, sys, time, urllib.error, urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ENV = Path('/workspaces/visionagenciaIAV2.0/visionagenciaIAv2.0-cripto-sim-y-corte-catania/VisionagenciaIAv2.0-main/.env')
API = 'https://api.wavespeed.ai/api/v3'
MODELO = 'decart/lucy-restyle'
VIDEO = Path(sys.argv[1]) if len(sys.argv) > 1 else AQUI / 'TRAMO_A' / '00_VIDEO_TRAMO_A.mp4'
SALIDA = AQUI / 'PRUEBA_LUCY_RESTYLE_TRAMO_A.mp4'

PROMPT = (
    "Transform this rough grey 3D animation into a premium, photoreal dental implant explainer, keeping the exact "
    "camera motion, timing and composition. Look: near-black background with deep teal and warm orange bokeh, bright "
    "glossy white enamel, translucent pink gums with a warm luminous edge, porous cream bone with a glowing orange cut "
    "edge, satin titanium, cinematic soft teal rim light, shallow depth of field. The woman keeps the same face and a "
    "single missing upper front tooth. Anatomically clean, not gore. No text, no logos, no watermark."
)


def clave():
    for l in ENV.read_text().splitlines():
        if l.startswith('WAVESPEED_API_KEY='):
            return l.split('=', 1)[1].strip().strip('"').strip("'")
    return ''


CAB = {'Authorization': 'Bearer ' + clave(), 'Content-Type': 'application/json'}


def lanzar(video_str):
    cuerpo = {'prompt': PROMPT, 'video': video_str}
    req = urllib.request.Request(API + '/' + MODELO, data=json.dumps(cuerpo).encode(), headers=CAB)
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r)['data']['id']


def esperar(job):
    for i in range(300):
        req = urllib.request.Request(f'{API}/predictions/{job}/result', headers=CAB)
        with urllib.request.urlopen(req, timeout=60) as r:
            d = json.load(r).get('data') or {}
        if i % 6 == 0:
            print('  estado:', d.get('status'), flush=True)
        if d.get('status') == 'completed':
            return d['outputs'][0]
        if d.get('status') == 'failed':
            raise RuntimeError('falló: ' + str(d.get('error')))
        time.sleep(4)
    raise TimeoutError('sin respuesta')


if __name__ == '__main__':
    print('video:', VIDEO.name, round(VIDEO.stat().st_size / 1e6, 2), 'MB')
    uri = 'data:video/mp4;base64,' + base64.b64encode(VIDEO.read_bytes()).decode()
    t0 = time.monotonic()
    try:
        job = lanzar(uri)
    except urllib.error.HTTPError as e:
        print('RECHAZÓ el data URI:', e.code, e.read().decode()[:400])
        print('Hay que subir el video a una URL pública y volver a correr con esa URL.')
        raise SystemExit(1)
    print('job', job, flush=True)
    (AQUI / 'lucy_restyle_job.json').write_text(json.dumps({'id': job, 'model': MODELO, 'prompt': PROMPT}, indent=2))
    url = esperar(job)
    with urllib.request.urlopen(url, timeout=600) as r:
        SALIDA.write_bytes(r.read())
    print('listo:', SALIDA.name, '|', round(time.monotonic() - t0), 'segundos |', round(SALIDA.stat().st_size / 1e6, 2), 'MB')
