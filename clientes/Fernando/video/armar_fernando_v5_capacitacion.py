"""Fernando (Anegocios) v5 «capacitación para la confianza»: puro Fernando REAL (su cara y su voz de su video del taller y de su nota de voz explicando cómo atiende a un cliente),
con las fotos reales del kit mientras explica; sin avatar ni voz clonada salvo el cierre de 3 s. Uso: python3 armar_fernando_v5_capacitacion.py"""
import subprocess, sys
from pathlib import Path
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/XV')
sys.path.insert(0, str(Path(__file__).resolve().parent))
import imageio_ffmpeg
from armar_fernando_v4 import TMP, tarjeta, dur, W, H, CL, MUSICA
from armar_xv import tex

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
VID = CL / '1021_014550_video.mp4'; NOTA = CL / '1021_221426_ptt.ogg'
CADENA = 'highpass=f=80,equalizer=f=3000:t=q:w=1:g=2.5,acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=4,alimiter=limit=0.95'


def ff(a):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1800:])


# (fuente de imagen, inicio, duración, texto en pantalla) — el audio de cada tramo es SU voz real
TRAMOS = [('vid', 0.0, 7.9, ['TALLER 100% PRÁCTICO', 'PUNTO DE VENTA EN LA NUBE']),
          ('vid', 27.95, 8.15, ['EN ~40 MINUTOS', 'TU PROGRAMA FUNCIONANDO'])]
# voz de su nota (51.7 a 69.1) con fotos reales encima, cambiando con lo que dice
NOTA_INI, NOTA_DUR = 51.7, 17.4
DIAPOS = [('soft', 4.6, ['SI QUIERES, LO VEMOS', 'FUNCIONANDO EN TU COMPUTADORA']), ('kit', 3.9, ['TE CREO TU CUENTA', 'EN ESE MOMENTO']),
          ('imp', 3.3, ['IMPRESORA + LECTOR', 'LOS INSTALO EN TU NEGOCIO']), ('yo', 5.6, ['TE MUESTRO CÓMO EL PROGRAMA', 'RESUELVE LO DE TU NEGOCIO'])]
CTA_V = AQUI / 'voz' / 'F5.mp3'


def main():
    tarjeta(TMP / 'd_tarj_cap.png')
    ds = sum(d for _, d, _ in DIAPOS)
    assert abs(ds - NOTA_DUR) < 0.2, ds
    t_cta = dur(CTA_V) + 0.5
    ent, fl, vs = [], '', []
    # video
    for i, (_, ini, d, _) in enumerate(TRAMOS):
        ent += ['-ss', str(ini), '-t', f'{d:.2f}', '-i', str(VID)]
        fl += (f'[{i}:v]scale={W}:{H}:flags=lanczos,unsharp=5:5:0.7,eq=contrast=1.04:saturation=1.05,fps=30,setsar=1,format=yuv420p,setpts=PTS-STARTPTS[v{i}];')
        vs.append(f'[v{i}]')
    k = len(TRAMOS)
    for j, (n, d, _) in enumerate(DIAPOS):
        i = k + j
        ent += ['-framerate', '30', '-loop', '1', '-t', f'{d + 0.1:.2f}', '-i', str(TMP / f'd_{n}.png')]
        fl += (f'[{i}:v]scale=1188:2112,zoompan=z=\'min(1.0+0.0007*on,1.07)\':x=\'(iw-iw/zoom)/2\':y=\'(ih-ih/zoom)/2\':d=1:s={W}x{H}:fps=30,setsar=1,format=yuv420p,'
               f'trim=duration={d:.2f},setpts=PTS-STARTPTS,fps=30[v{i}];')
        vs.append(f'[v{i}]')
    i = k + len(DIAPOS)
    ent += ['-framerate', '30', '-loop', '1', '-t', f'{t_cta + 0.1:.2f}', '-i', str(TMP / 'd_tarj_cap.png')]
    fl += f'[{i}:v]scale={W}:{H},fps=30,setsar=1,format=yuv420p,trim=duration={t_cta:.2f},setpts=PTS-STARTPTS[v{i}];'; vs.append(f'[v{i}]')
    fl += ''.join(vs) + f'concat=n={len(vs)}:v=1:a=0[base];'
    # textos
    tiempos, t = [], 0.0
    for _, _, d, lin in TRAMOS: tiempos.append((lin, t, t + d)); t += d
    for n, d, lin in DIAPOS: tiempos.append((lin, t, t + d)); t += d
    TOTAL = t + t_cta
    cur, b = 'base', i + 1
    for j, (lin, a, z) in enumerate(tiempos):
        p = TMP / f'tc{j}.png'; tex(lin, p, 1470, tam=66); ent += ['-loop', '1', '-t', f'{TOTAL:.1f}', '-i', str(p)]
        fl += f"[{cur}][{b + j}:v]overlay=0:0:enable='between(t,{a + 0.15:.2f},{z - 0.08:.2f})'[o{j}];"; cur = f'o{j}'
    # audio: su voz real (video, video, nota) + cierre; música muy baja
    a0 = b + len(tiempos)
    ent += ['-ss', '0', '-t', '7.9', '-i', str(VID), '-ss', '27.95', '-t', '8.15', '-i', str(VID), '-ss', str(NOTA_INI), '-t', str(NOTA_DUR), '-i', str(NOTA), '-i', str(CTA_V), '-i', str(MUSICA)]
    for q in range(3): fl += f'[{a0 + q}:a]aresample=48000,aformat=channel_layouts=mono,afade=t=in:d=0.04,afade=t=out:st=%s:d=0.06[w{q}];' % [7.84, 8.09, NOTA_DUR - 0.06][q]
    fl += f'[{a0 + 3}:a]aresample=48000,aformat=channel_layouts=mono,adelay=300|300[w3];'
    fl += f'[w0][w1][w2][w3]concat=n=4:v=0:a=1,{CADENA}[vz];'
    fl += f'[{a0 + 4}:a]aresample=48000,aloop=loop=-1:size=2147483647,aformat=channel_layouts=mono,volume=0.10,afade=t=in:st=0:d=0.8,afade=t=out:st={TOTAL - 1.2:.2f}:d=1.2,atrim=0:{TOTAL:.2f}[mu];'
    fl += '[vz][mu]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]'
    hd = TMP / 'hd5.mp4'; sal = AQUI / 'Anegocios_Fernando_v5_capacitacion.mp4'
    ff(ent + ['-filter_complex', fl, '-map', f'[{cur}]', '-map', '[a]', '-t', f'{TOTAL:.2f}', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', str(hd)])
    ff(['-i', str(hd), '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-pix_fmt', 'yuv420p', '-crf', '24', '-preset', 'slow', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(sal)])
    print(sal, sal.stat().st_size // 1024, 'KB', f'{TOTAL:.1f}s')


if __name__ == '__main__':
    main()
