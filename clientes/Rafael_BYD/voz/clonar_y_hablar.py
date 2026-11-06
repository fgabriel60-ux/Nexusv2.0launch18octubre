"""Rafael BYD (1 nov 2026): clona su voz en Fish con sus audios de WhatsApp (30 oct) y genera las frases del gancho v1.
4 tomas por frase; se queda con la que Whisper medium transcribe más parecido al guion. Uso: python3 clonar_y_hablar.py"""
import difflib, json, re, subprocess, sys
from pathlib import Path
import requests, imageio_ffmpeg

AQUI = Path(__file__).resolve().parent; RAIZ = AQUI.parents[2]; FF = imageio_ffmpeg.get_ffmpeg_exe()
env = {}
for l in open(RAIZ / '.env'):
    if '=' in l and not l.lstrip().startswith('#'): k, v = l.split('=', 1); env[k.strip()] = v.strip().strip('"\'')
H = {'Authorization': 'Bearer ' + env['FISH_API_KEY']}
ID = AQUI / 'voz_id_fish.txt'
if not ID.exists():
    muestras = sorted(AQUI.glob('muestra_*.wav'))
    r = requests.post('https://api.fish.audio/model', headers=H, timeout=600,
                      data={'type': 'tts', 'title': 'Rafael Hernandez BYD', 'train_mode': 'fast', 'visibility': 'private', 'enhance_audio_quality': 'true'},
                      files=[('voices', (m.name, m.read_bytes(), 'audio/wav')) for m in muestras])
    print(r.status_code, r.text[:300]); r.raise_for_status(); ID.write_text(r.json()['_id'])
VOZ = ID.read_text().strip(); print('voz', VOZ)

LINEAS = {
    'R1': '¿Estás pensando en estrenar un BYD? Soy Rafael Hernández, asesor de BYD Azcapotzalco.',
    'R2': 'Mándame mensaje por WhatsApp y te enseño el modelo que va contigo.',
    # gancho v2 (réplica del reel DO4g4PkEcis): guion de Glimmer 1 nov; «palabra CLAVE» → «BYD»
    'R3': '¿Estás listo para comprar un auto eléctrico o híbrido este mes? Soy Rafael Hernández Ortiz, asesor de BYD Azcapotzalco. Manejamos Song Plus, King y Dolphin. Escríbeme por WhatsApp con la palabra BYD.',
}
from faster_whisper import WhisperModel
W = WhisperModel('medium', compute_type='int8')
norm = lambda t: re.sub(r'[^a-záéíóúñü ]', '', t.lower().replace('whatsapp', 'whatsapp')).split()
for k, t in LINEAS.items():
    if (AQUI / f'{k}.wav').exists(): continue
    mejor = None
    for i in range(4):
        r = requests.post('https://api.fish.audio/v1/tts', headers={**H, 'Content-Type': 'application/json', 'model': 's2-pro'}, timeout=300,
                          data=json.dumps({'text': t, 'format': 'wav', 'reference_id': VOZ}))
        r.raise_for_status(); p = AQUI / f'{k}_{i}.wav'; p.write_bytes(r.content)
        oido = ' '.join(s.text for s in W.transcribe(str(p), language='es')[0])
        sc = difflib.SequenceMatcher(None, norm(t), norm(oido)).ratio(); print(k, i, round(sc, 3), oido)
        if not mejor or sc > mejor[0]: mejor = (sc, p)
    subprocess.run([FF, '-v', 'error', '-y', '-i', str(mejor[1]), str(AQUI / f'{k}.wav')], check=True); print('elegida', k, mejor)
