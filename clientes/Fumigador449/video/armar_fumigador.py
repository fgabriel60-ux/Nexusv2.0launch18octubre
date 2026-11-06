"""Fumigaciones Chávez AGS (Héctor Chávez): SU equipo real trabajando (su video del 23 oct) + SU voz clonada (Fish) + textos + tarjeta de WhatsApp, 9:16.
Uso: python3 armar_fumigador.py"""
import subprocess, sys
from pathlib import Path
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/XV')
import imageio_ffmpeg
from PIL import Image, ImageDraw
from armar_xv import fu, tex

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
TMP = Path('/tmp/claude-1000/-workspaces-Nexusv2-0launch18octubre/3f2c6b79-5aa7-409f-95e2-6c1cf5560d47/scratchpad/fumigador'); TMP.mkdir(parents=True, exist_ok=True)
EQUIPO = AQUI.parent / 'whatsapp' / '1023_173213_video.mp4'
MUSICA = AQUI.parents[1] / 'XV' / 'musica_suave_s7.wav'
W, H = 1080, 1920
TARJ = 3.6
CORTES = [  # (inicio en su video, duración, texto) siguiendo las frases de la voz
    (1.0, 5.0, ['¿CHINCHES, CUCARACHAS', 'O ALACRANES?']),
    (14.0, 5.08, ['FUMIGACIONES CHÁVEZ', 'AGUASCALIENTES']),
    (22.0, 4.24, ['CASAS · LOCALES DE COMIDA', 'Y CAMIONES']),
    (30.0, 3.84, ['VAMOS HASTA', 'EN DOMINGO']),
    (38.0, 5.36, ['NUESTRO EQUIPO REAL', 'TRABAJANDO']),
    (46.0, 4.80, ['PREGUNTA TU PRECIO', 'POR WHATSAPP']),
]


def ff(a):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1800:])


def tarjeta(ruta):
    img = Image.new('RGB', (W, H), (14, 14, 16)); d = ImageDraw.Draw(img)
    AMAR, VERDE = (255, 196, 0), (37, 211, 102)
    def c(t, y, tam, col, peso='Black'):
        f = fu(tam, peso)
        while d.textlength(t, font=f) > W - 110: tam -= 2; f = fu(tam, peso)
        d.text(((W - d.textlength(t, font=f)) / 2, y), t, font=f, fill=col)
    c('FUMIGACIONES', 520, 110, (255, 255, 255)); c('CHÁVEZ AGS', 650, 120, AMAR)
    c('CASAS · LOCALES DE COMIDA · CAMIONES', 820, 42, (255, 255, 255), 'Bold')
    c('TRABAJAMOS HASTA EN DOMINGO', 885, 42, (255, 255, 255), 'Bold')
    t = 'ESCRÍBENOS POR WHATSAPP'; f = fu(50, 'ExtraBold'); a = d.textlength(t, font=f) + 110
    d.rounded_rectangle(((W - a) / 2, 990, (W + a) / 2, 1120), 65, fill=VERDE); d.text(((W - a) / 2 + 55, 1025), t, font=f, fill=(255, 255, 255))
    c('449 819 0392', 1190, 104, AMAR)
    img.save(ruta)


def main():
    tarjeta(TMP / 'tarjeta.png')
    T_TARJ = sum(c[1] for c in CORTES); TOTAL = T_TARJ + TARJ
    ent, fl = [], ''
    for i, (ini, dur, _) in enumerate(CORTES):
        ent += ['-ss', str(ini), '-t', f'{dur:.2f}', '-i', str(EQUIPO)]
        fl += (f'[{i}:v]scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},unsharp=5:5:0.8,eq=contrast=1.08:saturation=1.15:brightness=0.02,'
               f'fps=30,setsar=1,format=yuv420p,tpad=stop_mode=clone:stop_duration=1,trim=duration={dur:.2f},setpts=PTS-STARTPTS[c{i}];')
    k = len(CORTES)
    ent += ['-loop', '1', '-t', str(TARJ), '-i', str(TMP / 'tarjeta.png')]
    fl += f'[{k}:v]scale={W}:{H},fps=30,setsar=1,format=yuv420p[tj];' + ''.join(f'[c{i}]' for i in range(k)) + f'[tj]concat=n={k + 1}:v=1:a=0[base];'
    cur, t0 = 'base', 0.0
    for j, (_, dur, lin) in enumerate(CORTES):
        p = TMP / f't{j}.png'; tex(lin, p, 1380, tam=74); ent += ['-loop', '1', '-t', f'{TOTAL:.1f}', '-i', str(p)]
        fl += f"[{cur}][{k + 1 + j}:v]overlay=0:0:enable='between(t,{t0 + 0.1:.2f},{t0 + dur - 0.05:.2f})'[o{j}];"; cur = f'o{j}'; t0 += dur
    a0 = k + 1 + len(CORTES)
    ent += ['-i', str(MUSICA), '-i', str(AQUI / 'voz' / 'hector_guion.wav')]
    fl += (f"[{a0}:a]aresample=48000,aloop=loop=-1:size=2147483647,volume=0.16,afade=t=in:st=0:d=0.5,afade=t=out:st={TOTAL - 1.2:.2f}:d=1.2,atrim=0:{TOTAL:.2f}[mu];"
           f"[{a0 + 1}:a]aresample=48000[vz];[mu][vz]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]")
    hd = TMP / 'hd.mp4'; sal = AQUI / 'Fumigaciones_Chavez_v1.mp4'
    ff(ent + ['-filter_complex', fl, '-map', f'[{cur}]', '-map', '[a]', '-t', f'{TOTAL:.2f}', '-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', str(hd)])
    ff(['-i', str(hd), '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-pix_fmt', 'yuv420p', '-crf', '24', '-preset', 'slow', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(sal)])
    print(sal, sal.stat().st_size // 1024, 'KB', f'{TOTAL:.1f}s')


if __name__ == '__main__':
    main()
