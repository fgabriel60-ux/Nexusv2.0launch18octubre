"""Narración del anuncio de Jeremías con la fórmula de Meta: gancho de comodidad, precio claro, «entrega en 1 hora», pago al recibir y CTA. Voz: Carlos real (Fish Audio)."""
import json, subprocess, urllib.request
from pathlib import Path
import imageio_ffmpeg, numpy as np

AQUI = Path(__file__).resolve().parent
VOZ = '1f679152b5d64c09a8e8eeecd3eb5424'  # Carlos real · voz aislada
TEXTO = ('¿Lo quieres? Lo tienes hoy. Cama completa con colchón, tres mil quinientos pesos. '
         'Entrega en una hora y envío gratis en Mérida. Pagas hasta que lo recibes, con tarjeta o meses sin intereses. '
         'Escríbenos por WhatsApp y estrénala hoy mismo.')
env = {}
for l in Path('/workspaces/Nexusv2.0launch18octubre/.env').read_text().splitlines():
    if '=' in l and not l.lstrip().startswith('#'):
        k, v = l.split('=', 1); env[k.strip()] = v.strip().strip('"\'')
req = urllib.request.Request('https://api.fish.audio/v1/tts', method='POST',
                             data=json.dumps({'text': TEXTO, 'format': 'mp3', 'reference_id': VOZ, 'prosody': {'speed': 1.05}}).encode(),
                             headers={'Authorization': 'Bearer ' + env['FISH_API_KEY'], 'Content-Type': 'application/json', 'model': 's1'})
mp3 = AQUI / 'voz' / 'guion.mp3'
mp3.write_bytes(urllib.request.urlopen(req, timeout=300).read())
FF = imageio_ffmpeg.get_ffmpeg_exe()
print(subprocess.run([FF, '-i', str(mp3)], capture_output=True, text=True).stderr.split('Duration: ')[1].split(',')[0])
from faster_whisper import WhisperModel
raw = subprocess.run([FF, '-v', 'error', '-i', str(mp3), '-f', 'f32le', '-ac', '1', '-ar', '16000', '-'], capture_output=True).stdout
segs, _ = WhisperModel('base', device='cpu', compute_type='int8').transcribe(np.frombuffer(raw, dtype=np.float32), language='es', word_timestamps=True)
P = [(w.word.strip(), round(float(w.start), 2), round(float(w.end), 2)) for s in segs for w in s.words]
(AQUI / 'voz' / 'palabras.json').write_text(json.dumps(P, ensure_ascii=False))
print([(w, s) for w, s, e in P])
