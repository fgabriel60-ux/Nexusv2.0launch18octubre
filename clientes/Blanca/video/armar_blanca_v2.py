"""Hablar...Hablando (Blanca Cruz): v2: ella habla con su voz clonada 1.15× (2 tomas H3 de la foto de escritorio que mandó) + escenas reales de sus terapias (su Instagram) + cierre con su logo, 9:16.
Uso: python3 armar_blanca.py"""
import subprocess, sys
from pathlib import Path
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/XV')
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageOps
from armar_xv import fu, tex

AQUI = Path(__file__).resolve().parent
IG = AQUI.parent / 'instagram'
FF = imageio_ffmpeg.get_ffmpeg_exe()
TMP = Path('/tmp/claude-1000/-workspaces-Nexusv2-0launch18octubre/7f4b01e6-9d5b-409e-acca-ec7fedd1520c/scratchpad/blanca_v2'); TMP.mkdir(parents=True, exist_ok=True)
W, H = 1080, 1920
DA, DB, DC, TARJ = 8.05, 10.71, 3.92, 3.5
# escenas reales de terapia mientras suena la parte B: (video, inicio)
ESCENAS = [('Dc6zVCrBynG', 3.0), ('Dc6TzbKhPHh', 4.0), ('DcygsDrhMj2', 1.0), ('DdDS3mFhEPZ', 14.0)]
DE = DB / len(ESCENAS)
T_B, T_C = DA, DA + DB
TOTAL = DA + DB + DC + TARJ
TEXTOS = [(['ARTICULACIÓN', 'RETRASO EN EL HABLA'], T_B + 0.2, T_B + 2 * DE, 1420),
          (['AUTISMO · NIÑOS SORDOS', 'DESDE 1 AÑO HASTA ADULTOS'], T_B + 2 * DE + 0.1, T_B + DB, 1420),
          (['AGENDA LA VALORACIÓN', 'DE TU HIJO'], T_C + 0.3, T_C + DC, 1420)]


def ff(a):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1800:])


def tarjeta(ruta):
    img = Image.new('RGB', (W, H), (255, 255, 255)); d = ImageDraw.Draw(img)
    logo = Image.open(AQUI.parent / 'whatsapp' / 'del_cliente' / 'img_4.jpg').convert('RGB'); logo = logo.resize((860, 860), Image.LANCZOS)
    img.paste(logo, ((W - 860) // 2, 330))
    def c(t, y, tam, col, peso='Black'):
        f = fu(tam, peso)
        while d.textlength(t, font=f) > W - 110: tam -= 2; f = fu(tam, peso)
        d.text(((W - d.textlength(t, font=f)) / 2, y), t, font=f, fill=col)
    c('BLANCA CRUZ SOLÍS', 1250, 64, (24, 72, 160)); c('TERAPIA DE LENGUAJE, HABLA Y COMUNICACIÓN', 1345, 36, (40, 120, 60), 'Bold')
    t = 'ESCRÍBEME POR WHATSAPP'; f = fu(50, 'ExtraBold'); an = d.textlength(t, font=f) + 110
    d.rounded_rectangle(((W - an) / 2, 1460, (W + an) / 2, 1590), 65, fill=(37, 211, 102)); d.text(((W - an) / 2 + 55, 1495), t, font=f, fill=(255, 255, 255))
    img.save(ruta)


def main():
    tarjeta(TMP / 'tarjeta.png')
    voz = TMP / 'voz.wav'
    ff(['-i', str(AQUI / 'voz' / 'bl_A2.mp3'), '-i', str(AQUI / 'voz' / 'bl_B2.mp3'), '-i', str(AQUI / 'voz' / 'bl_C2.mp3'), '-filter_complex',
        f'[0:a]aresample=44100,apad=whole_dur={DA}[a0];[1:a]aresample=44100,apad=whole_dur={DB}[a1];[2:a]aresample=44100[a2];[a0][a1][a2]concat=n=3:v=0:a=1,apad=whole_dur={TOTAL:.2f}[a]', '-map', '[a]', str(voz)])
    ent = ['-i', str(AQUI / 'tomas_v2' / 'B1_gancho.mp4')]
    for v, ini in ESCENAS:
        ent += ['-ss', str(ini), '-t', f'{DE + .2:.2f}', '-i', str(IG / f'{v}.mp4')]
    ent += ['-i', str(AQUI / 'tomas_v2' / 'B2_cierre.mp4'), '-loop', '1', '-t', str(TARJ), '-i', str(TMP / 'tarjeta.png')]
    n = len(ESCENAS)
    fl = f'[0:v]scale={W}:{H}:flags=lanczos,fps=30,setsar=1,format=yuv420p,tpad=stop_mode=clone:stop_duration=1,trim=duration={DA},setpts=PTS-STARTPTS[c0];'
    for i in range(n):
        fl += (f'[{i + 1}:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps=30,setsar=1,format=yuv420p,'
               f'tpad=stop_mode=clone:stop_duration=1,trim=duration={DE:.2f},setpts=PTS-STARTPTS[e{i}];')
    fl += f'[{n + 1}:v]scale={W}:{H}:flags=lanczos,fps=30,setsar=1,format=yuv420p,tpad=stop_mode=clone:stop_duration=1,trim=duration={DC},setpts=PTS-STARTPTS[c2];'
    fl += f'[{n + 2}:v]scale={W}:{H},fps=30,setsar=1,format=yuv420p[c3];'
    fl += '[c0]' + ''.join(f'[e{i}]' for i in range(n)) + f'[c2][c3]concat=n={n + 3}:v=1:a=0[base];'
    cur, base = 'base', n + 3
    for k, (lin, a, b, y) in enumerate(TEXTOS):
        p = TMP / f't{k}.png'; tex(lin, p, y, tam=72); ent += ['-loop', '1', '-t', f'{TOTAL:.1f}', '-i', str(p)]
        fl += f"[{cur}][{base + k}:v]overlay=0:0:enable='between(t,{a:.2f},{b:.2f})'[o{k}];"; cur = f'o{k}'
    ent += ['-i', str(voz)]
    fl += f"[{base + len(TEXTOS)}:a]loudnorm=I=-14:TP=-1.5[a]"
    hd = TMP / 'blanca_hd.mp4'; sal = AQUI / 'Hablar_Hablando_Blanca_v2.mp4'
    ff(ent + ['-filter_complex', fl, '-map', f'[{cur}]', '-map', '[a]', '-t', f'{TOTAL:.2f}', '-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', str(hd)])
    ff(['-i', str(hd), '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-pix_fmt', 'yuv420p', '-crf', '24', '-preset', 'slow', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(sal)])
    print(sal, sal.stat().st_size // 1024, 'KB', f'{TOTAL:.1f}s')


if __name__ == '__main__':
    main()
