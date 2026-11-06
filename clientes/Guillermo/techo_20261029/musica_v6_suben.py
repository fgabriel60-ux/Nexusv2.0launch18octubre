"""Guillermo · música propia (beat sintetizado, sin derechos) para el video de proceso del techo: intro filtrada con las vigas, DROP cuando empiezan las láminas, boom al cerrar.
Uso: python3 musica_techo.py"""
import subprocess, sys
from pathlib import Path
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/Mariano/video')
import imageio_ffmpeg
from spiderman_musica import beat

AQUI = Path(__file__).resolve().parent; S = AQUI / 'salida_v6_suben'
FF = imageio_ffmpeg.get_ffmpeg_exe()
SFX = AQUI.parent / 'video' / 'sfx'
TOTAL, DROP = 10.0, 5.0
wav = S / 'beat_techo.wav'; beat(str(wav), DROP, TOTAL)
fl = (f"[1:a]aresample=44100,volume=0.85,atrim=0:{TOTAL},afade=t=out:st={TOTAL - 1.0}:d=1.0[m];"
      f"[2:a]aresample=44100,volume=0.6,adelay={int((DROP - 0.35) * 1000)}|{int((DROP - 0.35) * 1000)}[w];"
      f"[3:a]aresample=44100,volume=0.5,adelay={int((TOTAL - 1.3) * 1000)}|{int((TOTAL - 1.3) * 1000)}[b];"
      "[m][w][b]amix=inputs=3:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]")
sal = S / 'Guillermo_techo_proceso_musica.mp4'
subprocess.run([FF, '-y', '-i', str(S / 'Guillermo_techo_proceso.mp4'), '-i', str(wav), '-i', str(SFX / 'whoosh.wav'), '-i', str(SFX / 'boom.wav'), '-filter_complex', fl,
                '-map', '0:v', '-map', '[a]', '-t', f'{TOTAL}', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', str(sal)], check=True, capture_output=True)
print(sal, sal.stat().st_size // 1024, 'KB')
