"""Mariano gancho helicóptero (1 nov 2026): voz clonada (Fish) de la frase del gancho por casa; 4 tomas, elige con Whisper medium."""
import difflib, json, re, subprocess, sys
from pathlib import Path
import requests, imageio_ffmpeg
AQUI = Path(__file__).resolve().parent; RAIZ = AQUI.parents[4]; FF = imageio_ffmpeg.get_ffmpeg_exe()
env = dict(l.strip().split('=', 1) for l in open(RAIZ / '.env') if '=' in l and not l.lstrip().startswith('#'))
H = {'Authorization': 'Bearer ' + env['FISH_API_KEY'].strip('"\''), 'Content-Type': 'application/json', 'model': 's2-pro'}
VOZ = '574f8646b8e54d1dab2bb8a6dd1aa189'
LINEAS = {'BUG': '¿Buscas casa en Rosarito? Así se llega a la Bugambilia de Viscaíno Residencial. Desde dos punto cuatro millones.'}
from faster_whisper import WhisperModel
W = WhisperModel('medium', compute_type='int8'); norm = lambda t: re.sub(r'[^a-záéíóúñü0-9 ]', '', t.lower().replace('vizcaíno', 'viscaíno')).split()
for k, t in LINEAS.items():
    mejor = None
    for i in range(4):
        r = requests.post('https://api.fish.audio/v1/tts', headers=H, timeout=300, data=json.dumps({'text': t, 'format': 'wav', 'reference_id': VOZ})); r.raise_for_status()
        p = AQUI / f'{k}_{i}.wav'; p.write_bytes(r.content); oido = ' '.join(s.text for s in W.transcribe(str(p), language='es')[0])
        sc = difflib.SequenceMatcher(None, norm(t), norm(oido)).ratio(); print(k, i, round(sc, 3), oido)
        if not mejor or sc > mejor[0]: mejor = (sc, p)
    subprocess.run([FF, '-v', 'error', '-y', '-i', str(mejor[1]), str(AQUI / f'{k}.wav')], check=True); print('elegida', mejor)
