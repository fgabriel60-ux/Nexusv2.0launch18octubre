"""Subtítulos virales (el estilo que ya se armó con Playfair): por frase, un conector chico en cursiva, la PALABRA PROTAGONISTA enorme en negrita y un remate en cursiva.
Cada palabra entra en el milisegundo en que se dice (opacidad 0→100 y una subida leve) y el grupo se queda hasta que termina la frase. Sin caja: sombra suave para leerse sobre cualquier fondo.
Uso: capas = subs_virales.capas(palabras, carpeta, y=0.8)  →  [(png, inicio, fin_grupo)];  filtro: subs_virales.overlay(capas, cur, primer_indice_png, total) → (entradas, filtro, cur)."""
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
FU = Path(__file__).resolve().parent / 'fuentes'
ESTILOS = {'c': ('PlayfairDisplay-Italic[wght].ttf', b'SemiBold Italic', 76), 'M': ('PlayfairDisplay[wght].ttf', b'Black', 150),
           'r': ('PlayfairDisplay-Italic[wght].ttf', b'SemiBold Italic', 104)}
VACIAS = {'de', 'la', 'el', 'en', 'y', 'a', 'que', 'los', 'las', 'un', 'una', 'con', 'por', 'para', 'es', 'se', 'su', 'al', 'lo', 'del', 'tu', 'te', 'me', 'no', 'si', 'o', 'ya', 'mi'}
_f = {}


def fuente(est, esc=1.0):
    ruta, var, tam = ESTILOS[est]; k = (est, round(tam * esc))
    if k not in _f:
        f = ImageFont.truetype(str(FU / ruta), k[1]); f.set_variation_by_name(var); _f[k] = f
    return _f[k]


def frases(ws, pausa=0.38, max_pal=6):
    out, g = [], []
    for i, w in enumerate(ws):
        g.append(w)
        fin = w[0].endswith(('.', ',', '?', '!', ':', ';')) or len(g) >= max_pal
        if i + 1 < len(ws) and ws[i + 1][1] - w[2] > pausa: fin = True
        if fin or i + 1 == len(ws): out.append(g); g = []
    return out


def protagonista(g):
    pts = [(len(re.sub(r'\W', '', w[0])) + (6 if any(c.isdigit() for c in w[0]) or w[0][:1].isupper() and i else 0) - (8 if re.sub(r'\W', '', w[0]).lower() in VACIAS else 0), i) for i, w in enumerate(g)]
    return max(pts)[1] if len(g) > 2 else len(g) - 1


def capas(ws, carpeta, y=0.80, evitar=(), W=1080, H=1920):
    """evitar: [(inicio, fin)] tramos sin subtítulo (tarjetas con texto propio)."""
    carpeta = Path(carpeta); carpeta.mkdir(parents=True, exist_ok=True); K = W / 1080
    gs = [g for g in frases(ws) if not any(a <= g[0][1] < b for a, b in evitar)]
    res = []
    for gi, g in enumerate(gs):
        p = protagonista(g)
        lineas = [(g[:p], 'c'), ([g[p]], 'M'), (g[p + 1:], 'r')]
        lineas = [(l, e) for l, e in lineas if l]
        fin = min(g[-1][2] + 0.6, gs[gi + 1][0][1] - 0.05) if gi + 1 < len(gs) else g[-1][2] + 0.9
        medidas = []
        for l, e in lineas:
            t = ' '.join(w[0].upper() if e == 'M' else w[0].lower() for w in l)
            esc = K
            while fuente(e, esc).getlength(t) > W * 0.88 and esc > 0.4 * K: esc *= 0.95
            f = fuente(e, esc); asc, desc = f.getmetrics(); medidas.append((f, int((asc + desc) * (0.8 if e == 'M' else 0.92)), t))
        top = H * y - sum(m[1] for m in medidas) / 2
        pos = []
        for (l, e), (f, alto, t) in zip(lineas, medidas):
            x = (W - f.getlength(t)) / 2
            for w in l:
                pal = w[0].upper() if e == 'M' else w[0].lower()
                pos.append((pal, f, x, top, w[1])); x += f.getlength(pal + ' ')
            top += alto
        for pal, f, x, yy, t0 in pos:
            n = len(res)
            sh = Image.new('L', (W, H), 0); ImageDraw.Draw(sh).text((x, yy + 6 * K), pal, font=f, fill=200)
            sh = sh.filter(ImageFilter.GaussianBlur(11 * K))
            img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); img.paste((0, 0, 0, 255), mask=sh)
            ImageDraw.Draw(img).text((x, yy), pal, font=f, fill=(255, 255, 255, 255))
            ruta = carpeta / f's{n:03d}.png'; img.save(ruta); res.append((ruta, t0, fin))
    return res


def overlay(res, cur, b, total, rise=18):
    ent, fl = [], ''
    for j, (ruta, a, z) in enumerate(res):
        ent += ['-loop', '1', '-framerate', '30', '-t', f'{total:.1f}', '-i', str(ruta)]
        fl += (f"[{b + j}:v]format=rgba,fade=t=in:st={a:.3f}:d=0.17:alpha=1[w{j}];"
               f"[{cur}][w{j}]overlay=x=0:y='{rise}*(1-min(1,(t-{a:.3f})/0.17))':enable='between(t,{a:.3f},{z:.3f})'[sv{j}];")
        cur = f'sv{j}'
    return ent, fl, cur
