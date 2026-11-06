"""Subtítulos virales al estilo del gancho de Kelsie Blevins (DbvIz5iRf_M): palabras normales delgadas y blancas a la altura de la cabeza y DETRÁS de la
persona (se recorta con rembg cuadro por cuadro), la palabra clave enorme en negritas y amarilla al frente, y cada grupo entra con desenfoque + escala.
Uso: from kelsie import quemar; quemar(video, palabras, claves, salida)  ·  palabras = kinetic.palabras(wav, texto) con los tiempos de la voz."""
import subprocess, sys
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/XV')
from armar_xv import fu

FF = imageio_ffmpeg.get_ffmpeg_exe()
AMARILLO = (255, 197, 49)
ENTRADA = 0.18   # segundos de la animación de entrada


def _grupos(ws, claves):
    """Corta en grupos: una palabra clave cierra su grupo (con hasta 2 palabras normales antes); sin clave, grupos de 2 palabras."""
    out, act = [], []
    for w in ws:
        act.append(w)
        es_clave = w[0].strip('.,:;¡!¿?').lower() in claves
        if es_clave or len(act) == 2 or w[0].endswith(('.', ',', '!', '?')):
            out.append(act); act = []
    if act: out.append(act)
    return [(g, g[0][1], (out[k + 1][0][1] - 0.03) if k + 1 < len(out) else g[-1][2] + 0.4) for k, g in enumerate(out)]


def _capa(grupo, claves, W):
    """Devuelve (capa_detras, capa_frente) RGBA del tamaño del texto, ya centradas en el ancho W."""
    normales = ' '.join(w for w, _, _ in grupo if w.strip('.,:;¡!¿?').lower() not in claves)
    clave = ' '.join(w for w, _, _ in grupo if w.strip('.,:;¡!¿?').lower() in claves)
    detras = frente = None
    if normales:
        tam = 64 if clave else 96
        f = fu(tam, 'Light')
        while ImageDraw.Draw(Image.new('L', (1, 1))).textlength(normales, font=f) > W - 60: tam -= 4; f = fu(tam, 'Light')
        img = Image.new('RGBA', (W, int(tam * 1.4))); d = ImageDraw.Draw(img)
        d.text(((W - d.textlength(normales, font=f)) / 2, 0), normales, font=f, fill=(255, 255, 255, 255))
        sombra = Image.new('RGBA', img.size); sombra.putalpha(img.getchannel('A').filter(ImageFilter.GaussianBlur(6)).point(lambda a: a * 0.45))
        detras = Image.alpha_composite(sombra, img)
    if clave:
        tam = 150
        f = fu(tam, 'Black')
        while ImageDraw.Draw(Image.new('L', (1, 1))).textlength(clave.upper(), font=f) > W - 50: tam -= 6; f = fu(tam, 'Black')
        img = Image.new('RGBA', (W, int(tam * 1.3))); d = ImageDraw.Draw(img)
        x = (W - d.textlength(clave.upper(), font=f)) / 2
        d.text((x + 4, 6), clave.upper(), font=f, fill=(120, 70, 0, 200))           # sombra dura para el relieve
        d.text((x, 0), clave.upper(), font=f, fill=AMARILLO + (255,))
        frente = img
    return detras, frente


def _animar(capa, p):
    """p de 0 a 1 durante la entrada: escala 1.18→1, desenfoque 10→0, opacidad 0→1."""
    if capa is None or p >= 1: return capa
    e = float(1 - (1 - p) ** 3)   # float de Python: Pillow truena con escalares de numpy
    s = 1.18 - 0.18 * e
    w, h = capa.size
    c = capa.resize((int(w * s), int(h * s)), Image.LANCZOS).filter(ImageFilter.GaussianBlur(10 * (1 - e)))
    out = Image.new('RGBA', (w, h)); out.paste(c, ((w - c.width) // 2, (h - c.height) // 2), c)
    a = out.getchannel('A').point(lambda v: int(v * e)); out.putalpha(a)
    return out


def quemar(video, ws, claves, salida, fps=30, hasta=None):
    from rembg import new_session, remove
    sesion = new_session('u2net_human_seg')
    info = subprocess.run([FF, '-i', str(video)], capture_output=True, text=True).stderr
    import re
    W, H = [int(x) for x in re.search(r'Video: .*?(\d{2,5})x(\d{2,5})', info).groups()]
    claves = {c.lower() for c in claves}
    grupos = [(g, a, b, *_capa(g, claves, W)) for g, a, b in _grupos(ws, claves)]
    lee = subprocess.Popen([FF, '-v', 'error', '-i', str(video), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-r', str(fps), '-'], stdout=subprocess.PIPE)
    esc = subprocess.Popen([FF, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(fps), '-i', '-', '-i', str(video),
                            '-map', '0:v', '-map', '1:a?', '-c:v', 'libx264', '-crf', '17', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-c:a', 'copy', '-shortest', str(salida)],
                           stdin=subprocess.PIPE)
    n = 0
    while True:
        raw = lee.stdout.read(W * H * 3)
        if len(raw) < W * H * 3: break
        t = n / fps; n += 1
        cuadro = Image.frombytes('RGB', (W, H), raw).convert('RGBA')
        activo = [g for g in grupos if g[1] <= t < g[2] and (hasta is None or t < hasta)]
        if activo:
            g, a, b, detras, frente = activo[0]
            p = (t - a) / ENTRADA
            chica = cuadro.convert('RGB').resize((W // 2, H // 2))
            masc = remove(chica, session=sesion, only_mask=True).resize((W, H), Image.BILINEAR)
            filas = np.where(np.array(masc).max(axis=1) > 128)[0]
            cabeza = int(filas[0]) if len(filas) else int(H * 0.2)
            if detras is not None:   # a la altura de la cabeza y detrás de ella
                capa = Image.new('RGBA', (W, H)); y = max(30, cabeza - detras.height // 3 - (frente.height // 2 if frente else 0))
                capa.alpha_composite(_animar(detras, p), (0, y))
                al = np.array(capa.getchannel('A')).astype(np.float32) * (1 - np.array(masc).astype(np.float32) / 255)
                capa.putalpha(Image.fromarray(al.astype(np.uint8)))
                cuadro = Image.alpha_composite(cuadro, capa)
            if frente is not None:   # la clave al frente, a la altura del pecho
                y = min(H - frente.height - 40, cabeza + int(H * 0.16))
                cuadro.alpha_composite(_animar(frente, p), (0, y))
        esc.stdin.write(cuadro.convert('RGB').tobytes())
    esc.stdin.close(); esc.wait(); lee.wait()
    return salida
