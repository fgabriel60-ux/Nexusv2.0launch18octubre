"""Mariano · Vizcaíno v4 «calidad de referencia» (reel del realtor que mandó Carlos + arte oficial en hora dorada). Plan de Glimmer del 24 oct:
gancho «Esta es tu oportunidad en Rosarito» caminando frente a las 3 casas → dron rasante → amenidades reales del arte (privada, acceso controlado, pádel,
juegos) → 3 modelos → precios → cierre con palabra clave + presupuesto. Voz Fish de Mariano por frase; escenas Qwen-Image-Edit + MiniMax H3 a 720×1280 con
los labios guiados por su voz. Uso: python3 mariano_v4_escenas.py  (luego armar_mariano_v4.py)"""
import json, subprocess, sys, urllib.request
from pathlib import Path
import imageio_ffmpeg
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/_productor')
from escenas_modal import app, escenas

AQUI = Path(__file__).resolve().parent
V4 = AQUI / 'v4'
FF = imageio_ffmpeg.get_ffmpeg_exe()
LLAVE = [l.split('=', 1)[1].strip().strip('"\'') for l in open('/workspaces/Nexusv2.0launch18octubre/.env') if l.startswith('FISH_API_KEY=')][0]
VOZ_MARIANO = '574f8646b8e54d1dab2bb8a6dd1aa189'
FRASES = ['Esta es tu oportunidad en Rosarito.',
          'Vizcaíno Residencial: un nuevo modelo de vivienda para cada etapa de vida.',
          'En privada, con acceso controlado, cancha de pádel y área de juegos.',
          'Tres modelos: Benjamina, Salvia y Bugambilia.',
          'Desde dos millones cuatrocientos cincuenta mil pesos.',
          'Escríbeme por WhatsApp con la palabra Vizcaíno y tu presupuesto, y agendamos tu visita.']
CARA = 'Conserva EXACTAMENTE la cara de este hombre: mismos ojos, cejas, nariz, boca, barba, edad, tono de piel y cabello. Saco azul claro y camisa blanca. '
DORADA = ('Hora dorada: el sol bajo pinta las fachadas color arena de naranja cálido, cielo azul intenso y limpio, pasto verde recortado y banqueta de concreto, '
          'como en el arte oficial. Foto vertical 9:16, cinematográfica, lente gran angular de 24 mm, profundidad de campo, nítida, sin texto, sin letras, sin logotipos.')
CUADROS = {
    'C1_camina': (['mariano', 'arte'], CARA + 'Él camina hacia la cámara por la banqueta frente a ESTAS mismas casas de dos pisos (las del arte), plano medio de cuerpo completo, '
                  'sonrisa segura, una mano abierta señalando las casas. ' + DORADA),
    'C2_dron': (['arte'], 'Vista de dron a baja altura, rasante, sobre ESTA misma fila de casas de dos pisos color arena con techos planos, mirando hacia adelante a lo largo '
                'de la calle del fraccionamiento, se ven más casas iguales al fondo. ' + DORADA),
    'C3_presenta': (['mariano', 'arte'], CARA + 'Plano medio de la cintura para arriba frente a la fachada de ESTA casa, él mira a cámara y presenta con la mano abierta. ' + DORADA),
    'C4_fila': (['arte'], 'La MISMA imagen de las tres casas en fila en hora dorada, mismo encuadre, pero SIN ningún texto, sin logotipos y sin precios; completa el cielo '
                'azul limpio donde estaba el texto. ' + DORADA),
    'C6_cierre': (['mariano', 'arte'], CARA + 'Primer plano del pecho para arriba, sonriente, mirando a cámara y apuntando con el dedo hacia la cámara, con ESTAS casas '
                  'desenfocadas atrás. ' + DORADA),
}
HABLA = (' He speaks Spanish to the camera with natural lip movement matching the speech, confident friendly expression. Cinematic, golden hour, shallow depth '
         'of field. Keep his face exactly. No text. Audio: clear male voice speaking Spanish.')
MUDO = ' Cinematic, golden hour, smooth. No text. Audio: soft ambience, no speech.'


def duracion(p):
    t = subprocess.run([FF, '-i', str(p)], capture_output=True, text=True).stderr.split('Duration: ')[1].split(',')[0].split(':')
    return int(t[0]) * 3600 + int(t[1]) * 60 + float(t[2])


def voces():
    (V4 / 'voz').mkdir(parents=True, exist_ok=True); d = []
    for i, t in enumerate(FRASES):
        mp3, wav = V4 / 'voz' / f'f{i}.mp3', V4 / 'voz' / f'f{i}.wav'
        if not wav.exists():
            r = urllib.request.Request('https://api.fish.audio/v1/tts', method='POST',
                                       data=json.dumps({'text': t, 'format': 'mp3', 'reference_id': VOZ_MARIANO, 'prosody': {'speed': 1.05}, 'temperature': 0.6, 'top_p': 0.8}).encode(),
                                       headers={'Authorization': 'Bearer ' + LLAVE, 'Content-Type': 'application/json', 'model': 's2-pro'})
            mp3.write_bytes(urllib.request.urlopen(r, timeout=300).read())
            subprocess.run([FF, '-v', 'error', '-y', '-i', str(mp3), '-af', 'apad=pad_dur=0.2', '-ar', '44100', '-ac', '1', str(wav)], check=True)
        d.append(round(duracion(wav), 2))
    return d


if __name__ == '__main__':
    d = voces(); print('voces', d, flush=True)
    tomas = [('M4_camina', 'C1_camina', 'Vertical shot: the man walks slowly toward the camera along the sidewalk in front of the houses while the camera tracks backward.' + HABLA, d[0], None, 'f0'),
             ('M4_dron', 'C2_dron', 'Low FPV drone shot gliding fast and smooth forward over the rooftops and along the street of the residential complex.' + MUDO, d[1]),
             ('M4_presenta', 'C3_presenta', 'Vertical medium shot, slow dolly in, he presents the houses with an open hand.' + HABLA, d[2], None, 'f2'),
             ('M4_fila', 'C4_fila', 'Slow cinematic lateral camera move from left to right along the three houses, the warm sunlight flickers softly.' + MUDO, d[3] + d[4]),
             ('M4_cierre', 'C6_cierre', 'Vertical close-up, slow push-in, he smiles and points at the camera.' + HABLA, d[5], None, 'f5')]
    refs = {'mariano': (AQUI.parent / 'fotos' / 'mariano_luz_final.png').read_bytes(),
            'arte': (AQUI.parent / 'referencia' / 'calidad' / 'vizcaino_flyer_final.jpg').read_bytes()}
    voz_bytes = {f'f{i}': (V4 / 'voz' / f'f{i}.wav').read_bytes() for i in (0, 2, 5)}
    with app.run():
        res = escenas.remote('mariano_v4', refs, CUADROS, tomas, 7, None, voz_bytes, (704, 1280))   # H3 pide múltiplos de 32: con 720 truena
    for n, b in res.items():
        (V4 / n).write_bytes(b); print('guardado', n, flush=True)
