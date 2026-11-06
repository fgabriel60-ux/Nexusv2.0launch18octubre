"""Reel XV v5 (Manuel) con la estructura de la referencia «GIO XV»: dron → detalles → retratos → letrero → grupo → giro → fiesta rápida → cierre.
Caras sin deformar: toda toma con personas es video o foto REAL (solo cámara lenta, color y Ken Burns); la IA (v5/clips S1-S3) solo hace tomas sin caras.
Uso: python3 armar_xv_v5.py"""
import subprocess
from pathlib import Path
import imageio_ffmpeg
from armar_xv import foto_vertical, tarjeta

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
ORI = AQUI / 'originales'
IA = AQUI / 'v5' / 'clips'
TMP = Path('/tmp/claude-1000/-workspaces-Nexusv2-0launch18octubre/30f81786-0fae-4f61-88f3-0421cbe18eec/scratchpad/xv5'); TMP.mkdir(parents=True, exist_ok=True)
MUSICA = AQUI / 'musica_suave_s7.wav'
W, H, FPS = 1080, 1920, 30
GLOW = "split[a][b];[b]gblur=sigma=20,eq=brightness=0.02[g];[a][g]blend=all_mode=screen:all_opacity=0.16,vignette=PI/5"
COLOR = "curves=all='0/0.03 0.35/0.40 1/1',eq=contrast=1.07:saturation=1.18:gamma=1.05,colorbalance=rs=0.04:bs=-0.03:rh=0.03:bh=-0.02"
# (tipo, fuente, inicio, centro_x / zoom, velocidad, duración de salida)
PLAN = [
    ('ia', 'S1', 0.3, None, 1.0, 2.6),                 # 1 dron del salón de noche (IA, sin gente)
    ('ia', 'S2', 0.3, None, 1.0, 2.4),                 # 2 detalle: rosas sobre el vestido (IA desde su foto, sin cara)
    ('foto', 'BV8B6048-Editar', 0, 'in', 1.0, 2.4),    # 3 retrato con rosas (foto real)
    ('foto', 'BV8B6090', 0, 'out', 1.0, 2.4),          # 4 retrato en la puerta (foto real)
    ('ia', 'S3', 0.3, None, 1.0, 2.6),                 # 5 salón vacío con niebla y letras XV (IA, sin gente)
    ('clip', 'C6752', 10, .50, .5, 2.6),               # 6 corte: ella con sus damas (real)
    ('clip', 'C6771', 4, .42, .5, 3.0),                # 7 giro del vestido (real, cámara lenta)
    ('clip', 'C6755', 15, .50, 1.0, 1.0),              # 8-13 fiesta: cortes rápidos de 1 s (real)
    ('clip', 'C6801', 3, .40, 1.0, 1.0),
    ('clip', 'C6755', 27, .55, 1.0, 1.0),
    ('clip', 'C6801', 75, .45, 1.0, 1.0),
    ('clip', 'C6801', 123, .40, 1.0, 1.0),
    ('clip', 'C6755', 45, .50, 1.0, 1.0),
    ('clip', 'C6801', 165, .45, .5, 2.6),              # 14 ella en la pista (real, lenta)
    ('foto', 'BV8B6220', 0, 'in', 1.0, 2.2),           # 15 sesión con el caballo (foto real)
    ('foto', 'BV8B6224', 0, 'out', 1.0, 2.2),          # 16 de espaldas con el vestido (foto real)
    ('foto', 'BV8B6038-Editar', 0, 'out', 1.0, 4.0),   # 17 cierre en el kiosco + tarjeta
]
T_FIESTA = sum(p[5] for p in PLAN[:5])                # la música de fiesta entra con el corte de las damas
TOTAL = sum(p[5] for p in PLAN)


def ff(a):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1800:])


def segmento(n, tipo, f, ini, cx, vel, dur):
    s = TMP / f's{n:02d}.mp4'
    post = f"{COLOR},{GLOW},noise=alls=4:allf=t,fps={FPS},setsar=1,format=yuv420p"
    if tipo == 'clip':
        ancho = 2160 * 9 / 16; x = int(max(0, min(3840 - ancho, cx * 3840 - ancho / 2)))
        ff(['-ss', str(ini), '-t', f'{dur * vel:.2f}', '-i', str(ORI / f'{f}.MP4'), '-filter_complex',
            f"[0:v]crop={int(ancho)}:2160:{x}:0,scale={W}:{H}:flags=lanczos,setpts={1 / vel:.3f}*PTS,{post}[v]",
            '-map', '[v]', '-an', '-t', f'{dur:.2f}', '-c:v', 'libx264', '-preset', 'fast', '-crf', '16', str(s)])
    elif tipo == 'ia':
        ff(['-ss', str(ini), '-t', f'{dur:.2f}', '-i', str(IA / f'{f}.mp4'), '-vf',
            f"scale={W}:{H}:flags=lanczos,unsharp=5:5:0.7,{post}", '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '16', str(s)])
    else:
        png = TMP / f'kb_{f}.png'; foto_vertical(f, int(W * 1.18), int(H * 1.18)).save(png)
        k = int(dur * FPS); z0, z1 = (1.0, 1.12) if cx == 'in' else (1.12, 1.0)
        ff(['-loop', '1', '-i', str(png), '-vf',
            f"zoompan=z='{z0}+({z1}-{z0})*on/{k}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={k}:s={W}x{H}:fps={FPS},{post}",
            '-frames:v', str(k), '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '16', str(s)])
    return s


def main():
    tarjeta(TMP / 'tarjeta.png')
    segs = [segmento(i, *p) for i, p in enumerate(PLAN)]
    (TMP / 'lista.txt').write_text(''.join(f"file '{s}'\n" for s in segs))
    fiesta = TMP / 'fiesta.wav'
    ff(['-ss', '72', '-t', f'{TOTAL - T_FIESTA + 2:.1f}', '-i', str(ORI / 'C6801.MP4'), '-vn', '-ac', '2', '-ar', '44100', str(fiesta)])
    t_f = T_FIESTA - 0.4
    ent = ['-f', 'concat', '-safe', '0', '-i', str(TMP / 'lista.txt'), '-loop', '1', '-t', '3.0', '-i', str(TMP / 'tarjeta.png'), '-i', str(fiesta), '-i', str(MUSICA)]
    fl = f"[1:v]format=rgba,fade=t=in:st=0:d=0.4:alpha=1,setpts=PTS+{TOTAL - 3.0:.2f}/TB[tj];[0:v][tj]overlay=0:0:eof_action=pass[v];"
    fl += f"[2:a]loudnorm=I=-15:TP=-1.5,afade=t=in:st=0:d=0.6,adelay={int(t_f * 1000)}|{int(t_f * 1000)}[f];"
    fl += (f"[3:a]aresample=44100,loudnorm=I=-19:TP=-2,afade=t=in:st=0:d=0.8,afade=t=out:st={t_f - 0.2:.2f}:d=1.0,atrim=0:{t_f + 1.0:.2f}[m];"
           f"[m][f]amix=inputs=2:normalize=0,afade=t=out:st={TOTAL - 1.2:.2f}:d=1.2[a]")
    hd = TMP / 'xv_v5_hd.mp4'; sal = AQUI / 'final' / 'XV_reel_v5.mp4'
    ff(ent + ['-filter_complex', fl, '-map', '[v]', '-map', '[a]', '-t', f'{TOTAL:.2f}', '-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-pix_fmt', 'yuv420p',
              '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', str(hd)])
    ff(['-i', str(hd), '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-pix_fmt', 'yuv420p', '-crf', '24', '-preset', 'slow',
        '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(sal)])
    print(sal, sal.stat().st_size // 1024, 'KB', f'{TOTAL:.1f}s')


if __name__ == '__main__':
    main()
