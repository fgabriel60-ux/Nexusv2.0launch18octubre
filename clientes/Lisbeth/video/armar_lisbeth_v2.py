"""Lisbeth v2: selfie con su terreno atrás diciendo el gancho («Tomatlán no es promesa, es terreno real») → lanza el celular y la cámara sube rápida y
fluida (sin corte, acelerada 1.8×) hasta la toma aérea → sigue su v22 completa con su audio. Uso: python3 armar_lisbeth_v2.py"""
import subprocess
from pathlib import Path
import imageio_ffmpeg

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H = 720, 1280
D_HABLA, VEL = 4.7, 1.8


def ff(a):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1800:])


def main():
    sal = AQUI / 'Lisbeth_v2_selfie_a_dron.mp4'
    v22 = AQUI.parent / 'referencia' / 'v22.mp4'
    fl = (f"[0:v]scale={W}:{H},fps=30,setsar=1,format=yuv420p,tpad=stop_mode=clone:stop_duration=1,trim=duration={D_HABLA},setpts=PTS-STARTPTS[a];"
          f"[1:v]scale={W}:{H},fps=30,setsar=1,format=yuv420p,setpts=PTS/{VEL}[s];"
          f"[2:v]scale={W}:{H},fps=30,setsar=1,format=yuv420p,setpts=PTS-STARTPTS[c];[a][s][c]concat=n=3:v=1:a=0[v];"
          f"[3:a]aresample=44100,apad=whole_dur={D_HABLA}[va];[1:a]aresample=44100,atempo={VEL}[sa];[2:a]aresample=44100[ca];[va][sa][ca]concat=n=3:v=0:a=1,loudnorm=I=-14:TP=-1.5[aud]")
    ff(['-i', str(AQUI / 'v2' / 'LIS_habla.mp4'), '-i', str(AQUI / 'v2' / 'LIS_sube.mp4'), '-i', str(v22), '-i', str(AQUI / 'voz' / 'L_gancho.mp3'),
        '-filter_complex', fl, '-map', '[v]', '-map', '[aud]', '-c:v', 'libx264', '-profile:v', 'main', '-pix_fmt', 'yuv420p', '-crf', '22', '-preset', 'slow',
        '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(sal)])
    print(sal, sal.stat().st_size // 1024, 'KB')


if __name__ == '__main__':
    main()
