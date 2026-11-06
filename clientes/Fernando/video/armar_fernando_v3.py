"""Fernando (Anegocios) v3: guion corregido por él («¿Ya tienes computadora en tu negocio…?») con SU voz clonada + 5 escenas de capacitación en una tiendita
(Qwen + H3 con su cara) + tarjeta de WhatsApp, 9:16. Uso: python3 armar_fernando_v3.py"""
import subprocess, sys
from pathlib import Path
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/XV')
import imageio_ffmpeg
from PIL import Image, ImageDraw
from armar_xv import fu, tex

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
TMP = Path('/tmp/claude-1000/-workspaces-Nexusv2-0launch18octubre/7f4b01e6-9d5b-409e-acca-ec7fedd1520c/scratchpad/fernando'); TMP.mkdir(parents=True, exist_ok=True)
MUSICA = AQUI.parents[1] / 'XV' / 'musica_suave_s7.wav'
W, H = 1080, 1920
# (escena, voz, texto en pantalla) — cada escena dura lo que su frase + 0.35 s
ESC = [('FER_1', 'F1', ['¿YA TIENES COMPUTADORA', 'EN TU NEGOCIO?']), ('FER_2', 'F2', ['TE LA COMPLETO', 'PUNTO DE VENTA + IMPRESORA + LECTOR']),
       ('FER_3', 'F3', ['$3,500 MXN', 'SOFTWARE · IMPRESORA · LECTOR · ROLLOS']), ('FER_5', 'F4', ['TE CAPACITO', 'EN TU TIENDA']), ('FER_4', 'F5', ['ESCRÍBEME', 'POR WHATSAPP'])]
TARJ = 3.4


def dur(p):
    r = subprocess.run([FF, '-hide_banner', '-i', str(p)], capture_output=True, text=True).stderr
    h, m, s = [l for l in r.splitlines() if 'Duration' in l][0].split('Duration: ')[1].split(',')[0].split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)


def ff(a):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1800:])


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


def main():
    tarjeta(TMP / 'tarjeta.png')
    ds = [dur(AQUI / 'voz' / f'{v}.mp3') + 0.35 for _, v, _ in ESC]
    T = [0]
    for d in ds: T.append(T[-1] + d)
    TOTAL = T[-1] + TARJ
    ent, fl = [], ''
    for i, (n, _, _) in enumerate(ESC):
        ent += ['-i', str(AQUI / 'tomas' / f'{n}.mp4')]
        fl += f'[{i}:v]scale={W}:{H}:flags=lanczos,fps=30,setsar=1,format=yuv420p,tpad=stop_mode=clone:stop_duration=3,trim=duration={ds[i]:.2f},setpts=PTS-STARTPTS[c{i}];'
    k = len(ESC)
    ent += ['-loop', '1', '-t', str(TARJ), '-i', str(TMP / 'tarjeta.png')]
    fl += f'[{k}:v]scale={W}:{H},fps=30,setsar=1,format=yuv420p[c{k}];' + ''.join(f'[c{i}]' for i in range(k + 1)) + f'concat=n={k + 1}:v=1:a=0[base];'
    cur, b = 'base', k + 1
    for j, (_, _, lin) in enumerate(ESC):
        p = TMP / f't{j}.png'; tex(lin, p, 1400, tam=74); ent += ['-loop', '1', '-t', f'{TOTAL:.1f}', '-i', str(p)]
        fl += f"[{cur}][{b + j}:v]overlay=0:0:enable='between(t,{T[j] + 0.1:.2f},{T[j + 1] - 0.05:.2f})'[o{j}];"; cur = f'o{j}'
    a0 = b + len(ESC)
    ent += ['-i', str(MUSICA)] + [x for _, v, _ in ESC for x in ('-i', str(AQUI / 'voz' / f'{v}.mp3'))]
    fl += f"[{a0}:a]aresample=44100,aloop=loop=-1:size=2147483647,volume=0.18,afade=t=in:st=0:d=0.6,afade=t=out:st={TOTAL - 1.2:.2f}:d=1.2,atrim=0:{TOTAL:.2f}[m];"
    fl += ''.join(f"[{a0 + 1 + i}:a]aresample=44100,adelay={int((T[i] + 0.15) * 1000)}|{int((T[i] + 0.15) * 1000)}[v{i}];" for i in range(len(ESC)))
    fl += '[m]' + ''.join(f'[v{i}]' for i in range(len(ESC))) + f'amix=inputs={len(ESC) + 1}:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]'
    hd = TMP / 'hd.mp4'; sal = AQUI / 'Anegocios_Fernando_v3.mp4'
    ff(ent + ['-filter_complex', fl, '-map', f'[{cur}]', '-map', '[a]', '-t', f'{TOTAL:.2f}', '-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', str(hd)])
    ff(['-i', str(hd), '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-pix_fmt', 'yuv420p', '-crf', '24', '-preset', 'slow', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(sal)])
    print(sal, sal.stat().st_size // 1024, 'KB', f'{TOTAL:.1f}s')


if __name__ == '__main__':
    main()
