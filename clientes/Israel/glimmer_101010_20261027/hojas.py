"""Hojas de 8 cuadros de cada reel de referencia + hoja del material real de Israel + transcripción de los reels."""
import glob, json, re, subprocess
from pathlib import Path
import numpy as np, imageio_ffmpeg
from PIL import Image
AQUI = Path(__file__).resolve().parent; RAIZ = AQUI.parent; FF = imageio_ffmpeg.get_ffmpeg_exe()

def dur(v):
    r = subprocess.run([FF, '-i', str(v)], capture_output=True, text=True).stderr
    h, m, s = re.search(r'Duration: (\d+):(\d+):([\d.]+)', r).groups(); return int(h) * 3600 + int(m) * 60 + float(s)

def hoja(v, salida, n=8):
    d = dur(v); subprocess.run([FF, '-v', 'error', '-y', '-i', str(v), '-vf', f'fps={n}/{d:.2f},scale=270:-2,tile={n//2}x2', '-frames:v', '1', str(salida)])

refs = sorted((RAIZ / 'referencia' / 'instagram').glob('*.mp4'))
for v in refs: hoja(v, AQUI / f'ref_{v.stem}.jpg')
# material real: 12 fotos + un cuadro de 12 videos
fotos = sorted((RAIZ / 'whatsapp' / 'del_cliente').glob('*.jpg'))[::4][:12]
vids = sorted((RAIZ / 'whatsapp' / 'del_cliente').glob('*.mp4'))[::3][:12]
ims = [Image.open(f).convert('RGB') for f in fotos]
for v in vids:
    t = dur(v) / 2; out = AQUI / '_tmp.jpg'
    subprocess.run([FF, '-v', 'error', '-y', '-ss', f'{t:.1f}', '-i', str(v), '-frames:v', '1', str(out)]); ims.append(Image.open(out).convert('RGB'))
ims = [i.resize((240, int(240 * i.height / i.width))).crop((0, 0, 240, 300)) for i in ims]
H = Image.new('RGB', (240 * 6, 300 * 4), 'white')
for k, i in enumerate(ims[:24]): H.paste(i, ((k % 6) * 240, (k // 6) * 300))
H.save(AQUI / 'material_israel.jpg', quality=88); (AQUI / '_tmp.jpg').unlink(missing_ok=True)
# transcripción
from faster_whisper import WhisperModel
m = WhisperModel('small', device='cpu', compute_type='int8'); tr = {}
for v in refs:
    pcm = subprocess.run([FF, '-v', 'error', '-i', str(v), '-f', 's16le', '-ac', '1', '-ar', '16000', '-'], capture_output=True).stdout
    segs, info = m.transcribe(np.frombuffer(pcm, np.int16).astype(np.float32) / 32768)
    tr[v.stem] = {'duracion': round(dur(v), 1), 'idioma': info.language, 'texto': ' '.join(s.text.strip() for s in segs)}
(AQUI / 'transcripciones.json').write_text(json.dumps(tr, ensure_ascii=False, indent=1)); print(json.dumps(tr, ensure_ascii=False, indent=1))
