"""Voz del video 'flujo de trabajo' (Fish, voz Farid dick 2) por segmentos + tiempos por palabra con faster-whisper."""
import json, urllib.request, subprocess, numpy as np
from pathlib import Path
import imageio_ffmpeg
A = Path(__file__).resolve().parent; FF = imageio_ffmpeg.get_ffmpeg_exe()
K = [l.split('=', 1)[1].strip().strip('"\'') for l in open('/workspaces/Nexusv2.0launch18octubre/.env') if l.startswith('FISH_API_KEY=')][0]
VOZ = '5bec805f042d447cb4c542f49f225178'
SEG = {
 'P': 'Software, lector, impresora, instalación y soporte, por tres mil quinientos pesos.',
 'S1': 'Uno: escaneas el producto con el lector.',
 'S2': 'Dos: se suma a la compra, con el total al instante.',
 'S3': 'Tres: cobras.',
 'S4': 'Cuatro: se imprime el ticket.',
 'S5': 'Cinco: consultas tu inventario y tu corte de caja.',
 'S6': 'Con rutas, tu vendedor registra desde la app Android y la tienda lo ve en tiempo real.',
 'E': 'Pago contra entrega: pagas hasta recibir tu impresora, lector y estar capacitado.',
 'F': 'Confirma tu entrega en WhatsApp.',
}
def tts(t):
    r = urllib.request.Request('https://api.fish.audio/v1/tts', method='POST', data=json.dumps({'text': t, 'format': 'wav', 'reference_id': VOZ, 'prosody': {'speed': 1.25}}).encode(),
        headers={'Authorization': 'Bearer ' + K, 'Content-Type': 'application/json', 'model': 's2-pro'})
    return urllib.request.urlopen(r, timeout=300).read()
for k, t in SEG.items():
    if not (A / 'voz_v5b' / f'{k}.wav').exists(): (A / 'voz_v5b' / f'{k}.wav').write_bytes(tts(t))
from faster_whisper import WhisperModel
import av
m = WhisperModel('small', device='cpu', compute_type='int8')
res = {}
for k in SEG:
    c = av.open(str(A / 'voz_v5b' / f'{k}.wav')); rs = av.AudioResampler(format='s16', layout='mono', rate=16000)
    x = np.concatenate([a.to_ndarray().ravel() for f in c.decode(audio=0) for a in rs.resample(f)]).astype(np.float32) / 32768
    segs, _ = m.transcribe(x, language='es', word_timestamps=True)
    palabras = [(w.word.strip(), round(w.start, 3), round(w.end, 3)) for s in segs for w in s.words]
    e = subprocess.run([FF, '-i', str(A / 'voz_v5b' / f'{k}.wav')], capture_output=True, text=True).stderr
    h, mi, s = e.split('Duration: ')[1].split(',')[0].split(':'); d = int(h) * 3600 + int(mi) * 60 + float(s)
    res[k] = {'texto': SEG[k], 'dur': round(d, 3), 'palabras': palabras}
    print(k, round(d, 2), len(palabras), 'palabras')
(A / 'voz_v5b' / 'tiempos.json').write_text(json.dumps(res, ensure_ascii=False, indent=1))
print('total', round(sum(v['dur'] for v in res.values()), 1))
