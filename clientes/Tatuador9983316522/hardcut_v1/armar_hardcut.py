"""Tatuador (Adrián, Cancún) · HARD CUT EDIT v1 (30 oct): como el reel de referencia que mandó (18.9 s, cortes secos al ritmo, oscuro).
SOLO su material real (sus 12 videos de WhatsApp), sin su cara hecha con IA (él lo pidió: en el gremio del tatuaje la IA quita credibilidad).
Beat propio (beat_techo de Guillermo, 125 bpm): intro 0-5 s con 2 tomas + gancho, luego un corte cada 2 golpes (0.96 s), tarjeta final con precio y WhatsApp."""
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
WA = AQUI.parent / 'whatsapp'
V = lambda n: WA / f'1029_{n}_el_video.mp4'
BEAT = AQUI.parents[1] / 'Guillermo/techo_20261029/salida_v6_caen/beat_techo.wav'
FUENTE = '/workspaces/Nexusv2.0launch18octubre/visionagenciaIAV2.0-main 2/entregables/modelos_modal/fuentes/Montserrat.ttf'
TMP = AQUI / 'tmp'; TMP.mkdir(exist_ok=True)
W, H, FPS = 720, 1280, 30
ROJO = (196, 30, 46)
INTRO, CORTE, N_CORTES, TARJ = 2.5, 0.96, 15, 3.0
# (video, segundo de inicio, texto encima o None)
TOMAS = [(V('181224'), 3.0, '¿TU PRÓXIMO TATUAJE?'), (V('180319'), 4.0, 'QUE SEA ÚNICO'),
         (V('180310'), 5.0, None), (V('180320'), 2.0, None), (V('181226'), 3.0, 'DISEÑO PERSONALIZADO'), (V('180322'), 2.0, None),
         (V('180327'), 3.0, None), (V('180321'), 5.0, 'TU IDEA'), (V('180312'), 2.0, None), (V('180318'), 3.0, 'TU ESTILO'),
         (V('181223'), 4.0, None), (V('180626'), 2.0, 'TU HISTORIA'), (V('181224'), 14.0, None), (V('180319'), 10.0, None),
         (V('180320'), 8.0, 'CENTRO DE CANCÚN'), (V('181226'), 8.0, None), (V('180310'), 11.0, 'TE ATIENDO HASTA TARDE')]


def ff(a):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1500:])


def fu(t, peso=900):
    f = ImageFont.truetype(FUENTE, t)
    try: f.set_variation_by_axes([peso])
    except Exception: pass
    return f


def capa(txt, ruta):
    im = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(im)
    d.text((W / 2, 46), 'TATUAJES · CANCÚN', font=fu(26, 800), fill=(255, 255, 255, 220), anchor='mt', stroke_width=3, stroke_fill=(0, 0, 0, 200))
    if txt:
        f = fu(56, 900); ls, l = [], ''
        for w in txt.split():
            if d.textlength((l + ' ' + w).strip(), font=f) > 600: ls.append(l); l = w
            else: l = (l + ' ' + w).strip()
        ls.append(l); y = H * 0.5 - 34 * (len(ls) - 1)
        for ln in ls: d.text((W / 2, y), ln, font=f, fill='white', anchor='mm', stroke_width=8, stroke_fill=ROJO); y += 68
    im.save(ruta)


def tarjeta(ruta):
    im = Image.new('RGB', (W, H), (10, 8, 10)); d = ImageDraw.Draw(im)
    c = lambda t, y, s, col, p=900: d.text((W / 2, y), t, font=fu(s, p), fill=col, anchor='mt')
    c('TATUAJES', 300, 44, (220, 220, 220), 700); c('DISEÑO ÚNICO', 370, 74, (255, 255, 255)); c('Y PERSONALIZADO', 460, 54, ROJO)
    c('Sesiones desde $1,000', 575, 44, (255, 255, 255), 800); c('Estudio profesional · centro de Cancún', 640, 28, (170, 170, 170), 500)
    a = 520; d.rounded_rectangle(((W - a) / 2, 760, (W + a) / 2, 860), 50, fill=(37, 211, 102)); c('Escríbeme por WhatsApp', 790, 36, (255, 255, 255), 800)
    c('998 331 6522', 920, 64, (255, 255, 255))
    im.save(ruta)


segs = []
for i, (src, ini, txt) in enumerate(TOMAS):
    dur = INTRO if i < 2 else CORTE
    capa(txt, TMP / f'c{i}.png'); s = TMP / f's{i}.mp4'
    grade = 'eq=contrast=1.18:saturation=1.12:brightness=-0.03,vignette=PI/4.5'
    zoom = f"scale={int(W*1.08)}:{int(H*1.08)},crop={W}:{H}" if i % 2 else f'scale={W}:{H}'
    ff(['-ss', str(ini), '-i', str(src), '-i', str(TMP / f'c{i}.png'), '-filter_complex',
        f'[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},{zoom},fps={FPS},{grade},setsar=1[v];[v][1:v]overlay=0:0,format=yuv420p[o]',
        '-map', '[o]', '-t', f'{dur:.3f}', '-an', '-c:v', 'libx264', '-crf', '18', str(s)])
    segs.append(s)
tarjeta(TMP / 'tarjeta.png')
ff(['-loop', '1', '-t', str(TARJ), '-i', str(TMP / 'tarjeta.png'), '-vf', f'fps={FPS},format=yuv420p', '-c:v', 'libx264', str(TMP / 'sT.mp4')]); segs.append(TMP / 'sT.mp4')
(TMP / 'lista.txt').write_text(''.join(f"file '{s}'\n" for s in segs))
ff(['-f', 'concat', '-safe', '0', '-i', str(TMP / 'lista.txt'), '-c:v', 'libx264', '-crf', '20', '-pix_fmt', 'yuv420p', str(TMP / 'mudo.mp4')])
total = 2 * INTRO + CORTE * (len(TOMAS) - 2) + TARJ
# música: beat completo (0-10 s) + su parte fuerte (5-10 s) en loop hasta cubrir el video, con fade final
ff(['-i', str(BEAT), '-i', str(BEAT), '-filter_complex', f'[1:a]atrim=5:10,asetpts=PTS-STARTPTS,aloop=loop=3:size=220500[l];[0:a][l]concat=n=2:v=0:a=1,atrim=0:{total:.2f},afade=t=out:st={total-1.2:.2f}:d=1.2[a]',
    '-map', '[a]', str(TMP / 'musica.wav')])
sal = AQUI / 'Tatuador_hardcut_v1.mp4'
ff(['-i', str(TMP / 'mudo.mp4'), '-i', str(TMP / 'musica.wav'), '-c:v', 'libx264', '-profile:v', 'main', '-crf', '21', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', str(sal)])
print(sal, round(total, 1), 's')
