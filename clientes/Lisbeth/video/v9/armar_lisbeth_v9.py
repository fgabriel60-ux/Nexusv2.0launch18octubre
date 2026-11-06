"""Lisbeth v9 (30 oct, pedido de Carlos + Glimmer 5/10): menos mapa, más terreno REAL. Misma voz de la v8.
Se conservan el gancho (0-4.5 s, ella en la carretera) y el cierre (38.5 s→fin); todo lo de en medio se cambia por SUS fotos y videos del terreno
(WhatsApp 24 oct) con letreros por frase. Se quita «Y recuerda, no compres promesas» (35.5-38.5 s, Glimmer). La presa Cajón de Peña: vistas aéreas
del valle hasta que llegue el video de la presa que mandó ella."""
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
V8 = AQUI.parent / 'Lisbeth_v8_tomatlan.mp4'
WA = AQUI.parents[1] / 'whatsapp'
F = lambda n: WA / f'24_{n}_el_image.jpg'
VID = lambda n: WA / f'24_{n}_el_video.mp4'
FUENTE = '/workspaces/Nexusv2.0launch18octubre/visionagenciaIAV2.0-main 2/entregables/modelos_modal/fuentes/Montserrat.ttf'
TMP = AQUI / 'tmp'; TMP.mkdir(exist_ok=True)
W, H, FPS = 720, 1280, 30
VERDE, ORO = (16, 64, 48), (236, 200, 90)
# (inicio, fin en la v8, [(fuente, inicio en la fuente)], letrero grande, letrero chico)
TRAMOS = [(4.5, 6.6, [(VID('200401'), 2.0)], 'ASÍ EMPIEZA TU PATRIMONIO', ''),
          (6.6, 13.2, [(F('200402'), 0), (F('200210'), 0), (F('200328'), 0)], 'TERRENOS DESDE 300 M²', 'Vista a las montañas · a 20 min de la playa'),
          (13.2, 21.2, [(F('200406'), 0), (F('200405'), 0), (F('200407'), 0)], 'A MENOS DE 2 KM', 'Nuevo tecnológico · central de autobuses · hospital'),
          (21.2, 23.7, [(F('200404'), 0)], 'LA ZONA YA SE ESTÁ POBLANDO', ''),
          (23.7, 31.0, [(F('200408'), 0), (F('200407'), 0)], 'ZONA CON MUCHO POTENCIAL', 'Cerca del aeropuerto de Chalacatepec y la presa Cajón de Peña'),
          (31.0, 35.5, [(VID('200328'), 1.0)], 'DOCUMENTOS EN REGLA', 'Invierte con tranquilidad')]
QUITAR = (35.5, 38.5)


def ff(a):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1500:])


def fu(t, p=900):
    f = ImageFont.truetype(FUENTE, t)
    try: f.set_variation_by_axes([p])
    except Exception: pass
    return f


def capa(grande, chico, ruta):
    im = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(im)
    f = fu(34, 800); t = 'TOMATLÁN, JALISCO'; w = d.textlength(t, font=f) + 90; x0 = (W - w) / 2
    d.rounded_rectangle((x0, 120, x0 + w, 182), 31, fill=VERDE + (232,), outline=ORO + (255,), width=3); d.text((W / 2, 151), t, font=f, fill='white', anchor='mm')
    y = 930
    g = fu(50, 900); ls, l = [], ''
    for p in grande.split():
        if d.textlength((l + ' ' + p).strip(), font=g) > 640: ls.append(l); l = p
        else: l = (l + ' ' + p).strip()
    ls.append(l)
    for ln in ls: d.text((W / 2, y), ln, font=g, fill='white', anchor='mm', stroke_width=7, stroke_fill=VERDE); y += 62
    if chico:
        tc = 28
        while d.textlength(chico, font=fu(tc, 700)) > 640: tc -= 1
        c = fu(tc, 700); w = d.textlength(chico, font=c) + 40
        d.rounded_rectangle(((W - w) / 2, y - 6, (W + w) / 2, y + 44), 14, fill=(0, 0, 0, 150)); d.text((W / 2, y + 19), chico, font=c, fill=ORO, anchor='mm')
    im.save(ruta)


def toma(src, ini, seg, ruta, k):
    if src.suffix == '.jpg':
        n = int(seg * FPS) + 1; z = 'min(zoom+0.0010,1.12)' if k % 2 == 0 else 'if(eq(on,1),1.12,max(zoom-0.0010,1))'
        ff(['-i', str(src), '-vf', f"scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2},zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps={FPS},setsar=1",
            '-frames:v', str(n), '-an', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', str(ruta)])
    else:
        ff(['-ss', str(ini), '-i', str(src), '-t', f'{seg:.3f}', '-vf', f'scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},setsar=1', '-an', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', str(ruta)])


partes = []
ff(['-i', str(V8), '-t', '4.5', '-vf', f'fps={FPS},setsar=1', '-an', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', str(TMP / 'a_gancho.mp4')]); partes.append(TMP / 'a_gancho.mp4')
for i, (a, b, fuentes, g, c) in enumerate(TRAMOS):
    seg = (b - a) / len(fuentes); sub = []
    for k, (src, ini) in enumerate(fuentes):
        p = TMP / f't{i}_{k}.mp4'; toma(src, ini, seg, p, k); sub.append(p)
    (TMP / f'l{i}.txt').write_text(''.join(f"file '{p}'\n" for p in sub))
    ff(['-f', 'concat', '-safe', '0', '-i', str(TMP / f'l{i}.txt'), '-c', 'copy', str(TMP / f'b{i}.mp4')])
    capa(g, c, TMP / f'c{i}.png')
    ff(['-i', str(TMP / f'b{i}.mp4'), '-i', str(TMP / f'c{i}.png'), '-filter_complex', '[0:v][1:v]overlay=0:0,format=yuv420p', '-t', f'{b - a:.3f}', '-an', '-c:v', 'libx264', '-crf', '18', str(TMP / f'm{i}.mp4')])
    partes.append(TMP / f'm{i}.mp4')
ff(['-ss', str(QUITAR[1]), '-i', str(V8), '-vf', f'fps={FPS},setsar=1', '-an', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', str(TMP / 'z_cierre.mp4')]); partes.append(TMP / 'z_cierre.mp4')
(TMP / 'lista.txt').write_text(''.join(f"file '{p}'\n" for p in partes))
ff(['-f', 'concat', '-safe', '0', '-i', str(TMP / 'lista.txt'), '-c:v', 'libx264', '-crf', '20', '-pix_fmt', 'yuv420p', str(TMP / 'mudo.mp4')])
ff(['-i', str(V8), '-filter_complex', f"[0:a]atrim=0:{QUITAR[0]},asetpts=PTS-STARTPTS[x];[0:a]atrim={QUITAR[1]},asetpts=PTS-STARTPTS[y];[x][y]concat=n=2:v=0:a=1[a]", '-map', '[a]', str(TMP / 'audio.wav')])
sal = AQUI.parent / 'Lisbeth_v9_terreno_real.mp4'
ff(['-i', str(TMP / 'mudo.mp4'), '-i', str(TMP / 'audio.wav'), '-c:v', 'libx264', '-profile:v', 'main', '-crf', '22', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k', '-shortest', '-movflags', '+faststart', str(sal)])
print(sal)
