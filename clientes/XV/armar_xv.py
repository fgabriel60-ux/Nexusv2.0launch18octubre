"""Reel XV (Manuel Fotografía) · v1 SIN Modal: ffmpeg + PIL. Fórmula de Meta (hook → contexto → proceso → prueba → cierre), 9:16.
Uso: python3 armar_xv.py            → render completo
     python3 armar_xv.py prueba     → solo cuadros de prueba (hoja de contactos)"""
import subprocess, sys, math
from pathlib import Path
import av, imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

AQUI = Path(__file__).resolve().parent
ORI = AQUI / 'originales'
FF = imageio_ffmpeg.get_ffmpeg_exe()
FUENTE = '/workspaces/Nexusv2.0launch18octubre/visionagenciaIAV2.0-main 2/entregables/modelos_modal/fuentes/Montserrat.ttf'
TMP = Path('/tmp/claude-1000/-workspaces-Nexusv2-0launch18octubre/6babdfdf-0126-43a3-a459-73c583442b35/scratchpad/xv'); TMP.mkdir(parents=True, exist_ok=True)
(AQUI / 'final').mkdir(exist_ok=True)
W, H, FPS = 1080, 1920, 30
ORO, VERDE_WA = (232, 190, 110), (37, 211, 102)

# ── línea de tiempo (s) ──
HOOK = 3.0
FOTOS_CTX = ['BV8B6048-Editar', 'BV8B6038-Editar', 'BV8B6090', 'BV8B6220']; D_FOTO = 1.75      # 3 → 10
# (archivo, inicio, centro horizontal 0-1 del recorte vertical)
PROCESO = [('C6801', 50, .48), ('C6755', 35, .75), ('C6801', 65, .45), ('C6801', 140, .45), ('C6771', 10, .40)]; D_CLIP = 3.0   # 10 → 25
FOTOS_PRUEBA = ['BV8B6224', 'BV8B6090', 'BV8B6220', 'BV8B6038-Editar', 'BV8B6048-Editar']; D_CARD = 1.2                       # 25 → 31
FINAL = ('C6801', 170, .62); D_FINAL = 3.0                                                                                     # 31 → 34
D_TARJETA = 3.0                                                                                                                # 34 → 37
TOTAL = HOOK + len(FOTOS_CTX) * D_FOTO + len(PROCESO) * D_CLIP + len(FOTOS_PRUEBA) * D_CARD + D_FINAL + D_TARJETA


def ff(a):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1500:])


def fu(t, peso='Black'):
    f = ImageFont.truetype(FUENTE, t); f.set_variation_by_name(peso); return f


def clip(nombre, ini, cx, dur, salida, lento=1.0):
    if Path(salida).exists(): return
    """Recorte vertical 9:16 de un clip 4K horizontal, centrado en cx (fracción del ancho)."""
    ancho = 2160 * 9 / 16
    x = max(0, min(3840 - ancho, cx * 3840 - ancho / 2))
    vf = f'crop={int(ancho)}:2160:{int(x)}:0,scale={W}:{H}:flags=lanczos,setsar=1,setpts={lento}*PTS,fps={FPS},format=yuv420p'
    ff(['-ss', str(ini), '-i', str(ORI / f'{nombre}.MP4'), '-t', f'{dur / lento:.3f}', '-vf', vf, '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '17', str(salida)])


def foto_vertical(nombre, ancho=W, alto=H):
    im = Image.open(ORI / f'{nombre}.jpg').convert('RGB'); im.draft('RGB', (ancho * 2, alto * 2))
    return ImageOps.fit(im, (ancho, alto), Image.LANCZOS, centering=(.5, .38))


def kenburns(nombre, dur, salida, rev=False):
    if Path(salida).exists(): return
    """Foto con zoom suave (Ken Burns) → clip."""
    base = foto_vertical(nombre, int(W * 1.18), int(H * 1.18)); base.save(TMP / f'kb_{nombre}.png')
    n = int(dur * FPS); z0, z1 = (1.15, 1.0) if rev else (1.0, 1.15)
    ff(['-loop', '1', '-i', str(TMP / f'kb_{nombre}.png'), '-vf',
        f"zoompan=z='{z0}+({z1}-{z0})*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps={FPS},format=yuv420p",
        '-frames:v', str(n), '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '17', str(salida)])


def suave(x): x = max(0, min(1, x)); return x * x * (3 - 2 * x)


def carrusel(salida):
    if Path(salida).exists(): return
    """Prueba: tarjetas con las fotos entregadas que entran deslizándose (álbum / fotos impresas)."""
    fondo = foto_vertical(FOTOS_PRUEBA[0]).filter(ImageFilter.GaussianBlur(40)); fondo = Image.eval(fondo, lambda v: int(v * .35))
    cw, ch = 800, 1180
    tarj = []
    for n in FOTOS_PRUEBA:
        f = foto_vertical(n, cw - 36, ch - 36); c = Image.new('RGBA', (cw, ch), (255, 255, 255, 255)); c.paste(f, (18, 18)); tarj.append(c)
    p = subprocess.Popen([FF, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '17', '-pix_fmt', 'yuv420p', str(salida)], stdin=subprocess.PIPE)
    total = int(D_CARD * len(tarj) * FPS)
    for fr in range(total):
        t = fr / FPS; im = fondo.copy().convert('RGBA'); k = min(len(tarj) - 1, int(t / D_CARD))
        for j in range(k + 1):                                        # tarjetas ya apiladas debajo con ligera rotación
            u = suave((t - j * D_CARD) / 0.35) if j == k else 1.0
            if u <= 0: continue
            rot = [-5, 4, -3, 5, 0][j % 5] * (1 if j < k else 1)
            c = tarj[j].rotate(rot * u if j < k or u >= 1 else rot * u, expand=True, resample=Image.BICUBIC)
            if j == k: x = int(W / 2 - c.width / 2 + (1 - u) * 900 * (1 if j % 2 == 0 else -1)); sc = 1.0
            else: x = int(W / 2 - c.width / 2); sc = 1.0
            sombra = Image.new('RGBA', c.size, (0, 0, 0, 0)); sombra.paste((0, 0, 0, 120), mask=c.getchannel('A')); sombra = sombra.filter(ImageFilter.GaussianBlur(18))
            y = int(H / 2 - c.height / 2 - 40)
            im.alpha_composite(sombra, (x + 10, y + 24)) if 0 <= x < W else None
            im.alpha_composite(c, (max(-c.width, min(W, x)), y)) if x > -c.width and x < W else None
        p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close(); p.wait()


def tex(lineas, ruta, y, tam=84, color=(255, 255, 255), sombra=True, fondo=True):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    if fondo:
        for yy in range(max(0, y - 120), min(H, y + len(lineas) * (tam + 12) + 120)):
            a = int(150 * max(0, 1 - abs(yy - (y + len(lineas) * (tam + 12) / 2)) / (len(lineas) * (tam + 12) / 2 + 120)))
            d.line([(0, yy), (W, yy)], fill=(0, 0, 0, a))
    for i, l in enumerate(lineas):
        f = fu(tam if i == 0 else int(tam * .62), 'Black' if i == 0 else 'Bold')
        while d.textlength(l, font=f) > W - 110: f = fu(f.size - 2, 'Black' if i == 0 else 'Bold')
        yy = y + i * (tam + 12)
        d.text(((W - d.textlength(l, font=f)) / 2, yy), l, font=f, fill=ORO if i else color, stroke_width=6 if sombra else 0, stroke_fill=(15, 10, 10))
    img.save(ruta)


def tarjeta(ruta):
    img = Image.new('RGBA', (W, H), (8, 20, 18, 215)); d = ImageDraw.Draw(img)
    def c(t, y, tam, col, peso='Black'):
        f = fu(tam, peso)
        while d.textlength(t, font=f) > W - 110: tam -= 2; f = fu(tam, peso)
        d.text(((W - d.textlength(t, font=f)) / 2, y), t, font=f, fill=col)
    c('AGENDA TU FECHA', 560, 96, (255, 255, 255)); c('XV AÑOS · BODAS · EVENTOS', 690, 46, ORO, 'Bold')
    c('FOTO + VIDEO', 790, 56, (255, 255, 255), 'ExtraBold')
    t = 'ESCRÍBENOS POR WHATSAPP'; f = fu(50, 'ExtraBold'); a = d.textlength(t, font=f) + 110
    d.rounded_rectangle(((W - a) / 2, 960, (W + a) / 2, 1090), 65, fill=VERDE_WA); d.text(((W - a) / 2 + 55, 995), t, font=f, fill=(255, 255, 255))
    c('MANUEL FOTOGRAFÍA', 1230, 58, ORO)
    img.save(ruta)


def main():
    segs = []
    # 1 hook: giro del vestido en cámara lenta
    s = TMP / 's00.mp4'; clip('C6771', 4.0, .40, HOOK, s, lento=2.0); segs.append(s)
    for i, n in enumerate(FOTOS_CTX):
        s = TMP / f's1{i}.mp4'; kenburns(n, D_FOTO, s, rev=i % 2 == 1); segs.append(s)
    for i, (n, ini, cx) in enumerate(PROCESO):
        s = TMP / f's2{i}.mp4'; clip(n, ini, cx, D_CLIP, s); segs.append(s)
    s = TMP / 's30.mp4'; carrusel(s); segs.append(s)
    s = TMP / 's40.mp4'; clip(*FINAL[:3], D_FINAL + D_TARJETA, s); segs.append(s)

    t_ctx = HOOK; t_proc = t_ctx + len(FOTOS_CTX) * D_FOTO; t_prueba = t_proc + len(PROCESO) * D_CLIP; t_final = t_prueba + len(FOTOS_PRUEBA) * D_CARD; t_tarj = t_final + D_FINAL
    cap = [(['TUS XV AÑOS', 'COMO UNA PELÍCULA'], 0.2, HOOK - .1, 1380),
           (['SESIÓN DE FOTOS XV'], t_ctx + .2, t_proc - .2, 1500),
           (['Y TODA LA FIESTA,', 'CADA MOMENTO'], t_proc + .2, t_prueba - .2, 1440),
           (['TUS FOTOS, TU VIDEO', 'Y TU RECUERDO'], t_prueba + .15, t_final - .15, 1560),
           (['ASÍ SE VIVE TU XV'], t_final + .2, t_tarj - .1, 1500)]
    (TMP / 'lista.txt').write_text(''.join(f"file '{x}'\n" for x in segs))
    entr = ['-f', 'concat', '-safe', '0', '-i', str(TMP / 'lista.txt'), '-ss', '20', '-t', f'{TOTAL:.2f}', '-i', str(ORI / 'C6755.MP4')]
    fl, prev = '', '0:v'
    for k, (l, a, b, y) in enumerate(cap):
        tex(l, TMP / f'c{k}.png', y, 84 if k != 1 else 70); entr += ['-i', str(TMP / f'c{k}.png')]
        fl += f"[{prev}][{2 + k}:v]overlay=0:0:enable='between(t,{a:.2f},{b:.2f})'[o{k}];"; prev = f'o{k}'
    tarjeta(TMP / 'tarjeta.png'); entr += ['-loop', '1', '-i', str(TMP / 'tarjeta.png')]; kt = 2 + len(cap)
    fl += f"[{kt}:v]format=rgba,fade=t=in:st={t_tarj:.2f}:d=0.4:alpha=1[tj];[{prev}][tj]overlay=0:0:enable='gte(t,{t_tarj:.2f})'[v];"
    fl += f"[1:a]loudnorm=I=-15:TP=-1.5,afade=t=in:d=0.4,afade=t=out:st={TOTAL - 1.5:.2f}:d=1.5[a]"
    hd = TMP / 'xv_hd.mp4'; sal = AQUI / 'final' / 'XV_reel_v1.mp4'
    ff(entr + ['-filter_complex', fl, '-map', '[v]', '-map', '[a]', '-t', f'{TOTAL:.2f}', '-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', str(hd)])
    ff(['-i', str(hd), '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-pix_fmt', 'yuv420p', '-crf', '22', '-c:a', 'copy', '-movflags', '+faststart', str(sal)])
    print(sal, sal.stat().st_size // 1024, 'KB', f'{TOTAL:.1f}s')


if __name__ == '__main__':
    main()
