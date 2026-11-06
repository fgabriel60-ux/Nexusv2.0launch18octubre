"""Servilin (Víctor): v2 sin el líquido raro (la escena de la máquina ahora es su cuadro limpio con acercamiento): 4 escenas NUEVAS de trabajo (Qwen + H3) con sus trabajadores reales + su voz clonada + textos estilo «La limpieza no debería ser un problema» + tarjeta de WhatsApp, 9:16.
Uso: python3 armar_victor.py [musica.wav]"""
import subprocess, sys
from pathlib import Path
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/XV')
import imageio_ffmpeg
from PIL import Image, ImageDraw
from armar_xv import fu, tex

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
TMP = Path('/tmp/claude-1000/-workspaces-Nexusv2-0launch18octubre/7f4b01e6-9d5b-409e-acca-ec7fedd1520c/scratchpad/victor_v2'); TMP.mkdir(parents=True, exist_ok=True)
MUSICA = Path(sys.argv[1]) if len(sys.argv) > 1 else AQUI.parents[1] / 'XV' / 'musica_suave_s7.wav'
W, H = 1080, 1920
XF, D = 0.25, 4.1
ORDEN = ['S1_trapeo', 'S2_ventanas', 'S3_seco_kb', 'S4_supervision']   # S3: cuadro limpio de Qwen con acercamiento; H3 siempre metía líquido
T_INTRO = len(ORDEN) * D - XF * (len(ORDEN) - 1)
TARJ = 4.5
TOTAL = T_INTRO + TARJ
TEXTOS = [(['LA LIMPIEZA NO DEBERÍA', 'SER UN PROBLEMA'], 0.2, 3.6, 1380),
          (['PERSONAL UNIFORMADO', 'CAPACITADO Y SUPERVISADO'], 3.8, 8.4, 1380),
          (['LIMPIEZA Y MANTENIMIENTO', 'TÚ TE ENFOCAS EN PRODUCIR'], 8.6, 13.4, 1380),
          (['PIDE TU COTIZACIÓN', 'POR WHATSAPP'], 13.6, 15.6, 1380)]


def ff(a):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1800:])


def tarjeta(ruta):
    img = Image.new('RGBA', (W, H), (10, 28, 64, 232)); d = ImageDraw.Draw(img)
    AMARILLO, VERDE = (250, 214, 50), (37, 211, 102)
    def c(t, y, tam, col, peso='Black'):
        f = fu(tam, peso)
        while d.textlength(t, font=f) > W - 110: tam -= 2; f = fu(tam, peso)
        d.text(((W - d.textlength(t, font=f)) / 2, y), t, font=f, fill=col)
    c('SERVILIN', 560, 130, (255, 255, 255)); c('LIMPIEZA Y MANTENIMIENTO', 720, 54, AMARILLO, 'Bold')
    c('PARA PLANTAS Y EMPRESAS', 800, 46, (255, 255, 255), 'Bold')
    t = 'PIDE TU COTIZACIÓN POR WHATSAPP'; f = fu(42, 'ExtraBold'); a = d.textlength(t, font=f) + 110
    d.rounded_rectangle(((W - a) / 2, 940, (W + a) / 2, 1070), 65, fill=VERDE); d.text(((W - a) / 2 + 55, 980), t, font=f, fill=(255, 255, 255))
    img.save(ruta)


def main():
    tarjeta(TMP / 'tarjeta.png')
    ent, fl = [], ''
    for i, n in enumerate(ORDEN):
        ent += ['-t', str(D + 0.2), '-i', str(AQUI / 'v2' / f'{n}.mp4')]
        fl += (f"[{i}:v]scale={W}:{H}:flags=lanczos,unsharp=5:5:0.7,eq=contrast=1.05:saturation=1.10,"
               f"fps=30,setsar=1,format=yuv420p,setpts=PTS-STARTPTS,trim=duration={D},setpts=PTS-STARTPTS,fps=30,settb=AVTB[v{i}];")
    prev, acum = 'v0', D
    for i in range(1, len(ORDEN)):
        off = acum - XF
        fl += f"[{prev}][v{i}]xfade=transition=fade:duration={XF}:offset={off:.2f}[x{i}];"; prev = f'x{i}'; acum = off + D
    intro = TMP / 'intro.mp4'
    ff(ent + ['-filter_complex', fl.rstrip(';'), '-map', f'[{prev}]', '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '16', '-pix_fmt', 'yuv420p', str(intro)])
    ent2, fl2 = ['-i', str(intro), '-loop', '1', '-t', str(TARJ), '-i', str(TMP / 'tarjeta.png')], ''
    fl2 += f'[0:v]tpad=stop_mode=clone:stop_duration={TARJ - 1:.1f}[b0];'
    cur = 'b0'
    for k, (lin, a, b, y) in enumerate(TEXTOS):
        p = TMP / f't{k}.png'; tex(lin, p, y, tam=76); ent2 += ['-loop', '1', '-t', f'{b + .5:.1f}', '-i', str(p)]
        fl2 += f"[{cur}][{k + 2}:v]overlay=0:0:enable='between(t,{a},{b})'[o{k}];"; cur = f'o{k}'
    nt = 2 + len(TEXTOS)
    ent2 += ['-i', str(MUSICA), '-i', str(AQUI / 'voz' / 'victor.mp3')]
    fl2 += f"[1:v]format=rgba,fade=t=in:st=0:d=0.4:alpha=1,setpts=PTS+{T_INTRO:.2f}/TB[tj];[{cur}][tj]overlay=0:0:eof_action=pass[v];"
    fl2 += (f"[{nt}:a]aresample=44100,aloop=loop=-1:size=2147483647,volume=0.22,afade=t=in:st=0:d=0.8,afade=t=out:st={TOTAL - 1.4:.2f}:d=1.4,atrim=0:{TOTAL:.2f}[m];"
            f"[{nt + 1}:a]aresample=44100,adelay=150|150,atrim=0:{TOTAL:.2f}[v2];[m][v2]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]")
    hd = TMP / 'victor_hd.mp4'; sal = AQUI / 'Servilin_escenas_v2_sin_liquido.mp4'
    ff(ent2 + ['-filter_complex', fl2, '-map', '[v]', '-map', '[a]', '-t', f'{TOTAL:.2f}', '-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', str(hd)])
    ff(['-i', str(hd), '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-pix_fmt', 'yuv420p', '-crf', '24', '-preset', 'slow', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(sal)])
    print(sal, sal.stat().st_size // 1024, 'KB', f'{TOTAL:.1f}s')


if __name__ == '__main__':
    main()
