"""Mariano · Bugambilia gancho helicóptero v1 (1 nov 2026), instrucciones de Carlos en el chat de Mariano (31 oct 20:04, réplica del reel DcJgZ1Lk5ym):
helicóptero sobre su casa → baja por la cuerda → habla con su voz clonada (BUG) → RECORRIDO REAL de la Bugambilia (video que mandó Mariano el 31 oct)
en hard cut con clic → tarjeta final. Datos: Bugambilia 2 pisos desde $2.4 MDP (letrero de su video)."""
import subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg
R = Path('/workspaces/Nexusv2.0launch18octubre'); sys.path.insert(0, str(R / 'clientes/_escenas_carlos'))
from subs_png import trozos, png_sub, overlays, FB
A = R / 'clientes/Mariano/video/helicoptero'; G = A / 'bug_v1'; T = G / 'tmp'; T.mkdir(exist_ok=True); FF = imageio_ffmpeg.get_ffmpeg_exe()
SFX = R / 'clientes/Guillermo/video/sfx'; VOZ = A / 'voz/BUG.wav'; REC = A / 'ref/10-31_1956_9F93B698.mp4'
MUS = R / 'entregables/prospectos_sancarlos_20261031/musica/villa_s3.wav'
GUION = '¿Buscas casa en Rosarito? Así se llega a la Bugambilia de Vizcaíno Residencial. Desde 2.4 millones.'
W, H = 720, 1280; D1, D2 = 2.8, 2.8
dur = lambda p: (lambda e: sum(float(x) * 60 ** i for i, x in enumerate(reversed(e.split('Duration: ')[1].split(',')[0].split(':')))))(subprocess.run([FF, '-i', str(p)], capture_output=True, text=True).stderr)
D3 = dur(VOZ) + 0.3; T3 = D1 + D2
CORTES = [3.6, 6.2, 9.0, 12.5, 16.0, 19.5, 23.0, 26.5, 30.0, 33.5, 37.0, 41.0]; DC = 1.1; T_REC = T3 + D3; D_REC = len(CORTES) * DC
TARJ = 3.2; TOTAL = T_REC + D_REC + TARJ

def txt(d, y, t, tam, color):
    f = ImageFont.truetype(FB, tam); d.text(((W - d.textlength(t, font=f)) / 2, y), t, font=f, fill=color)
c = Image.new('RGB', (W, H), (14, 24, 40)); d = ImageDraw.Draw(c)
txt(d, 300, 'BUGAMBILIA', 66, (230, 190, 120)); txt(d, 390, 'Vizcaíno Residencial · Rosarito, B.C.', 30, 'white')
txt(d, 500, 'Casa de 2 pisos', 40, 'white'); txt(d, 570, 'Desde $2.4 MDP', 58, (230, 190, 120))
d.rounded_rectangle([120, 760, 600, 860], radius=50, fill=(37, 211, 102)); txt(d, 785, 'Escribe «BUGAMBILIA»', 38, 'white')
txt(d, 890, 'por WhatsApp y agenda tu visita', 30, 'white'); c.save(T / 'tarjeta.png')
g = Image.new('RGBA', (W, 120), (0, 0, 0, 0)); dd = ImageDraw.Draw(g); f = ImageFont.truetype(FB, 40); t = 'Así se llega a tu casa nueva'
dd.text(((W - dd.textlength(t, font=f)) / 2, 30), t, font=f, fill='white', stroke_width=5, stroke_fill='black'); g.save(T / 'gancho.png')
subs = trozos(VOZ, GUION, desfase=T3)
for k, (_, _, s) in enumerate(subs): png_sub(s, T / f's{k}.png')

ent = ['-i', str(G / 'KH1_heli.mp4'), '-i', str(G / 'KH2_cuerda.mp4'), '-i', str(G / 'KH3_habla.mp4'), '-i', str(REC),
       '-loop', '1', '-t', str(TARJ), '-i', str(T / 'tarjeta.png'), '-loop', '1', '-i', str(T / 'gancho.png')] + sum([['-loop', '1', '-i', str(T / f's{k}.png')] for k in range(len(subs))], [])
norm = f'scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps=30,format=yuv420p'
fc = (f"[0:v]trim=0:{D1},setpts=PTS-STARTPTS,{norm}[k1];[1:v]trim=0:{D2},setpts=PTS-STARTPTS,{norm}[k2];"
      f"[2:v]{norm},tpad=stop_mode=clone:stop_duration=2,trim=0:{D3},setpts=PTS-STARTPTS[k3];")
for j, s in enumerate(CORTES):
    fc += f"[3:v]trim={s}:{s + DC},setpts=PTS-STARTPTS,{norm}[r{j}];"
fc += f"[4:v]{norm}[tj];[k1][k2][k3]" + ''.join(f'[r{j}]' for j in range(len(CORTES))) + f"[tj]concat=n={len(CORTES) + 4}:v=1:a=0[b0];"
fc += f"[b0][5:v]overlay=x=0:y=140:enable='between(t,0,{T3})'[b1];"
fc += overlays([(a, b, 6 + k) for k, (a, b, _) in enumerate(subs)], 'b1', 'v')
n0 = 6 + len(subs)
pistas = [(G / 'KH1_heli.mp4', 0, 0.9, D1), (SFX / 'whoosh.wav', D1 - 0.15, 0.8, None), (VOZ, T3, 1.3, None)] + \
         [(SFX / 'clic.wav', T_REC + j * DC, 0.6, None) for j in range(len(CORTES))] + [(SFX / 'boom.wav', T_REC + D_REC, 0.6, None)]
ent += sum([['-i', str(p)] for p, *_ in pistas], []) + ['-i', str(MUS)]
for i, (p, s, v, lim) in enumerate(pistas):
    cut = f'atrim=0:{lim},' if lim else ''
    fc += f"[{n0 + i}:a]{cut}aresample=48000,aformat=channel_layouts=stereo,volume={v},adelay={int(s * 1000)}|{int(s * 1000)}[p{i}];"
m = n0 + len(pistas)
fc += f"[{m}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{D_REC + TARJ},volume=0.35,afade=t=in:d=0.3,afade=t=out:st={D_REC + TARJ - 0.8}:d=0.8,adelay={int(T_REC * 1000)}|{int(T_REC * 1000)}[mu];"
fc += ''.join(f'[p{i}]' for i in range(len(pistas))) + f"[mu]amix=inputs={len(pistas) + 1}:duration=longest:normalize=0,apad,atrim=0:{TOTAL:.2f},loudnorm=I=-14:TP=-1.5[a]"
out = R / 'clientes/Mariano/video/Vizcaino_Mariano_bugambilia_helicoptero_v1.mp4'
subprocess.run([FF, '-v', 'error', '-y'] + ent + ['-filter_complex', fc, '-map', '[v]', '-map', '[a]', '-t', f'{TOTAL:.2f}', '-c:v', 'libx264', '-profile:v', 'main',
                '-pix_fmt', 'yuv420p', '-crf', '22', '-preset', 'fast', '-c:a', 'aac', '-b:a', '128k', '-ar', '48000', '-movflags', '+faststart', str(out)], check=True)
print(out, f'{TOTAL:.1f}s')
