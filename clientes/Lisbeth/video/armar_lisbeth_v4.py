"""Lisbeth v4: TODO el video con su terreno NUEVO (el que mandó el 24 oct), ya sin el terreno de la v22 y sin el audio que H3 inventa en la subida y en la
construcción (se oía una voz rara). Gancho con su voz frente a su terreno → sube como dron a SU foto aérea real → «Así podría verse» → su narración de la v22
sobre SUS fotos y videos reales del terreno nuevo → ella frente a su terreno pidiendo WhatsApp. Uso: python3 armar_lisbeth_v4.py"""
import subprocess, sys
from pathlib import Path
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/XV')
import imageio_ffmpeg
from PIL import Image, ImageOps
import armar_xv
from armar_xv import tex

AQUI = Path(__file__).resolve().parent
NUEVAS = AQUI.parent / 'whatsapp' / 'nuevas_1024'
V3 = AQUI / 'v3'
FF = imageio_ffmpeg.get_ffmpeg_exe()
TMP = Path('/tmp/claude-1000/-workspaces-Nexusv2-0launch18octubre/3f2c6b79-5aa7-409f-95e2-6c1cf5560d47/scratchpad/lisbeth_v4'); TMP.mkdir(parents=True, exist_ok=True)
MUSICA = AQUI.parents[1] / 'XV' / 'musica_suave_s7.wav'
W, H = 1080, 1920
D_HABLA, VEL = 4.7, 1.5
# (tipo, archivo, inicio o None, duración, texto)
TOMAS = [
    ('video', V3 / 'LIS3_habla.mp4', 0.0, D_HABLA, ['TOMATLÁN, JALISCO', 'TERRENO REAL']),
    ('video', V3 / 'LIS3_sube_v.mp4', 0.0, 4.0 / VEL, None),
    ('video', V3 / 'LIS3_construye_v.mp4', 0.0, 4.0, ['ASÍ PODRÍA VERSE', 'VISUALIZACIÓN']),
    # de aquí en adelante va su narración de la v22 (38 s), una toma por frase
    ('video', NUEVAS / '24_130401_video.mp4', 0.0, 6.68, ['TERRENOS DESDE 300 M²', 'CON VISTA A LAS MONTAÑAS']),
    ('foto', NUEVAS / '24_130402_image.jpg', None, 5.88, ['A 20 MINUTOS', 'DE LA PLAYA']),
    ('foto', V3 / 'L3_aereo_v.png', None, 5.88, ['TECNOLÓGICO, CENTRAL', 'Y HOSPITAL MUY CERCA']),
    ('foto', NUEVAS / '24_130406_image.jpg', None, 5.36, ['LA ZONA YA', 'SE ESTÁ POBLANDO']),
    ('video', NUEVAS / '24_130328_video.mp4', 0.0, 6.32, ['DOCUMENTOS EN REGLA', 'INVIERTE CON TRANQUILIDAD']),
    ('foto', NUEVAS / '24_130403_image.jpg', None, 4.0, ['NO COMPRES PROMESAS', 'VEN A CONOCERLO']),
    ('foto', V3 / 'L3_calle.png', None, 4.0, ['ESCRÍBEME', 'POR WHATSAPP']),
]
T_GANCHO = sum(t[3] for t in TOMAS[:3])


def ff(a):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1800:])


def main():
    armar_xv.W, armar_xv.H = W, H
    TOTAL = sum(t[3] for t in TOMAS)
    ent, fl = [], ''
    AJ = f'scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},unsharp=5:5:0.5,eq=contrast=1.05:saturation=1.12'
    for i, (tipo, ruta, ini, d, _) in enumerate(TOMAS):
        if tipo == 'video':
            vel = f',setpts=PTS/{VEL}' if 'sube' in ruta.name else ''
            ent += ['-ss', str(ini), '-i', str(ruta)]
            fl += f'[{i}:v]{AJ}{vel},fps=30,setsar=1,format=yuv420p,tpad=stop_mode=clone:stop_duration=3,trim=duration={d:.2f},setpts=PTS-STARTPTS[c{i}];'
        else:   # foto con acercamiento lento
            f = TMP / f'f{i}.jpg'
            ImageOps.fit(ImageOps.exif_transpose(Image.open(ruta)).convert('RGB'), (int(W * 1.1), int(H * 1.1)), Image.LANCZOS).save(f, quality=95)
            ent += ['-loop', '1', '-t', f'{d:.2f}', '-i', str(f)]
            fl += (f"[{i}:v]crop={W}:{H}:x='(iw-{W})/2*(1-t/{d:.2f})':y='(ih-{H})/2*(1-t/{d:.2f})',fps=30,setsar=1,format=yuv420p,"
                   f"trim=duration={d:.2f},setpts=PTS-STARTPTS[c{i}];")
    k = len(TOMAS)
    fl += ''.join(f'[c{i}]' for i in range(k)) + f'concat=n={k}:v=1:a=0[base];'
    cur, t0, b = 'base', 0.0, k
    for j, (_, _, _, d, lin) in enumerate(TOMAS):
        if lin:
            p = TMP / f't{j}.png'; tex(lin, p, 1380, tam=74); ent += ['-loop', '1', '-t', f'{TOTAL:.1f}', '-i', str(p)]
            fl += f"[{cur}][{b}:v]overlay=0:0:enable='between(t,{t0 + 0.1:.2f},{t0 + d - 0.05:.2f})'[o{j}];"; cur = f'o{j}'; b += 1
        t0 += d
    # audio: su voz del gancho + música suave en la parte IA (sin el audio de H3) → narración de la v22 con su música
    ent += ['-i', str(AQUI / 'voz' / 'L_gancho.mp3'), '-i', str(MUSICA), '-i', str(AQUI.parent / 'referencia' / 'v22.mp4')]
    fl += (f"[{b}:a]aresample=44100,apad=whole_dur={T_GANCHO:.2f}[g];[{b + 1}:a]aresample=44100,volume=0.22,atrim=0:{T_GANCHO:.2f},afade=t=out:st={T_GANCHO - 0.6:.2f}:d=0.6[m];"
           f"[g][m]amix=inputs=2:duration=longest:normalize=0,atrim=0:{T_GANCHO:.2f}[p1];[{b + 2}:a]aresample=44100[p2];[p1][p2]concat=n=2:v=0:a=1,loudnorm=I=-14:TP=-1.5[a]")
    hd = TMP / 'hd.mp4'; sal = AQUI / 'Lisbeth_v4_terreno_nuevo.mp4'
    ff(ent + ['-filter_complex', fl, '-map', f'[{cur}]', '-map', '[a]', '-t', f'{TOTAL:.2f}', '-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', str(hd)])
    ff(['-i', str(hd), '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-pix_fmt', 'yuv420p', '-crf', '23', '-preset', 'slow', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(sal)])
    print(sal, sal.stat().st_size // 1024, 'KB', f'{TOTAL:.1f}s')


if __name__ == '__main__':
    main()
