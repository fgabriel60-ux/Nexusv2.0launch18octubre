"""Pone mensajes de WhatsApp llegando en la pantalla verde del celular de Guillermo (T6_gui_mensaje) — pedido de Carlos 30 oct:
«que cuando Guillermo muestre el teléfono se vean cómo llegan mensajes». Sigue la pantalla cuadro por cuadro (verde brillante) y respeta lo que la tapa."""
import subprocess, json
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
SRC, OUT = AQUI / 'salida' / 'T6_gui_mensaje.mp4', AQUI / 'salida' / 'T6_gui_mensaje_chat.mp4'
FUENTE = '/workspaces/Nexusv2.0launch18octubre/visionagenciaIAV2.0-main 2/entregables/modelos_modal/fuentes/Montserrat.ttf'
MSJ = [(0.3, 'Hola, vi su anuncio. ¿Hace zaguanes?'), (1.2, '¿Cuánto cuesta una cortina?'), (2.1, 'Quiero cotizar una pérgola'), (3.0, '¿Me visita mañana?'), (3.8, 'Me interesa el portón negro')]


def fu(t, p=700):
    f = ImageFont.truetype(FUENTE, t)
    try: f.set_variation_by_axes([p])
    except Exception: pass
    return f


def pantalla(t, W=300, H=600):
    im = Image.new('RGB', (W, H), (236, 229, 221)); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 70), fill=(7, 94, 84)); d.text((16, 22), 'Clientes', font=fu(26, 800), fill='white')
    n = sum(1 for s, _ in MSJ if t >= s)
    if n: d.rounded_rectangle((W - 64, 20, W - 14, 52), 16, fill=(37, 211, 102)); d.text((W - 39, 36), str(n), font=fu(22, 900), fill='white', anchor='mm')
    y = 86
    for s, m in MSJ:
        if t < s: break
        a = min(1, (t - s) / 0.25)
        f = fu(19, 600); lineas, l = [], ''
        for w in m.split():
            if d.textlength((l + ' ' + w).strip(), font=f) > W - 70: lineas.append(l); l = w
            else: l = (l + ' ' + w).strip()
        lineas.append(l); h = 18 + 24 * len(lineas)
        x0 = 12 - int((1 - a) * 40)
        d.rounded_rectangle((x0, y, W - 40, y + h), 14, fill='white')
        for k, ln in enumerate(lineas): d.text((x0 + 12, y + 9 + 24 * k), ln, font=f, fill=(30, 30, 30))
        y += h + 12
    return im


info = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v', '-show_entries', 'stream=width,height,r_frame_rate', '-of', 'json', str(SRC)], capture_output=True, text=True).stdout)['streams'][0]
W, H = info['width'], info['height']; n_, d_ = map(int, info['r_frame_rate'].split('/')); fps = n_ / d_
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(SRC), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
frames = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(fps), '-i', '-', '-c:v', 'libx264', '-crf', '17', '-pix_fmt', 'yuv420p', str(OUT)], stdin=subprocess.PIPE)
for i, a in enumerate(frames):
    a = a.copy(); r, g, b = a[..., 0].astype(int), a[..., 1].astype(int), a[..., 2].astype(int)
    m = (g > 170) & (r < 110) & (b < 110) & (g - r > 90)
    m[int(H * 0.72):] = False; m[:, int(W * 0.6):] = False   # solo la zona del celular (no la barda verde de abajo)
    ys, xs = np.where(m)
    if len(xs) > 500:
        x0, x1 = np.percentile(xs, [1, 99]).astype(int); y0, y1 = np.percentile(ys, [1, 99]).astype(int)
        img = np.asarray(pantalla(i / fps).resize((x1 - x0 + 1, y1 - y0 + 1)))
        caja = a[y0:y1 + 1, x0:x1 + 1].astype(int)
        blanco = (caja.min(axis=2) > 175)   # adornos blancos de la pantalla original (no la mano café)
        sub = m[y0:y1 + 1, x0:x1 + 1] | blanco
        for _ in range(2):   # ensancha la máscara 2 px para quitar el borde verde
            sub = sub | np.roll(sub, 1, 0) | np.roll(sub, -1, 0) | np.roll(sub, 1, 1) | np.roll(sub, -1, 1)
        verde = (caja[..., 1] - np.maximum(caja[..., 0], caja[..., 2]) > 40)
        sub = sub & (verde | blanco | m[y0:y1 + 1, x0:x1 + 1] | (np.abs(caja - caja.mean(axis=2, keepdims=True)).max(axis=2) < 25))
        a[y0:y1 + 1, x0:x1 + 1][sub] = img[sub]
    enc.stdin.write(a.tobytes())
enc.stdin.close(); enc.wait(); print(OUT, len(frames), 'cuadros')
