"""Anima un flyer de Mariano con el método que usó Astra en el flyer 1 (Carlos: «haz el siguiente flyer como lo
hizo Astra el último con end frame»):

  inicio = fondo_flyer_N.png (sin texto)  →  final = flyer_N.jpg (el flyer original, exacto)
  kwaivgi/kling-v2.6-pro/image-to-video, 5 s, sin sonido, y luego SFX con mirelo-ai/sfx-1.6/video-to-video.

Así el clip abre con la foto limpia, el texto y los logos entran animados y el último cuadro es el flyer tal cual.
Guarda el id del job: si se vuelve a correr, retoma en vez de pagar otra generación.
Uso: python3 kling_flyer_endframe.py 2
"""
import base64, json, os, sys, time, urllib.error, urllib.request
from io import BytesIO
from pathlib import Path
from PIL import Image

AQUI = Path(__file__).resolve().parent
ENV = Path('/workspaces/visionagenciaIAV2.0/visionagenciaIAv2.0-cripto-sim-y-corte-catania/VisionagenciaIAv2.0-main/.env')
API = 'https://api.wavespeed.ai/api/v3'
MODELO = 'kwaivgi/kling-v2.6-pro/image-to-video'
SFX = 'mirelo-ai/sfx-1.6/video-to-video'

BASE = ('Create a polished 5-second cinematic animation that starts on the clean background and ends EXACTLY on the '
        'original flyer. Animate only the original text, logos and icons appearing in sequence, perfectly legible and '
        'locked to their exact final positions, with elegant fades, gentle upward motion and a soft light sweep. '
        'Keep the exact composition, framing, colours and architecture; subtle parallax and barely moving clouds only. ')
CIERRE = ('The final frame must match the end image exactly. No invented words, no spelling changes, no warped or '
          'flickering letters, no new objects, people or cars, no camera shake.')
PROMPTS = {
    '2': BASE + ('This flyer shows three white coastal houses in diagonal blue panels. Reveal order: the San Marino '
                 'shield and title first, then the "3 formas de vivir" headline, then the three house photos settling '
                 'into their diagonal panels, then the price and the Grupo Lagsa footer last. ') + CIERRE,
    '3': BASE + ('Mexican party invitation flyer with papel picado, confetti and lottery cards of the houses. Reveal '
                 'order: papel picado and confetti drifting in first, then the "Tarde Mexicana" title, then the '
                 'lottery cards settling, then the date, schedule and footer last. ') + CIERRE,
    '4': BASE + ('Dark blue flyer with three stacked aerial photos on the right. Reveal order: shield and title first, '
                 'then the "Últimos lotes" headline and price, then the three photos, then the benefit icons and '
                 'footer last. ') + CIERRE,
    '5': BASE + ('Aerial photo of the development with two hands framing the view. Reveal order: shield and title '
                 'first, then the headline and price, then the blue tag and the footer last. ') + CIERRE,
    '6': BASE + ('Sunset coastal aerial photo. Reveal order: shield and title first, then the price headline, then the '
                 'four benefit cards, then the two bottom photos and footer last. ') + CIERRE,
}
NEG = ('invented text, misspelled words, warped letters, flickering text, extra logos, watermark, distorted '
       'architecture, melting buildings, jitter, camera shake, new people, new cars, low quality')
# Un diseño sonoro por flyer, en capas y a tiempo con lo que aparece (Carlos: «mejores sonidos»).
SONIDO_BASE = ('High-end sound design for a 5-second ad, clean and full: layered stereo, natural reverb, crisp highs '
               'and a warm low end. Time the accents to what appears on screen. No music, no voice, no speech.')
SONIDOS = {
    '1': SONIDO_BASE + (' Family walking on a quiet coastal road: soft unhurried footsteps on warm asphalt, a light '
                        'inland breeze with distant ocean surf, a small dog collar jingling now and then, faint happy '
                        'children far in the background, a gentle airy rise as the title appears and a warm low settle '
                        'on the final frame.'),
    '2': SONIDO_BASE + (' Coastal real-estate reveal: distant ocean surf and open-air wind bed, a soft airy whoosh '
                        'rising as the camera settles, three light glassy swishes as each photo panel slides into '
                        'place, a delicate shimmer as the light sweep crosses the title, and a deep polished low '
                        'impact with a short tail on the final frame.'),
    '3': SONIDO_BASE + (' Rich warm Mexican outdoor fiesta, full and lively: papel picado tissue paper fluttering and '
                        'snapping crisply in the breeze on both sides of the stereo field, two bright confetti bursts '
                        'with fine paper raining down, firm wooden card slaps and a riffled card shuffle as the '
                        'lotería cards land one by one, a small clay-and-wood shaker and a single bright acoustic '
                        'guitar rasgueo accent as the title lands (one strum, not a music bed), a light triangle or '
                        'bell sparkle on the date, a happy outdoor crowd with children playing and scattered claps '
                        'breathing far in the background, warm afternoon air, and a deep rounded low thump with a '
                        'short tail as the invitation settles.'),
    '4': SONIDO_BASE + (' Premium aerial reveal: high-altitude wind bed, three smooth cinematic whooshes as the aerial '
                        'photos stack into place, subtle digital ticks as the benefit icons appear, and a confident '
                        'deep sub impact on the final frame.'),
    '5': SONIDO_BASE + (' Open-air aerial vista: steady coastal wind with distant surf, a soft cloth-and-skin movement '
                        'as the hands frame the view, a bright airy rise as the price appears, and a clean low impact '
                        'to close.'),
    '6': SONIDO_BASE + (' Sunset coastal calm: slow ocean waves and warm evening wind, a smooth rising whoosh into the '
                        'headline, four soft rounded taps as the benefit cards pop in one by one, and a gentle deep '
                        'settle on the final frame.'),
}


def clave():
    for l in ENV.read_text().splitlines():
        if l.startswith('WAVESPEED_API_KEY='):
            return l.split('=', 1)[1].strip().strip('"').strip("'")
    return ''


CAB = {'Authorization': 'Bearer ' + clave(), 'Content-Type': 'application/json'}


def uri(path):
    im = Image.open(path).convert('RGB'); im.thumbnail((1600, 1600))
    b = BytesIO(); im.save(b, 'PNG')
    return 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()


def post(modelo, body):
    req = urllib.request.Request(API + '/' + modelo, data=json.dumps(body).encode(), headers=CAB)
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return json.load(r)['data']['id']
    except urllib.error.HTTPError as e:
        raise RuntimeError(e.read().decode()[:1500])


def esperar(job, etiqueta):
    for i in range(300):
        req = urllib.request.Request(f'{API}/predictions/{job}/result', headers=CAB)
        with urllib.request.urlopen(req, timeout=60) as r:
            d = json.load(r).get('data') or {}
        if i % 6 == 0:
            print(etiqueta, d.get('status'), flush=True)
        if d.get('status') == 'completed':
            return d['outputs'][0]
        if d.get('status') == 'failed':
            raise RuntimeError(etiqueta + ' falló: ' + str(d.get('error')))
        time.sleep(4)
    raise TimeoutError(etiqueta)


def bajar(url, path):
    with urllib.request.urlopen(url, timeout=600) as r:
        Path(path).write_bytes(r.read())


def animar(n):
    fondo = AQUI / ('fondo_flyer_%s.png' % n)
    original = next(p for p in (AQUI / ('flyer_%s.%s' % (n, e)) for e in ('jpg', 'png')) if p.exists())
    job_f = AQUI / ('kling_flyer%s_job.json' % n)
    sjob_f = AQUI / ('sfx_flyer%s_job.json' % n)
    salida = AQUI / ('FLYER%s_5S_TEXTO_ANIMADO_SIN_AUDIO.mp4' % n)
    con_sfx = AQUI / ('FLYER%s_5S_TEXTO_ANIMADO_CON_SFX.mp4' % n)
    prompt = PROMPTS.get(n, BASE + CIERRE)
    sonido = SONIDOS.get(n, SONIDO_BASE)

    if salida.exists():
        print('Kling ya existe:', salida.name)
    else:
        job = json.loads(job_f.read_text())['id'] if job_f.exists() else post(MODELO, {
            'image': uri(fondo), 'end_image': uri(original), 'prompt': prompt,
            'negative_prompt': NEG, 'duration': 5, 'sound': False})
        job_f.write_text(json.dumps({'id': job, 'model': MODELO, 'prompt': prompt}, indent=2))
        bajar(esperar(job, 'kling'), salida)
        print('Kling listo:', salida.name)

    if con_sfx.exists():
        print('SFX ya existe:', con_sfx.name); return
    sj = json.loads(sjob_f.read_text())['id'] if sjob_f.exists() else post(SFX, {
        'video': _video_uri(salida), 'prompt': sonido, 'duration': 5, 'num_samples': 1, 'seed': -1})
    sjob_f.write_text(json.dumps({'id': sj, 'model': SFX, 'prompt': sonido}, indent=2))
    bajar(esperar(sj, 'sfx'), con_sfx)
    print('SFX listo:', con_sfx.name)


def _video_uri(path):
    return 'data:video/mp4;base64,' + base64.b64encode(Path(path).read_bytes()).decode()


if __name__ == '__main__':
    for n in sys.argv[1:] or ['2']:
        animar(n)
