"""Tercera alternativa a Genjutsu: `wavespeed-ai/ltx-2-19b/control` ($0.20, hasta 20 s).

Es el que mejor encaja con el método de Carlos (3D primero): toma la geometría del render de Blender como guía por
**profundidad** (`mode: depth`), en vez de adivinar como hacía lucy. Y aguanta 20 s, así que el tramo A de 18 s
entra COMPLETO, sin recortar como hubo que hacer con MiniMax.

Diferencia contra MiniMax: solo acepta UNA imagen de referencia, no nueve.

Valores confirmados del esquema: mode = pose|depth|canny, resolution = 480p|720p|1080p,
audio_mode = preserve|generate|none. Solo `video` es obligatorio.
Uso: python3 prueba_ltx_control.py [depth|canny]
"""
import base64, json, sys, time, urllib.error, urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ENV = Path('/workspaces/visionagenciaIAV2.0/visionagenciaIAv2.0-cripto-sim-y-corte-catania/VisionagenciaIAv2.0-main/.env')
API = 'https://api.wavespeed.ai/api/v3'
MODELO = 'wavespeed-ai/ltx-2-19b/control'
MODO = sys.argv[1] if len(sys.argv) > 1 else 'depth'
VIDEO = AQUI / 'TRAMO_A' / '00_VIDEO_TRAMO_A.mp4'          # 18 s completos
REFERENCIA = AQUI / 'IMAGENES' / '04_sticker_revela.png'    # única imagen permitida: lleva rostro Y anatomía
SALIDA = AQUI / ('PRUEBA_LTX_%s_TRAMO_A.mp4' % MODO.upper())

PROMPT = (
    "Premium photoreal dental implant explainer. A woman with one missing upper front tooth; a dental syringe "
    "touches her gum; her face peels away like a sticker revealing a cross-section of the upper jaw with porous "
    "cream bone, translucent pink gums, white glossy teeth with their roots and a satin titanium implant; a thin "
    "steel drill prepares the bone. Look: near-black background with deep teal and warm orange bokeh, soft teal rim "
    "light, shallow depth of field, cinematic 3D medical render. Anatomically clean and dry, no blood, no gore, no "
    "red fluid. No text, no logos, no watermark."
)


def clave():
    for l in ENV.read_text().splitlines():
        if l.startswith('WAVESPEED_API_KEY='):
            return l.split('=', 1)[1].strip().strip('"').strip("'")
    return ''


CAB = {'Authorization': 'Bearer ' + clave(), 'Content-Type': 'application/json'}


def uri(p, mime):
    return 'data:%s;base64,%s' % (mime, base64.b64encode(Path(p).read_bytes()).decode())


def esperar(job):
    for i in range(450):
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
    print('modo:', MODO, '| video:', VIDEO.name, round(VIDEO.stat().st_size / 1e6, 2), 'MB (18 s completos)')
    cuerpo = {'video': uri(VIDEO, 'video/mp4'), 'image': uri(REFERENCIA, 'image/png'),
              'mode': MODO, 'prompt': PROMPT, 'resolution': '480p', 'audio_mode': 'none', 'seed': 42}
    t0 = time.monotonic()
    try:
        req = urllib.request.Request(API + '/' + MODELO, data=json.dumps(cuerpo).encode(), headers=CAB)
        with urllib.request.urlopen(req, timeout=300) as r:
            job = json.load(r)['data']['id']
    except urllib.error.HTTPError as e:
        print('RECHAZADO:', e.code, e.read().decode()[:500]); raise SystemExit(1)
    print('job', job, flush=True)
    (AQUI / ('ltx_%s_job.json' % MODO)).write_text(json.dumps({'id': job, 'model': MODELO, 'mode': MODO, 'prompt': PROMPT}, indent=2))
    url = esperar(job)
    with urllib.request.urlopen(url, timeout=600) as r:
        SALIDA.write_bytes(r.read())
    print('listo:', SALIDA.name, '|', round(time.monotonic() - t0), 'segundos |',
          round(SALIDA.stat().st_size / 1e6, 2), 'MB')
