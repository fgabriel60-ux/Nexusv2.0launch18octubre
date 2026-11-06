"""Tatuador Adrián · HARD CUT v2 (31 oct): frames de ÉL generados (Qwen + MiniMax L40S, estudio oscuro neón como la ref adrian_1957)
intercalados al golpe con SUS tatuajes reales; tarjeta final de la v1 (precio + WhatsApp)."""
import subprocess
from pathlib import Path
A = Path(__file__).parent; S = A / 'frames_v1/salida'; WA = A / 'whatsapp'
F = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
BEAT = A.parents[0] / 'Guillermo/techo_20261029/salida_v6_caen/beat_techo.wav'
C = 0.96
P = [(S / 'AT1_entra.mp4', 0.2, 2 * C, '¿TU PRÓXIMO TATUAJE?'), (S / 'AT2_cara.mp4', 0.3, C, None), (WA / '1029_180319_el_video.mp4', 4.0, C, 'QUE SEA ÚNICO'),
     (S / 'AT3_manos.mp4', 0.3, C, None), (WA / '1029_180320_el_video.mp4', 2.0, C, 'DISEÑO PERSONALIZADO'), (S / 'AT4_ring.mp4', 0.3, C, None),
     (WA / '1029_181226_el_video.mp4', 3.0, C, None), (WA / '1029_180322_el_video.mp4', 2.0, C, 'TU IDEA · TU ESTILO'), (S / 'AT5_maquina.mp4', 0.3, C, None),
     (WA / '1029_180327_el_video.mp4', 3.0, C, None), (WA / '1029_180321_el_video.mp4', 5.0, C, 'CENTRO DE CANCÚN'), (S / 'AT6_cierre.mp4', 0.3, 2 * C, 'ADRIÁN · TATUADOR')]
T = A / 'hardcut_v2'; T.mkdir(exist_ok=True); segs = []
for k, (v, a, d, txt) in enumerate(P):
    dt = f",drawtext=fontfile={F}:text='{txt}':fontsize={min(54, int(980 / len(txt)))}:fontcolor=white:borderw=5:bordercolor=black:x=(w-text_w)/2:y=h*0.72" if txt else ''
    o = T / f's{k:02d}.mp4'; segs.append(o)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(a), '-t', str(d + .1), '-i', str(v), '-vf',
                    f'scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1,fps=30,trim=0:{d},setpts=PTS-STARTPTS{dt}',
                    '-an', '-c:v', 'libx264', '-crf', '19', '-pix_fmt', 'yuv420p', str(o)], check=True)
o = T / 'tarjeta.mp4'; segs.append(o)
v1 = A / 'hardcut_v1/Tatuador_hardcut_v1.mp4'
dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(v1)], capture_output=True, text=True).stdout)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(dur - 3.0), '-i', str(v1), '-an', '-vf', 'fps=30,setsar=1', '-c:v', 'libx264', '-crf', '19', '-pix_fmt', 'yuv420p', str(o)], check=True)
(T / 'lista.txt').write_text(''.join(f"file '{s}'\n" for s in segs))
tot = sum(p[2] for p in P) + 3.0
out = A / 'hardcut_v2/Tatuador_hardcut_v2.mp4'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(T / 'lista.txt'), '-stream_loop', '-1', '-i', str(BEAT), '-filter_complex',
                f'[1:a]atrim=0:{tot},afade=t=out:st={tot - 1}:d=1[a]', '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-shortest', str(out)], check=True)
print('listo', out, round(tot, 1))
