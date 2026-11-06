"""Subtítulos de palabras gigantes al estilo de los reels de realtor de referencia: 1 o 2 palabras a la vez, enormes, blancas con borde, y la palabra clave
de cada frase en color. Toma los tiempos de cada palabra con faster-whisper. Uso: from kinetic import palabras, pngs"""
import subprocess
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageDraw
import sys
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/XV')
from armar_xv import fu

FF = imageio_ffmpeg.get_ffmpeg_exe()
_modelo = None


def palabras(wav, texto=None):
    """[(palabra, inicio, fin)] de un audio. Con `texto` (el guion real) se usan sus palabras con los tiempos de Whisper, porque Whisper se equivoca
    en nombres propios («Tomatlán no es promesa» lo oyó «Tomadla en nuestra mesa»); si no cuadra el número de palabras, se reparten en el tiempo hablado."""
    global _modelo
    if _modelo is None:
        from faster_whisper import WhisperModel
        _modelo = WhisperModel('medium', device='cpu', compute_type='int8')
    a = np.frombuffer(subprocess.run([FF, '-v', 'error', '-i', str(wav), '-f', 'f32le', '-ac', '1', '-ar', '16000', '-'], capture_output=True).stdout, np.float32)
    segs, _ = _modelo.transcribe(a, language='es', word_timestamps=True)
    ws = [(w.word.strip(), w.start, w.end) for s in segs for w in s.words if w.word.strip()]
    if not texto or not ws:
        return ws
    reales = texto.split()
    if len(reales) == len(ws):
        return [(r, a0, b0) for r, (_, a0, b0) in zip(reales, ws)]
    t0, t1 = ws[0][1], ws[-1][2]; paso = (t1 - t0) / len(reales)
    return [(r, t0 + i * paso, t0 + (i + 1) * paso) for i, r in enumerate(reales)]


def grupos(ws, max_chars=13):
    """Junta palabras de 2 en 2 mientras quepan; cada grupo dura hasta que empieza el siguiente."""
    out, i = [], 0
    while i < len(ws):
        g = [ws[i]]
        if i + 1 < len(ws) and len(ws[i][0]) + len(ws[i + 1][0]) + 1 <= max_chars and not ws[i][0].endswith(('.', ',', ':', '?', '!')):
            g.append(ws[i + 1])
        out.append(g); i += len(g)
    # termina 0.03 s antes del siguiente para que dos grupos nunca se encimen en el mismo cuadro
    return [(' '.join(w for w, _, _ in g), g[0][1], (out[k + 1][0][1] - 0.03 if k + 1 < len(out) else g[-1][2] + 0.3)) for k, g in enumerate(out)]


def pngs(grupos_, clave, carpeta, W, H, y, tam=150, color=(255, 255, 255), resalte=(255, 145, 20)):
    """Un PNG transparente por grupo; las palabras que estén en `clave` van en color. Devuelve [(ruta, inicio, fin)]."""
    rutas = []
    for k, (texto, a, b) in enumerate(grupos_):
        img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
        limpio = texto.upper()
        f = fu(tam, 'Black')
        while d.textlength(limpio, font=f) > W - 80: f = fu(f.size - 4, 'Black')
        x = (W - d.textlength(limpio, font=f)) / 2
        for w in limpio.split(' '):
            c = resalte if w.strip('.,:¿?¡!').lower() in clave else color
            d.text((x, y), w, font=f, fill=c, stroke_width=max(4, f.size // 22), stroke_fill=(10, 10, 12))
            x += d.textlength(w + ' ', font=f)
        p = carpeta / f'k{k:03d}.png'; img.save(p); rutas.append((p, a, b))
    return rutas
