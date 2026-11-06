"""Lisbeth · dron en Tomatlán: habla (su voz) → lanza el dron → desde el aire el lote se construye → casa terminada → cierre hablando → tarjeta, 9:16.
Uso: python3 armar_lisbeth.py"""
import subprocess, sys
from pathlib import Path
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/XV')
import imageio_ffmpeg
from PIL import Image, ImageDraw
from armar_xv import fu, tex

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
TMP = Path('/tmp/claude-1000/-workspaces-Nexusv2-0launch18octubre/7f4b01e6-9d5b-409e-acca-ec7fedd1520c/scratchpad/lisbeth'); TMP.mkdir(parents=True, exist_ok=True)
MUSICA = AQUI.parents[1] / 'XV' / 'musica_suave_s7.wav'
W, H = 1080, 1920
# (toma, segundos que se usan)
SEG = [('L0_habla', 5.85), ('L1_lanza', 3.2), ('L2_obra', 4.6), ('L3_casa', 4.6), ('L4_cierre', 3.13)]
TARJ = 3.2
T = [0]
for _, d in SEG: T.append(T[-1] + d)
TOTAL = T[-1] + TARJ
VOCES = [('L_A', 0.0), ('L_B', T[2] + 0.2), ('L_C', T[4])]
TEXTOS = [(['TOMATLÁN, JALISCO', 'TERRENOS CON VISTA A LA MONTAÑA'], 0.4, T[1], 1420),
          (['A 20 MIN DE LA PLAYA'], T[2] + 0.3, T[3], 1420),
          (['LOTES DESDE 300 m²', 'CONSTRUYE LA CASA QUE IMAGINAS'], T[3] + 0.1, T[4], 1420)]


def ff(a):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1800:])


def tarjeta(ruta):
    img = Image.new('RGB', (W, H), (16, 42, 38)); d = ImageDraw.Draw(img)
    def c(t, y, tam, col, peso='Black'):
        f = fu(tam, peso)
        while d.textlength(t, font=f) > W - 110: tam -= 2; f = fu(tam, peso)
        d.text(((W - d.textlength(t, font=f)) / 2, y), t, font=f, fill=col)
    c('LISBETH', 600, 130, (255, 255, 255)); c('ASESORA DE TERRENOS', 760, 52, (232, 196, 120), 'Bold')
    c('TOMATLÁN, JALISCO', 840, 52, (255, 255, 255), 'Bold')
    t = 'ESCRÍBEME POR WHATSAPP'; f = fu(50, 'ExtraBold'); an = d.textlength(t, font=f) + 110
    d.rounded_rectangle(((W - an) / 2, 990, (W + an) / 2, 1120), 65, fill=(37, 211, 102)); d.text(((W - an) / 2 + 55, 1025), t, font=f, fill=(255, 255, 255))
    img.save(ruta)


def main():
    tarjeta(TMP / 'tarjeta.png')
    ent, fl = [], ''
    for i, (n, d) in enumerate(SEG):
        ent += ['-i', str(AQUI / 'tomas' / f'{n}.mp4')]
        fl += f'[{i}:v]scale={W}:{H}:flags=lanczos,fps=30,setsar=1,format=yuv420p,tpad=stop_mode=clone:stop_duration=1,trim=duration={d},setpts=PTS-STARTPTS[c{i}];'
    k = len(SEG)
    ent += ['-loop', '1', '-t', str(TARJ), '-i', str(TMP / 'tarjeta.png')]
    fl += f'[{k}:v]scale={W}:{H},fps=30,setsar=1,format=yuv420p[c{k}];' + ''.join(f'[c{i}]' for i in range(k + 1)) + f'concat=n={k + 1}:v=1:a=0[base];'
    cur, base = 'base', k + 1
    for j, (lin, a, b, y) in enumerate(TEXTOS):
        p = TMP / f't{j}.png'; tex(lin, p, y, tam=72); ent += ['-loop', '1', '-t', f'{TOTAL:.1f}', '-i', str(p)]
        fl += f"[{cur}][{base + j}:v]overlay=0:0:enable='between(t,{a:.2f},{b:.2f})'[o{j}];"; cur = f'o{j}'
    a0 = base + len(TEXTOS)
    ent += ['-i', str(MUSICA)] + [x for v, _ in VOCES for x in ('-i', str(AQUI / 'voz' / f'{v}.mp3'))]
    fl += f"[{a0}:a]aresample=44100,aloop=loop=-1:size=2147483647,volume=0.2,afade=t=in:st=0:d=0.8,afade=t=out:st={TOTAL - 1.2:.2f}:d=1.2,atrim=0:{TOTAL:.2f}[m];"
    fl += ''.join(f"[{a0 + 1 + i}:a]aresample=44100,adelay={int(s * 1000)}|{int(s * 1000)}[v{i}];" for i, (_, s) in enumerate(VOCES))
    fl += '[m]' + ''.join(f'[v{i}]' for i in range(len(VOCES))) + f'amix=inputs={len(VOCES) + 1}:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]'
    hd = TMP / 'lisbeth_hd.mp4'; sal = AQUI / 'Lisbeth_dron_Tomatlan_v1.mp4'
    ff(ent + ['-filter_complex', fl, '-map', f'[{cur}]', '-map', '[a]', '-t', f'{TOTAL:.2f}', '-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', str(hd)])
    ff(['-i', str(hd), '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-pix_fmt', 'yuv420p', '-crf', '24', '-preset', 'slow', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(sal)])
    print(sal, sal.stat().st_size // 1024, 'KB', f'{TOTAL:.1f}s')


if __name__ == '__main__':
    main()
