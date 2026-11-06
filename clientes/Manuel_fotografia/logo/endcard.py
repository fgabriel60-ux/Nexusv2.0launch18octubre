"""End card animado de Hunab Ku Fotografía (logo real de su página de Facebook, perfil.jpg), 1080x1920, pensado para 8 golpes (~3.8 s a 125 BPM).
0.0-0.6 s  luces doradas (bokeh) que giran y se juntan al centro
0.3-1.4 s  el símbolo Hunab Ku entra girando 540° con resplandor verde
1.4 s      FLASH de cámara (en el golpe) y aparece el parche completo con «Hunab Ku Fotografía» con rebote
1.5-2.5 s  barrido de luz sobre el logo
1.9-2.7 s  suben los textos: AGENDA TU FECHA · XV AÑOS · BODAS · EVENTOS · botón de WhatsApp
resto      el logo respira y siguen las chispas
Uso como módulo: endcard(t, fondo) -> Image RGB; o `python3 endcard.py` para un mp4 de prueba."""
import sys, math, subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/XV')
from armar_xv import fu

AQUI = Path(__file__).resolve().parent
W, H = 1080, 1920
VERDE, ORO, VERDE_WA = (150, 230, 40), (255, 215, 110), (37, 211, 102)
CY = 760                                    # centro vertical del logo


def _prepara():
    im = Image.open(AQUI / 'perfil.jpg').convert('RGB')
    a = np.asarray(im).astype(np.float32)
    lum = a.max(axis=2)
    alfa = np.clip((lum - 28) / 50, 0, 1)                            # el fondo es casi negro: máscara suave del parche
    import scipy.ndimage as nd
    lleno = nd.binary_fill_holes(nd.binary_closing(alfa > 0.5, iterations=4))          # las letras y el símbolo negros son PARTE del parche
    alfa = np.maximum(alfa, nd.binary_erosion(lleno, iterations=3).astype(np.float32))
    alfa = np.asarray(Image.fromarray((alfa * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2))).astype(np.float32) / 255
    rgba = np.dstack([a, alfa * 255]).astype(np.uint8)
    logo = Image.fromarray(rgba, 'RGBA')
    esc = 780 / logo.width
    logo = logo.resize((int(logo.width * esc), int(logo.height * esc)), Image.LANCZOS)
    # disco del símbolo (centro y radio medidos sobre perfil.jpg 716x720)
    cx, cy, r = 335 * esc, 255 * esc, 172 * esc
    m = Image.new('L', logo.size, 0); ImageDraw.Draw(m).ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
    disco = logo.copy(); disco.putalpha(ImageChops.multiply(logo.getchannel('A'), m))
    disco = disco.crop((int(cx - r), int(cy - r), int(cx + r), int(cy + r)))
    return logo, disco, (cx, cy)


LOGO, DISCO, CENTRO_DISCO = _prepara()
RNG = np.random.default_rng(11)
NP = 90
P_ANG, P_RAD, P_TAM, P_FASE = RNG.uniform(0, 2 * np.pi, NP), RNG.uniform(380, 900, NP), RNG.uniform(6, 22, NP), RNG.uniform(0, 6.3, NP)


def suave(x): x = min(1, max(0, x)); return x * x * (3 - 2 * x)
def sale(x): x = min(1, max(0, x)); return 1 - (1 - x) ** 3
def rebote(x):
    x = min(1, max(0, x)); return 1 + 0.12 * math.sin(x * math.pi * 2.2) * (1 - x) if x < 1 else 1


def resplandor(img, radio, fuerza):
    g = img.filter(ImageFilter.GaussianBlur(radio))
    if fuerza != 1: g.putalpha(g.getchannel('A').point(lambda v: int(min(255, v * fuerza))))
    return g


def boton(d, y, a):
    t = 'ESCRÍBENOS POR WHATSAPP'; f = fu(48, 'ExtraBold'); an = d.textlength(t, font=f) + 110
    d.rounded_rectangle(((W - an) / 2, y, (W + an) / 2, y + 120), 60, fill=VERDE_WA + (int(255 * a),))
    d.text(((W - an) / 2 + 55, y + 33), t, font=f, fill=(255, 255, 255, int(255 * a)))


def centrado(d, t, y, tam, col, a, peso='Black'):
    f = fu(tam, peso)
    while d.textlength(t, font=f) > W - 110: tam -= 2; f = fu(tam, peso)
    d.text(((W - d.textlength(t, font=f)) / 2, y), t, font=f, fill=col + (int(255 * a),), stroke_width=3, stroke_fill=(0, 0, 0, int(160 * a)))


def endcard(t, fondo=None, dur=3.83):
    base = (fondo.convert('RGB').resize((W, H)).filter(ImageFilter.GaussianBlur(28)) if fondo is not None else Image.new('RGB', (W, H), (10, 12, 8)))
    base = Image.blend(base, Image.new('RGB', (W, H), (4, 6, 4)), 0.72).convert('RGBA')
    capa = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    # chispas doradas que giran y se juntan al centro (y luego quedan flotando)
    junta = sale(t / 1.3)
    for i in range(NP):
        ang = P_ANG[i] + t * (1.6 - 0.9 * junta) + 0.3 * math.sin(P_FASE[i] + t)
        rad = P_RAD[i] * (1 - 0.72 * junta) + 40 * math.sin(P_FASE[i] + 2 * t)
        x, y = W / 2 + rad * math.cos(ang), CY + rad * 0.9 * math.sin(ang)
        s = P_TAM[i] * (0.6 + 0.4 * abs(math.sin(P_FASE[i] + 3 * t)))
        al = int(200 * min(1, t / 0.3) * (0.55 + 0.45 * math.sin(P_FASE[i] + 4 * t)))
        d.ellipse((x - s, y - s, x + s, y + s), fill=ORO + (max(0, al),) if i % 3 else VERDE + (max(0, al),))
    base.alpha_composite(resplandor(capa, 10, 1.6)); base.alpha_composite(capa)
    lx, ly = (W - LOGO.width) // 2, CY - LOGO.height // 2
    if t < 1.4:   # el símbolo entra girando
        u = sale((t - 0.3) / 1.1)
        if u > 0:
            esc = 0.25 + 0.75 * u; rot = 540 * (1 - u)
            dd = DISCO.resize((max(2, int(DISCO.width * esc)), max(2, int(DISCO.height * esc))), Image.LANCZOS).rotate(rot, Image.BICUBIC, expand=True)
            dd.putalpha(dd.getchannel('A').point(lambda v: int(v * min(1, u * 1.6))))
            x = lx + CENTRO_DISCO[0] - dd.width / 2; y = ly + CENTRO_DISCO[1] - dd.height / 2
            g = resplandor(dd, 26, 2.2); base.alpha_composite(g, (int(x), int(y))); base.alpha_composite(dd, (int(x), int(y)))
    else:         # parche completo con rebote, resplandor verde y respiración
        u = (t - 1.4) / 0.6
        esc = rebote(u) * (1 + 0.012 * math.sin((t - 1.4) * 3.0))
        lg = LOGO.resize((int(LOGO.width * esc), int(LOGO.height * esc)), Image.LANCZOS)
        x, y = (W - lg.width) // 2, CY - lg.height // 2
        g = resplandor(lg, 40, 0.8 + 1.2 * max(0, 1 - u)); base.alpha_composite(g, (x, y)); base.alpha_composite(lg, (x, y))
        k = (t - 1.5) / 1.0                                   # barrido de luz diagonal, recortado al logo
        if 0 < k < 1:
            br = Image.new('L', lg.size, 0); bd = ImageDraw.Draw(br); xb = -300 + k * (lg.width + 600)
            bd.polygon([(xb, 0), (xb + 140, 0), (xb - 160, lg.height), (xb - 300, lg.height)], fill=170)
            br = ImageChops.multiply(br.filter(ImageFilter.GaussianBlur(25)), lg.getchannel('A'))
            luz = Image.new('RGBA', lg.size, (255, 255, 230, 0)); luz.putalpha(br); base.alpha_composite(luz, (x, y))
    # FLASH de cámara en el golpe
    if 1.36 <= t < 1.75:
        f = 1 - (t - 1.36) / 0.39
        base = Image.blend(base, Image.new('RGBA', (W, H), (255, 255, 255, 255)), 0.85 * f * f)
    # textos
    tx = Image.new('RGBA', (W, H), (0, 0, 0, 0)); td = ImageDraw.Draw(tx)
    for j, (txt, yy, tam, col, peso) in enumerate([('AGENDA TU FECHA', 1250, 92, (255, 255, 255), 'Black'),
                                                    ('XV AÑOS · BODAS · EVENTOS', 1370, 46, ORO, 'Bold'),
                                                    ('FOTO + VIDEO', 1440, 52, (255, 255, 255), 'ExtraBold')]):
        a = suave((t - 1.9 - 0.12 * j) / 0.35)
        if a > 0: centrado(td, txt, yy + 40 * (1 - a), tam, col, a, peso)
    a = suave((t - 2.35) / 0.35)
    if a > 0:
        boton(td, 1570 + 40 * (1 - a), a)
    base.alpha_composite(tx)
    return base.convert('RGB')


if __name__ == '__main__':
    FF = __import__('imageio_ffmpeg').get_ffmpeg_exe()
    sal = AQUI / 'HunabKu_endcard.mp4'; FPS = 30; DUR = 4.5
    p = subprocess.Popen([FF, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-profile:v', 'main', '-pix_fmt', 'yuv420p', '-crf', '20', str(sal)], stdin=subprocess.PIPE)
    for k in range(int(DUR * FPS)): p.stdin.write(np.asarray(endcard(k / FPS)).tobytes())
    p.stdin.close(); p.wait(); print(sal)
