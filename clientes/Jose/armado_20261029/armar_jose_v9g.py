"""José v9g (31 oct): igual que v9f pero SIN paneles de texto sobre el video (pedido de Carlos); solo subtítulos normales abajo
(frases cortas sincronizadas con Whisper sobre la voz) + la misma tarjeta final de v9f."""
from pathlib import Path
import subprocess, numpy as np
from faster_whisper import WhisperModel
R = Path('/workspaces/Nexusv2.0launch18octubre'); A = R / 'clientes/Jose/armado_20261029'; T = A / 'tmp_v9g'; T.mkdir(exist_ok=True)
V = A / 'tmp_v9d'; F = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
clips = ['V7_lluvia', 'V2_cubetas', 'V4_primario', 'V5_poliuretano', 'V6_terminada', 'V8_cierre']
CORR = {'grupo jr': 'Grupo JR', 'grupo j r': 'Grupo JR', 'jotero': 'JR'}
b = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(V / 'voz.wav'), '-f', 's16le', '-ac', '1', '-ar', '16000', '-'], capture_output=True).stdout
seg, _ = WhisperModel('medium', compute_type='int8').transcribe(np.frombuffer(b, np.int16).astype(np.float32) / 32768, language='es', word_timestamps=True)
pal = [(w.start, w.end, w.word.strip()) for s in seg for w in s.words]
GUION = '¿Se te filtra el agua cuando llueve? En Grupo JR lo resolvemos. Usamos poliuretano acrílico de 12 años más primario fibratado elástico. Primero el primario, para una base sólida. Luego la protección continua, sin uniones. Tu losa queda lista para la temporada de lluvias. Mándanos fotos de tu azotea por WhatsApp y te cotizamos hoy.'.split()
if len(GUION) == len(pal): pal = [(a, e, g) for (a, e, _), g in zip(pal, GUION)]
else: print('AVISO: no cuadra el guion', len(GUION), len(pal))
# trozos de máx 4 palabras, cortando en puntuación
trozos, cur = [], []
for p in pal:
    cur.append(p)
    if len(cur) >= 4 or p[2][-1:] in '.,?!':
        trozos.append(cur); cur = []
if cur: trozos.append(cur)
def limpio(t):
    t = t.replace("'", '’').replace(':', '\\:').replace('%', '\\%')
    for k, v in CORR.items(): t = t.replace(k, v).replace(k.title(), v)
    return t
fl = []
for i, tr in enumerate(trozos):
    a = tr[0][0]; e = trozos[i + 1][0][0] if i + 1 < len(trozos) else tr[-1][1] + .3
    txt = limpio(' '.join(w for _, _, w in tr))
    fl.append(f"drawtext=fontfile={F}:text='{txt}':fontsize=40:fontcolor=white:borderw=4:bordercolor=black:x=(w-text_w)/2:y=h*0.80:enable='between(t,{a:.2f},{e:.2f})'")
(T / 'subs.txt').write_text('\n'.join(' '.join(w for _, _, w in tr) for tr in trozos))
(T / 'list.txt').write_text(''.join(f"file '{V / c}.mp4'\n" for c in clips))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(T / 'list.txt'), '-vf', 'scale=720:1280,setsar=1,fps=30,' + ','.join(fl),
                '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '20', '-pix_fmt', 'yuv420p', str(T / 'cuerpo.mp4')], check=True)
(T / 'list2.txt').write_text(f"file '{T / 'cuerpo.mp4'}'\nfile '{A / 'tmp_v9f/card.mp4'}'\n")
out = R / 'clientes/Jose/Jose_GrupoJR_Pixar_obrero_v9g.mp4'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(T / 'list2.txt'), '-i', str(V / 'voz.wav'), '-map', '0:v', '-map', '1:a', '-af', 'apad', '-shortest',
                '-c:v', 'libx264', '-profile:v', 'main', '-pix_fmt', 'yuv420p', '-preset', 'fast', '-crf', '22', '-c:a', 'aac', '-movflags', '+faststart', str(out)], check=True)
print(out)
