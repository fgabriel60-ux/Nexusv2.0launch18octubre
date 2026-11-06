"""Subtítulos estilo Horseman DETRÁS de la persona (reutilizable para todos los clientes).

Receta (de catania_mariano_subs_20260914 / pancho/kling_5s/subs_horseman.py):
- Playfair Display: palabras chicas en cursiva y la palabra protagonista GIGANTE en negrita, a la altura de la cabeza.
- La persona se recorta cuadro por cuadro con rembg (u2net_human_seg) y va ENCIMA de las letras.
- Cada palabra entra con su voz (opacidad + escala 92→100 % en 5 cuadros).

Uso desde Python:
    from horseman import render
    render(tomas=[(clip_mp4, voz_wav), ...], salida='final.mp4', cierre_png=None)
La voz de cada toma es el wav limpio con el que se sincronizaron los labios; se usa también como audio final.
"""
import subprocess
from pathlib import Path
import av
import imageio_ffmpeg
import numpy as np
from faster_whisper import WhisperModel
from PIL import Image, ImageDraw, ImageFont
from rembg import new_session, remove

FF = imageio_ffmpeg.get_ffmpeg_exe()
FUENTES = Path(__file__).resolve().parent.parent / 'catania_mariano_subs_20260914' / 'fuentes'
F_BOLD = str(FUENTES / 'PlayfairDisplay[wght].ttf')
F_ITAL = str(FUENTES / 'PlayfairDisplay-Italic[wght].ttf')
W, H, FPS = 1080, 1920, 30
_modelo = None
_sesion = None
_cache = {}


def _fuente(ruta, var, tam):
    k = (ruta, var, tam)
    if k not in _cache:
        f = ImageFont.truetype(ruta, tam); f.set_variation_by_name(var); _cache[k] = f
    return _cache[k]


def _palabras(wav):
    global _modelo
    _modelo = _modelo or WhisperModel('small', device='cpu', compute_type='int8')
    c = av.open(str(wav)); rs = av.AudioResampler(format='s16', layout='mono', rate=16000)
    a = np.concatenate([x.to_ndarray().ravel() for fr in c.decode(audio=0) for x in rs.resample(fr)]).astype(np.float32) / 32768
    segs, _ = _modelo.transcribe(a, language='es', word_timestamps=True, vad_filter=True)
    return [(w.word.strip(), w.start, w.end) for s in segs for w in s.words]


def _grupos(pal):
    """Agrupa de 2 a 4 palabras; la más larga del grupo es la protagonista."""
    grupos, actual = [], []
    for p in pal:
        actual.append(p)
        if len(actual) >= 3 or p[0].endswith(('.', ',', '?', '!', ':')):
            grupos.append(actual); actual = []
    if actual:
        grupos.append(actual)
    return grupos


def _capa(grupo, t, y_centro):
    """Dibuja el grupo con la protagonista gigante; cada palabra aparece cuando la dice la voz."""
    img = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(img)
    prota = max(range(len(grupo)), key=lambda i: len(grupo[i][0].strip('.,¿?¡!:')))
    lineas = []
    for i, (p, a, b) in enumerate(grupo):
        if t < a - 0.05:
            continue
        aparicion = min(1.0, (t - a + 0.05) / 0.17)
        texto = p.strip('.,¿?¡!:').upper() if i == prota else p
        if i == prota:
            tam = 260
            while d.textlength(texto, font=_fuente(F_BOLD, b'Black', tam)) > W * 0.94 and tam > 80:
                tam -= 8
            f = _fuente(F_BOLD, b'Black', int(tam * (0.92 + 0.08 * aparicion)))
        else:
            f = _fuente(F_ITAL, b'SemiBold Italic', 84)
        lineas.append((texto, f, int(255 * aparicion)))
    alto = sum(int(f.size * 1.05) for _, f, _ in lineas)
    y = y_centro - alto // 2
    for texto, f, alfa in lineas:
        x = (W - d.textlength(texto, font=f)) / 2
        d.text((x, y), texto, font=f, fill=alfa)
        y += int(f.size * 1.05)
    return img


def render(tomas, salida, cierre_png=None, cierre_seg=2.5, y_centro=0.24, crf=19):
    global _sesion
    _sesion = _sesion or new_session('u2net_human_seg')
    salida = Path(salida); tmp = salida.parent / (salida.stem + '_tmp'); tmp.mkdir(exist_ok=True)
    audios, t0, grupos_tl = [], 0.0, []
    clips_cortos = []
    for k, (clip, wav) in enumerate(tomas):
        pal = _palabras(wav); fin = pal[-1][2] + 0.3
        for g in _grupos(pal):
            grupos_tl.append([(p, a + t0, b + t0) for p, a, b in g])
        clips_cortos.append((clip, fin)); audios.append((wav, fin)); t0 += fin
    total = t0
    # video: decodifica, recorta persona, compone letras detrás
    proc = subprocess.Popen([FF, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                             '-c:v', 'libx264', '-preset', 'fast', '-crf', str(crf), '-pix_fmt', 'yuv420p', str(tmp / 'video.mp4')],
                            stdin=subprocess.PIPE)
    t = 0.0; n = 0
    for clip, fin in clips_cortos:
        c = av.open(str(clip)); ultimo = None; tl = 0.0
        frames = [fr.to_image() for fr in c.decode(video=0)]
        fps_src = float(c.streams.video[0].average_rate or 24)
        while tl < fin:
            idx = min(int(tl * fps_src), len(frames) - 1)
            img = frames[idx].convert('RGB').resize((W, H), Image.LANCZOS)
            if idx != ultimo:
                chico = img.resize((W // 2, H // 2))
                mask = remove(chico, session=_sesion, only_mask=True, post_process_mask=True).resize((W, H), Image.BILINEAR)
                ultimo = idx
            activo = [g for g in grupos_tl if g[0][1] - 0.05 <= t <= g[-1][2] + 0.35]
            if activo:
                letras = _capa(activo[-1], t, int(H * y_centro))
                base = np.asarray(img).astype(np.float32)
                al = np.asarray(letras).astype(np.float32)[..., None] / 255
                fondo = base * (1 - al * 0.92) + 255 * al * 0.92
                m = np.asarray(mask).astype(np.float32)[..., None] / 255
                comp = base * m + fondo * (1 - m)
                frame = comp.astype(np.uint8)
            else:
                frame = np.asarray(img)
            proc.stdin.write(frame.tobytes()); n += 1
            tl += 1 / FPS; t += 1 / FPS
    if cierre_png:
        cierre = np.asarray(Image.open(cierre_png).convert('RGB').resize((W, H)))
        for _ in range(int(cierre_seg * FPS)):
            proc.stdin.write(cierre.tobytes())
        total += cierre_seg
    proc.stdin.close(); proc.wait()
    # audio: voces limpias en secuencia + silencio del cierre
    entradas = sum([['-i', str(w)] for w, _ in audios], [])
    filtro = ''.join(f'[{i}:a]atrim=0:{fin:.2f},apad=whole_dur={fin:.2f}[a{i}];' for i, (_, fin) in enumerate(audios))
    filtro += ''.join(f'[a{i}]' for i in range(len(audios))) + f'concat=n={len(audios)}:v=0:a=1,apad=whole_dur={total:.2f},loudnorm=I=-15:TP=-1.5[a]'
    subprocess.run([FF, '-v', 'error', '-y', '-i', str(tmp / 'video.mp4'), *entradas, '-filter_complex', filtro, '-map', '0:v', '-map', '[a]',
                    '-c:v', 'copy', '-c:a', 'aac', '-ar', '44100', '-ac', '2', '-b:a', '160k', '-t', f'{total:.2f}', str(tmp / 'hd.mp4')], check=True)
    subprocess.run([FF, '-v', 'error', '-y', '-i', str(tmp / 'hd.mp4'), '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264',
                    '-profile:v', 'main', '-level', '3.1', '-pix_fmt', 'yuv420p', '-preset', 'slow', '-crf', '21', '-c:a', 'copy',
                    '-movflags', '+faststart', str(salida)], check=True)
    return salida, total
