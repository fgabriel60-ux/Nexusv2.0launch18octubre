"""Mariano · Vizcaíno v3 con gancho estilo Lisbeth (sin teléfono volando): él frente a las casas REALES de Vizcaíno (su video del 22 oct) dice con su voz
«no son promesas, son casas reales, ¡míralas desde arriba!» → la cámara sube como dron hasta el conjunto → sigue su video de las 3 casas v2 (43 s) completo.
Uso: python3 armar_mariano_gancho_v2.py"""
import subprocess, sys
from pathlib import Path
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/XV')
import imageio_ffmpeg
from armar_xv import tex

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
TMP = Path('/tmp/claude-1000/-workspaces-Nexusv2-0launch18octubre/3f2c6b79-5aa7-409f-95e2-6c1cf5560d47/scratchpad/mariano_g2'); TMP.mkdir(parents=True, exist_ok=True)
W, H = 720, 1280
D_HABLA, VEL = 7.7, 1.5


def ff(a):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1800:])


def main():
    sys.modules['armar_xv'].W, sys.modules['armar_xv'].H = W, H   # textos al tamaño de este video
    tex(['NO SON PROMESAS', 'SON CASAS REALES'], TMP / 't0.png', 900, tam=56)
    g = AQUI / 'gancho_v2'; sal = AQUI / 'Vizcaino_3casas_v3_gancho.mp4'
    fl = (f"[0:v]scale={W}:{H},fps=30,setsar=1,format=yuv420p,tpad=stop_mode=clone:stop_duration=1,trim=duration={D_HABLA},setpts=PTS-STARTPTS[a0];"
          f"[a0][4:v]overlay=0:0:enable='between(t,0.2,{D_HABLA - 0.1})'[a];"
          f"[1:v]scale={W}:{H},fps=30,setsar=1,format=yuv420p,setpts=PTS/{VEL}[s];"
          f"[2:v]scale={W}:{H},fps=30,setsar=1,format=yuv420p,setpts=PTS-STARTPTS[c];[a][s][c]concat=n=3:v=1:a=0[v];"
          f"[3:a]aresample=44100,apad=whole_dur={D_HABLA}[va];[1:a]aresample=44100,atempo={VEL}[sa];[2:a]aresample=44100[ca];[va][sa][ca]concat=n=3:v=0:a=1,loudnorm=I=-14:TP=-1.5[aud]")
    ff(['-i', str(g / 'MAR2_habla.mp4'), '-i', str(g / 'MAR2_sube.mp4'), '-i', str(AQUI / 'enviados' / 'Vizcaino_3casas_v2_43s.mp4'), '-i', str(g / 'M_gancho.mp3'),
        '-loop', '1', '-t', str(D_HABLA), '-i', str(TMP / 't0.png'),
        '-filter_complex', fl, '-map', '[v]', '-map', '[aud]', '-c:v', 'libx264', '-profile:v', 'main', '-pix_fmt', 'yuv420p', '-crf', '22', '-preset', 'slow',
        '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(sal)])
    print(sal, sal.stat().st_size // 1024, 'KB')


if __name__ == '__main__':
    main()
