"""Genera cada frase 4 veces (modelos s2-pro y s1, dos semillas de texto) y se queda con la que mejor se entiende según la transcripción."""
import difflib, json, os, re, subprocess, urllib.request
import numpy as np
from faster_whisper import WhisperModel
VOZ = '1f679152b5d64c09a8e8eeecd3eb5424'
FRASES = ['¿Tu publicidad no te trae mensajes?', 'Estás perdiendo dinero hoy mismo.',
          'Muchos negocios regalan su presupuesto a Meta intentando adivinar qué funciona, sin una estrategia clara.',
          'En Nexus creamos tu estrategia, tus volantes y tu primer video gratis, en una llamada de diez minutos.',
          'Ya ayudamos a otros a bajar sus costos de mensajes drásticamente.', 'Toca el botón y agenda tu llamada.',
          'El costo es de quinientos pesos.', 'El precio por dejar de adivinar y empezar a dominar Facebook.']
DICHO = {3: 'En Néksus creamos tu estrategia, tus volantes y tu primer video gratis, en una llamada de diez minutos.',
         7: 'El precio por dejar de adivinar, y empezar a dominar Feisbuk.', 1: 'Estás perdiendo dinero, hoy mismo.'}
m = WhisperModel('medium', device='cpu', compute_type='int8')
norm = lambda t: re.sub(r'[^a-záéíóúñ0-9 ]', '', t.lower().replace('nexus', 'néksus').replace('facebook', 'feisbuk').replace('quinientos', '500').replace('diez', '10'))
def tr(f):
    b = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-f', 's16le', '-ac', '1', '-ar', '16000', '-'], capture_output=True).stdout
    s, _ = m.transcribe(np.frombuffer(b, np.int16).astype(np.float32) / 32768, language='es', initial_prompt='Nexus, Meta, Facebook, estrategia, volantes.')
    return ' '.join(x.text.strip() for x in s)
for k, meta in enumerate(FRASES):
    texto = DICHO.get(k, meta); mejor = (-1, None, '')
    for j, (modelo, txt) in enumerate([('s2-pro', texto), ('s1', texto), ('s2-pro', texto + ' '), ('s1', texto + ' ')]):
        f = f'c{k}_{j}.wav'
        if not os.path.exists(f):
            h = {'Authorization': 'Bearer ' + os.environ['FISH_API_KEY'], 'Content-Type': 'application/json', 'model': modelo}
            r = urllib.request.Request('https://api.fish.audio/v1/tts', method='POST', data=json.dumps({'text': txt, 'format': 'wav', 'reference_id': VOZ}).encode(), headers=h)
            open(f, 'wb').write(urllib.request.urlopen(r, timeout=300).read())
        t = tr(f); sc = difflib.SequenceMatcher(None, norm(t), norm(meta)).ratio()
        if sc > mejor[0]: mejor = (sc, f, t)
    os.replace(mejor[1], f'f{k}_raw.wav')
    print(k, f'{mejor[0]:.2f}', mejor[2], flush=True)
