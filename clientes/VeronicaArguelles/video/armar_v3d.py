"""Verónica · reel estilo referencia DfGOIz3z7uZ (monitor en cuarto oscuro con recorrido 3D) — 31 oct 2026.
Torre real → maqueta 3D (Qwen) → cada cuarto real vacío «se decora con IA» con barrida de luz → tarjeta final. Voz clonada f0..f4.
  python3 armar_v3d.py [version]"""
import glob, json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

V = sys.argv[1] if len(sys.argv) > 1 else 'v1'
R = Path('/workspaces/Nexusv2.0launch18octubre/clientes/VeronicaArguelles')
D = R / 'video/v3d_v1'; VOZ = D / 'voz'; OUT = R / f'video/Veronica_recorrido3D_{V}.mp4'
TMP = D / f'tmp_{V}'; TMP.mkdir(exist_ok=True)
FS = sorted(glob.glob(str(R / 'fotos/*.jpg')))
W, H, FPS = 1080, 1920, 30
SX, SY, SW, SH = 70, 560, 940, 529          # pantalla del monitor
B = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'; N = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
f = lambda p, s: ImageFont.truetype(p, s)


def vacio(i):  # mismo recorte que Qwen (ImageOps.fit 1280x720, centro 0.45)
    return ImageOps.fit(Image.open(FS[i]).convert('RGB'), (1280, 720), Image.LANCZOS, centering=(0.5, 0.45))


def deco(n): return Image.open(D / f'{n}.png').convert('RGB').resize((1280, 720), Image.LANCZOS)


def fachada():
    im = Image.open(FS[0]).convert('RGB'); fondo = ImageOps.fit(im, (1280, 720)).filter(ImageFilter.GaussianBlur(30))
    im.thumbnail((1280, 720)); fondo.paste(im, ((1280 - im.width) // 2, 0)); return fondo


def alberca(): return ImageOps.fit(Image.open(FS[2]).convert('RGB'), (1280, 720), Image.LANCZOS)


dur = [float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(VOZ / f'f{i}.wav')], capture_output=True, text=True).stdout) for i in range(5)]
PAUSA = 0.25; ini = [0.3]
for d in dur[:-1]: ini.append(ini[-1] + d + PAUSA)
TOTAL = ini[-1] + dur[-1] + 2.2
SUBS = ["¿Así quieres conocer tu próximo departamento?", "Torre exclusiva en El Charro, Tampico.", "Tres recámaras con baño completo y balcón.",
        "Desde $7,600,000 pesos.", "Escríbeme por WhatsApp\ny te mando la disponibilidad."]

# planos de pantalla: (inicio, fin, tipo, datos)
t0, t1, t2, t3, t4 = ini
P = [(0, t1, 'foto', (fachada(), 'TORRE EL CHARRO · TAMPICO')),
     (t1, t2, 'foto', (deco('D_maqueta'), 'RECORRIDO 3D')),
     (t2, t2 + dur[2] / 2 + .1, 'deco', (vacio(30), deco('S_recamara'), 'RECÁMARA PRINCIPAL')),
     (t2 + dur[2] / 2 + .1, t3, 'deco', (vacio(13), deco('S_bano'), 'BAÑO COMPLETO')),
     (t3, t3 + dur[3] / 2 + .1, 'deco', (vacio(24), deco('S_sala'), 'SALA Y COMEDOR')),
     (t3 + dur[3] / 2 + .1, t4, 'deco', (vacio(16), deco('S_cocina'), 'COCINA')),
     (t4, t4 + 1.6, 'deco', (vacio(12), deco('S_balcon'), 'BALCÓN')),
     (t4 + 1.6, t4 + dur[4] + .3, 'foto', (alberca(), 'AMENIDADES')),
     (t4 + dur[4] + .3, TOTAL + 1, 'tarjeta', None)]


def ui(img, etiqueta, extra=None):
    d = ImageDraw.Draw(img); d.rounded_rectangle((24, 24, 24 + 22 * len(etiqueta) + 40, 78), 12, fill=(15, 15, 18))
    d.text((44, 34), etiqueta, font=f(B, 30), fill='white')
    if extra:
        w = 18 * len(extra) + 36; d.rounded_rectangle((1280 - w - 24, 650, 1256, 700), 12, fill=(15, 15, 18)); d.text((1280 - w - 6, 660), extra, font=f(N, 26), fill=(230, 210, 160))
    return img


def tarjeta():
    im = Image.new('RGB', (1280, 720), (12, 12, 14)); d = ImageDraw.Draw(im)
    for y, t, fo, c in [(150, 'VERÓNICA ARGUELLES', f(B, 78), 'white'), (255, 'ASESORA INMOBILIARIA', f(N, 44), (230, 210, 160)),
                        (360, 'EL CHARRO · TAMPICO · DESDE $7.6 MDP', f(B, 44), 'white'), (480, 'WhatsApp 789 101 5551', f(B, 64), (90, 220, 120))]:
        d.text((640, y), t, font=fo, fill=c, anchor='mm')
    return im


def pantalla(t):
    for a, b, tipo, dat in P:
        if a <= t < b: break
    k = (t - a) / max(b - a, .01); z = 1 + .06 * k
    if tipo == 'tarjeta': return tarjeta()
    if tipo == 'foto':
        im, et = dat; base = im
    else:
        v, dd, et = dat; p = min(max((k - .18) / .5, 0), 1); x = int(1280 * p)
        base = v.copy(); base.paste(dd.crop((0, 0, x, 720)), (0, 0))
        if 0 < p < 1:
            dr = ImageDraw.Draw(base)
            for g in range(14, 0, -2): dr.rectangle((x - g, 0, x + g, 720), outline=None, fill=(255, 240, 200) if g < 4 else None)
            glow = Image.new('RGB', (60, 720), (255, 235, 190)); base.paste(Image.blend(base.crop((max(x - 30, 0), 0, max(x - 30, 0) + 60, 720)), glow, .45), (max(x - 30, 0), 0))
    cw, ch = int(1280 / z), int(720 / z); ox, oy = (1280 - cw) // 2, (720 - ch) // 2
    im = base.crop((ox, oy, ox + cw, oy + ch)).resize((1280, 720), Image.LANCZOS)
    extra = None if tipo == 'foto' else ('ANTES' if p == 0 else 'DECORACIÓN ILUSTRATIVA CON IA')
    return ui(im, et, extra)


FONDO = Image.new('RGB', (W, H), (6, 6, 8))
dr = ImageDraw.Draw(FONDO)
for i in range(60): dr.ellipse((SX - 200 + i * 6, SY - 160 + i * 4, SX + SW + 200 - i * 6, SY + SH + 220 - i * 4), fill=(6 + i // 3, 6 + i // 3, 10 + i // 3))
FONDO = FONDO.filter(ImageFilter.GaussianBlur(40))


def cuadro(n):
    t = n / FPS; im = FONDO.copy()
    sc = pantalla(t).resize((SW, SH), Image.LANCZOS)
    glow = Image.new('RGB', (W, H), (0, 0, 0)); glow.paste(sc.resize((SW // 8, SH // 8)).resize((SW, SH)), (SX, SY))
    im = Image.blend(im, glow.filter(ImageFilter.GaussianBlur(60)), .35)
    im.paste(sc, (SX, SY)); d = ImageDraw.Draw(im)
    d.rectangle((SX - 6, SY - 6, SX + SW + 6, SY + SH + 6), outline=(25, 25, 28), width=6)
    d.text((W // 2, 300), 'Departamento desde $7.6 MDP', font=f(B, 56), fill='white', anchor='mm')
    d.text((W // 2, 375), 'El Charro · Tampico', font=f(N, 40), fill=(220, 220, 220), anchor='mm')
    for i, s in enumerate(SUBS):
        if ini[i] <= t < ini[i] + dur[i] + .15:
            d.multiline_text((W // 2, 1250), s, font=f(B, 48 if len(s) < 34 else 42), fill='white', anchor='mm', align='center', stroke_width=4, stroke_fill='black', spacing=12)
    return im


nf = int(TOTAL * FPS)
p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                      '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '19', str(TMP / 'video.mp4')], stdin=subprocess.PIPE)
for n in range(nf): p.stdin.write(cuadro(n).tobytes())
p.stdin.close(); p.wait()
# audio: voz con pausas + música suave baja
fil = ''.join(f'[{i + 1}:a]adelay={int(ini[i] * 1000)}|{int(ini[i] * 1000)}[v{i}];' for i in range(5))
cmd = ['ffmpeg', '-v', 'error', '-y', '-i', str(TMP / 'video.mp4')] + sum([['-i', str(VOZ / f'f{i}.wav')] for i in range(5)], []) + \
      ['-stream_loop', '-1', '-i', '/workspaces/Nexusv2.0launch18octubre/clientes/XV/musica_suave_s7.wav',
       '-filter_complex', fil + ''.join(f'[v{i}]' for i in range(5)) + f'amix=inputs=5:normalize=0[voz];[6:a]volume=0.12,afade=t=out:st={TOTAL - 1.5}:d=1.5[m];[voz][m]amix=inputs=2:normalize=0,atrim=0:{TOTAL}[a]',
       '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', str(OUT)]
subprocess.run(cmd, check=True); print('listo', OUT, round(TOTAL, 1), 's')
