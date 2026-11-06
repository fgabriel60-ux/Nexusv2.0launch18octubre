"""Veneers Dental (Dra. Ángeles): 2 tomas H3 hablando con su voz Fish encima + textos + cierre con su anuncio real, 9:16.
Uso: python3 armar_alberto.py"""
import subprocess, sys
from pathlib import Path
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/XV')
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageOps
from armar_xv import fu, tex

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
TMP = Path('/tmp/claude-1000/-workspaces-Nexusv2-0launch18octubre/7f4b01e6-9d5b-409e-acca-ec7fedd1520c/scratchpad/alberto'); TMP.mkdir(parents=True, exist_ok=True)
W, H = 1080, 1920
DA, DB, PAUSA, TARJ = 11.91, 8.80, 0.25, 3.8
T2 = DA + PAUSA
TOTAL = T2 + DB + 0.3 + TARJ
TEXTOS = [(['IMPLANTE DENTAL', 'RAÍZ DE TITANIO'], 4.6, 8.4, 1420),
          (['CON ANESTESIA LOCAL'], 8.6, DA, 1420),
          (['DESDE $12,500 MXN', 'LA CORONA VA APARTE'], T2 + 0.2, T2 + 5.6, 1420),
          (['ESCRÍBENOS POR WHATSAPP'], T2 + 5.8, T2 + DB + 0.3, 1420)]


def ff(a):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1800:])


def tarjeta(ruta):
    # Sin el anuncio viejo: dice «sin sentir dolor», frase que Meta rechazó. Foto real de la doctora + datos confirmados.
    foto = ImageOps.fit(ImageOps.exif_transpose(Image.open(AQUI.parent / 'whatsapp' / 'del_cliente' / 'doctora_5.jpg')).convert('RGB'), (W, H), centering=(.5, .3))
    capa = Image.new('RGBA', (W, H)); dc = ImageDraw.Draw(capa)
    for y in range(H):
        dc.line([(0, y), (W, y)], fill=(8, 8, 10, int(235 * max(0, (y - H * .38) / (H * .3)) if y < H * .68 else 235)))
    img = Image.alpha_composite(foto.convert('RGBA'), capa); d = ImageDraw.Draw(img)
    ORO = (226, 186, 98)
    def c(t, y, tam, col, peso='Black'):
        f = fu(tam, peso)
        while d.textlength(t, font=f) > W - 110: tam -= 2; f = fu(tam, peso)
        d.text(((W - d.textlength(t, font=f)) / 2, y), t, font=f, fill=col)
    c('VENEERS DENTAL', 1230, 96, (255, 255, 255)); c('AESTHETIC CLINIC · NOGALES, SONORA', 1345, 40, ORO, 'Bold')
    c('IMPLANTE DESDE $12,500 MXN', 1440, 58, (255, 255, 255), 'ExtraBold')
    t = 'ESCRÍBENOS POR WHATSAPP'; f = fu(50, 'ExtraBold'); an = d.textlength(t, font=f) + 110
    d.rounded_rectangle(((W - an) / 2, 1560, (W + an) / 2, 1690), 65, fill=(37, 211, 102)); d.text(((W - an) / 2 + 55, 1595), t, font=f, fill=(255, 255, 255))
    img.convert('RGB').save(ruta)


def main():
    tarjeta(TMP / 'tarjeta.png')
    voz = TMP / 'voz.wav'
    ff(['-i', str(AQUI / 'voz' / 'dra_A.mp3'), '-i', str(AQUI / 'voz' / 'dra_B.mp3'), '-filter_complex',
        f'[0:a]aresample=44100,apad=pad_dur={PAUSA}[a0];[1:a]aresample=44100[a1];[a0][a1]concat=n=2:v=0:a=1,apad=whole_dur={TOTAL:.2f}[a]', '-map', '[a]', str(voz)])
    ent = ['-t', f'{DA + PAUSA:.2f}', '-i', str(AQUI / 'tomas' / 'A1_presenta.mp4'), '-t', f'{DB + 0.3:.2f}', '-i', str(AQUI / 'tomas' / 'A2_precio.mp4'),
           '-loop', '1', '-t', str(TARJ), '-i', str(TMP / 'tarjeta.png')]
    fl = ''
    for i in range(2):
        fl += f'[{i}:v]scale={W}:{H}:flags=lanczos,unsharp=5:5:0.6,fps=30,setsar=1,format=yuv420p,tpad=stop_mode=clone:stop_duration=1,setpts=PTS-STARTPTS[v{i}];'
    fl += f'[v0]trim=duration={DA + PAUSA:.2f}[c0];[v1]trim=duration={DB + 0.3:.2f}[c1];[2:v]scale={W}:{H},fps=30,setsar=1,format=yuv420p[c2];[c0][c1][c2]concat=n=3:v=1:a=0[base];'
    cur = 'base'
    for k, (lin, a, b, y) in enumerate(TEXTOS):
        p = TMP / f't{k}.png'; tex(lin, p, y, tam=74); ent += ['-loop', '1', '-t', f'{TOTAL:.1f}', '-i', str(p)]
        fl += f"[{cur}][{k + 3}:v]overlay=0:0:enable='between(t,{a:.2f},{b:.2f})'[o{k}];"; cur = f'o{k}'
    ent += ['-i', str(voz)]
    fl += f"[{3 + len(TEXTOS)}:a]loudnorm=I=-14:TP=-1.5[a]"
    hd = TMP / 'alberto_hd.mp4'; sal = AQUI / 'Veneers_Dra_Angeles_implante_v1.mp4'
    ff(ent + ['-filter_complex', fl, '-map', f'[{cur}]', '-map', '[a]', '-t', f'{TOTAL:.2f}', '-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', str(hd)])
    ff(['-i', str(hd), '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-pix_fmt', 'yuv420p', '-crf', '24', '-preset', 'slow', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(sal)])
    print(sal, sal.stat().st_size // 1024, 'KB', f'{TOTAL:.1f}s')


if __name__ == '__main__':
    main()
