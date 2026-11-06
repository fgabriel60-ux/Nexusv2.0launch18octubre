"""Rafael BYD gancho v2 (1 nov 2026), réplica del reel DO4g4PkEcis (pedido de Carlos):
0-2.5 s Rafael serio frente a la agencia BYD con 5 cortes secos que se acercan (clic en cada uno) + «¿Listo para comprar auto?»;
whoosh → dentro del BYD (cámara de tablero) diciendo el guion de Glimmer con su voz clonada (R3) y subtítulos; tarjeta final con WhatsApp."""
import subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg
R = Path('/workspaces/Nexusv2.0launch18octubre'); sys.path.insert(0, str(R / 'clientes/_escenas_carlos'))
from subs_png import trozos, png_sub, overlays, FB
A = R / 'clientes/Rafael_BYD'; G = A / 'gancho_v2'; T = G / 'tmp'; T.mkdir(exist_ok=True); FF = imageio_ffmpeg.get_ffmpeg_exe()
SFX = R / 'clientes/Guillermo/video/sfx'; VOZ = A / 'voz/R3.wav'
GUION = '¿Estás listo para comprar un auto eléctrico o híbrido este mes? Soy Rafael Hernández Ortiz, asesor de BYD Azcapotzalco. Manejamos Song Plus, King y Dolphin. Escríbeme por WhatsApp con la palabra BYD.'
W, H = 720, 1280; ZOOM = [1.0, 1.3, 1.65, 2.1, 2.6]; DC = 0.5; CX, CY = 0.5, 0.52; T_IN = len(ZOOM) * DC
dur = lambda p: (lambda e: sum(float(x) * 60 ** i for i, x in enumerate(reversed(e.split('Duration: ')[1].split(',')[0].split(':')))))(subprocess.run([FF, '-i', str(p)], capture_output=True, text=True).stderr)
D_IN = dur(VOZ) + 0.4; TARJ = 3.0; TOTAL = T_IN + D_IN + TARJ

def txt(d, y, t, tam, color, w=W):
    f = ImageFont.truetype(FB, tam); d.text(((w - d.textlength(t, font=f)) / 2, y), t, font=f, fill=color, stroke_width=0)
# tarjeta final
c = Image.new('RGB', (W, H), (12, 18, 32)); d = ImageDraw.Draw(c)
txt(d, 330, 'Rafael Hernández Ortiz', 46, 'white'); txt(d, 400, 'Asesor BYD Azcapotzalco', 36, (200, 210, 225))
txt(d, 520, 'Song Plus · King · Dolphin', 38, 'white')
d.rounded_rectangle([110, 680, 610, 790], radius=55, fill=(37, 211, 102)); txt(d, 708, 'WhatsApp 55 7386 9438', 36, 'white')
txt(d, 840, 'Escribe «BYD»', 44, (255, 214, 0)); c.save(T / 'tarjeta.png')
# texto del gancho (primeros 2.5 s)
g = Image.new('RGBA', (W, 130), (0, 0, 0, 0)); d = ImageDraw.Draw(g); t = '¿Listo para comprar auto?'; tam = 50
while ImageDraw.Draw(g).textlength(t, font=ImageFont.truetype(FB, tam)) > W - 60: tam -= 2
f = ImageFont.truetype(FB, tam)
d.text(((W - d.textlength(t, font=f)) / 2, 30), t, font=f, fill='white', stroke_width=5, stroke_fill='black'); g.save(T / 'gancho.png')
subs = trozos(VOZ, GUION, desfase=T_IN)
for k, (_, _, s) in enumerate(subs): png_sub(s, T / f's{k}.png')

ent = ['-i', str(G / 'KX1_afuera.mp4'), '-i', str(G / 'KX2_dentro.mp4'), '-loop', '1', '-t', str(TARJ), '-i', str(T / 'tarjeta.png'),
       '-loop', '1', '-i', str(T / 'gancho.png')] + sum([['-loop', '1', '-i', str(T / f's{k}.png')] for k in range(len(subs))], [])
fc = ''
for j, z in enumerate(ZOOM):
    fc += (f"[0:v]trim={j * DC}:{(j + 1) * DC},setpts=PTS-STARTPTS,scale={W}:{H},crop=iw/{z}:ih/{z}:(iw-iw/{z})*{CX}:(ih-ih/{z})*{CY},"
           f"scale={W}:{H},setsar=1,fps=30[z{j}];")
fc += f"[1:v]trim=0:{D_IN},setpts=PTS-STARTPTS,scale={W}:{H},setsar=1,fps=30,tpad=stop_mode=clone:stop_duration=2,trim=0:{D_IN}[dentro];"
fc += f"[2:v]scale={W}:{H},setsar=1,fps=30,format=yuv420p[tj];"
fc += ''.join(f'[z{j}]' for j in range(len(ZOOM))) + f"[dentro][tj]concat=n={len(ZOOM) + 2}:v=1:a=0[b0];"
fc += f"[b0][3:v]overlay=x=0:y=150:enable='between(t,0,{T_IN})'[b1];"
fc += overlays([(a, b, 4 + k) for k, (a, b, _) in enumerate(subs)], 'b1', 'v')
# audio: clic por corte, whoosh a la entrada, voz, golpe a la tarjeta
pistas = [(SFX / 'clic.wav', j * DC, 0.7) for j in range(len(ZOOM))] + [(SFX / 'whoosh.wav', T_IN - 0.15, 0.8), (VOZ, T_IN, 1.3), (SFX / 'boom.wav', T_IN + D_IN, 0.6)]
n0 = 4 + len(subs); ent += sum([['-i', str(p)] for p, _, _ in pistas], [])
fc += ''.join(f"[{n0 + i}:a]aresample=48000,aformat=channel_layouts=stereo,volume={v},adelay={int(s * 1000)}|{int(s * 1000)}[p{i}];" for i, (_, s, v) in enumerate(pistas))
fc += ''.join(f'[p{i}]' for i in range(len(pistas))) + f"amix=inputs={len(pistas)}:duration=longest:normalize=0,apad,atrim=0:{TOTAL:.2f},loudnorm=I=-14:TP=-1.5[a]"
out = A / 'Rafael_BYD_gancho_v2.mp4'
subprocess.run([FF, '-v', 'error', '-y'] + ent + ['-filter_complex', fc, '-map', '[v]', '-map', '[a]', '-t', f'{TOTAL:.2f}', '-c:v', 'libx264', '-profile:v', 'main',
                '-pix_fmt', 'yuv420p', '-crf', '21', '-preset', 'fast', '-c:a', 'aac', '-b:a', '128k', '-ar', '48000', '-movflags', '+faststart', str(out)], check=True)
print(out, f'{TOTAL:.1f}s')
