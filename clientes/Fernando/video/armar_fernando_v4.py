"""Fernando (Anegocios) v4 «carrusel»: lo que pidió, sin él generado con IA («me veo muy falso»). Diapositivas con SUS fotos reales (él en su escritorio, impresora, lector,
rollos y el kit de su video) que entran en el momento en que su voz clonada los menciona. Uso: python3 armar_fernando_v4.py"""
import subprocess, sys
from pathlib import Path
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/XV')
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageOps
from armar_xv import fu, tex

AQUI = Path(__file__).resolve().parent
CL = AQUI.parent / 'whatsapp' / 'del_cliente'
FF = imageio_ffmpeg.get_ffmpeg_exe()
TMP = Path('/tmp/claude-1000/-workspaces-Nexusv2-0launch18octubre/22fc94f1-5b92-44e4-9296-5a2e47cda3a3/scratchpad/fer'); TMP.mkdir(parents=True, exist_ok=True)
MUSICA = AQUI.parents[1] / 'XV' / 'musica_suave_s7.wav'
W, H = 1080, 1920
X = 0.25   # duración del deslizado entre diapositivas
TARJ = 3.4
VOCES = ['F1', 'F2', 'F3', 'F4', 'F5']


def ff(a):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1800:])


def dur(p):
    r = subprocess.run([FF, '-hide_banner', '-i', str(p)], capture_output=True, text=True).stderr
    h, m, s = [l for l in r.splitlines() if 'Duration' in l][0].split('Duration: ')[1].split(',')[0].split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)


def diapo(im, ruta, fondo=(10, 30, 70), caja=None):
    """foto centrada sobre su propio fondo desenfocado (nunca estirada)."""
    im = im.convert('RGB')
    bg = ImageOps.fit(im, (W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(40))
    bg = Image.blend(bg, Image.new('RGB', (W, H), fondo), 0.45)
    fg = ImageOps.contain(im, caja or (960, 1250), Image.LANCZOS)
    m = Image.new('L', fg.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, fg.width, fg.height), 36, fill=255)
    bg.paste(fg, ((W - fg.width) // 2, 330 + (1250 - fg.height) // 2), m)
    bg.save(ruta)


def tarjeta(ruta):
    img = Image.new('RGB', (W, H), (12, 30, 60)); d = ImageDraw.Draw(img)
    def c(t, y, tam, col, peso='Black'):
        f = fu(tam, peso)
        while d.textlength(t, font=f) > W - 110: tam -= 2; f = fu(tam, peso)
        d.text(((W - d.textlength(t, font=f)) / 2, y), t, font=f, fill=col)
    c('ANEGOCIOS', 560, 130, (255, 255, 255)); c('PUNTO DE VENTA PARA TU NEGOCIO · CDMX', 720, 44, (255, 200, 70), 'Bold')
    t = 'ESCRÍBEME POR WHATSAPP'; f = fu(50, 'ExtraBold'); an = d.textlength(t, font=f) + 110
    d.rounded_rectangle(((W - an) / 2, 860, (W + an) / 2, 990), 65, fill=(37, 211, 102)); d.text(((W - an) / 2 + 55, 895), t, font=f, fill=(255, 255, 255))
    c('55 7645 6707', 1060, 96, (255, 200, 70))
    img.save(ruta)


def precio(ruta):
    img = Image.open(CL / 'image_09_10-20_1842.jpg').convert('RGB')
    diapo(img, ruta, caja=(900, 900))


def main():
    kit = Image.open(TMP / 'kit_full.png').convert('RGB')
    P = lambda n: Image.open(CL / n)
    yo = P('image_16_10-20_1845.jpg'); w, h = yo.size                       # él en su escritorio (16:9): recorte vertical centrado en su cara
    yo_v = yo.crop((int(w * 0.18), 0, int(w * 0.18) + int(h * 9 / 16 * 1.0), h)) if False else yo.crop((int(w * 0.25), 0, int(w * 0.25) + int(h * 0.75), h))
    SL = {'yo': yo_v, 'soft': kit.crop((0, 640, 560, 1230)), 'imp': P('image_03_10-20_1842.jpg'), 'lec': P('image_07_10-20_1842.jpg'),
          'kit': kit.crop((0, 560, 1080, 1800)), 'capa': P('image_11_10-20_1845.jpg')}
    for k, v in SL.items(): diapo(v, TMP / f'd_{k}.png', caja=(900, 1250) if k in ('yo', 'capa', 'kit') else (900, 1000))
    precio(TMP / 'd_precio.png'); tarjeta(TMP / 'd_tarj.png')
    ds = [dur(AQUI / 'voz' / f'{v}.mp3') + 0.35 for v in VOCES]
    T = [0]
    for d in ds: T.append(T[-1] + d)
    # (diapositiva, inicio, texto)  — cada una dura hasta que entra la siguiente
    S = [('yo', T[0], ['¿YA TIENES COMPUTADORA', 'EN TU NEGOCIO?']),
         ('soft', T[1], ['PUNTO DE VENTA', 'SOFTWARE ANEGOCIOS']), ('imp', T[1] + 2.5, ['IMPRESORA', 'DE TICKETS']), ('lec', T[1] + 3.8, ['LECTOR', 'DE CÓDIGOS']),
         ('kit', T[2], ['$3,500 MXN', 'SOFTWARE · IMPRESORA · LECTOR · ROLLOS']), ('precio', T[2] + 3.6, ['INCLUYE ROLLOS', 'LISTO PARA VENDER']),
         ('capa', T[3], ['TE CAPACITO', 'EN TU NEGOCIO']), ('tarj', T[4], None)]
    TOTAL = T[-1] + TARJ
    ini = [s[1] for s in S] + [TOTAL]
    ent, fl = [], ''
    for i, (n, a, _) in enumerate(S):
        L = ini[i + 1] - a + (X if i < len(S) - 1 else 0)
        ent += ['-framerate', '30', '-loop', '1', '-t', f'{L + 0.1:.2f}', '-i', str(TMP / f'd_{n}.png')]
        fl += (f'[{i}:v]scale=1188:2112,zoompan=z=\'min(1.0+0.0006*on,1.06)\':x=\'(iw-iw/zoom)/2\':y=\'(ih-ih/zoom)/2\':d=1:s={W}x{H}:fps=30,'
               f'setsar=1,format=yuv420p,trim=duration={L:.2f},setpts=PTS-STARTPTS,fps=30,settb=1/30[s{i}];')
    cur = 's0'
    for i in range(1, len(S)):
        fl += f'[{cur}][s{i}]xfade=transition=slideleft:duration={X}:offset={ini[i] - X:.2f}[x{i}];'; cur = f'x{i}'
    j0 = len(S)
    textos = [(s[2], s[1], ini[i + 1]) for i, s in enumerate(S) if s[2]]
    for j, (lin, a, z) in enumerate(textos):
        p = TMP / f't{j}.png'; tex(lin, p, 1470, tam=70); ent += ['-loop', '1', '-t', f'{TOTAL:.1f}', '-i', str(p)]
        fl += f"[{cur}][{j0 + j}:v]overlay=0:0:enable='between(t,{a + 0.15:.2f},{z - 0.05:.2f})'[o{j}];"; cur = f'o{j}'
    a0 = j0 + len(textos)
    ent += ['-i', str(MUSICA)] + [x for v in VOCES for x in ('-i', str(AQUI / 'voz' / f'{v}.mp3'))]
    fl += f"[{a0}:a]aresample=44100,aloop=loop=-1:size=2147483647,volume=0.18,afade=t=in:st=0:d=0.6,afade=t=out:st={TOTAL - 1.2:.2f}:d=1.2,atrim=0:{TOTAL:.2f}[m];"
    fl += ''.join(f"[{a0 + 1 + i}:a]aresample=44100,adelay={int((T[i] + 0.15) * 1000)}|{int((T[i] + 0.15) * 1000)}[v{i}];" for i in range(len(VOCES)))
    fl += '[m]' + ''.join(f'[v{i}]' for i in range(len(VOCES))) + f'amix=inputs={len(VOCES) + 1}:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]'
    hd = TMP / 'hd.mp4'; sal = AQUI / 'Anegocios_Fernando_v4_carrusel.mp4'
    ff(ent + ['-filter_complex', fl, '-map', f'[{cur}]', '-map', '[a]', '-t', f'{TOTAL:.2f}', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', str(hd)])
    ff(['-i', str(hd), '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-pix_fmt', 'yuv420p', '-crf', '24', '-preset', 'slow', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(sal)])
    print(sal, sal.stat().st_size // 1024, 'KB', f'{TOTAL:.1f}s')


if __name__ == '__main__':
    main()
