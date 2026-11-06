"""Rafael BYD · 4 nov 2026 · dos videos con el material REAL que mandó el 3 nov.

  A (guion nuestro)      : su cara en cortes rápidos + voz clonada diciendo el guion v2 + tomas del auto.
  B (guion que le pasó Carlos el 2 nov): sus 3 tomas reales con SU voz grabada + cierre con voz clonada.

Glimmer calificó su material 6/10: Oferta 3 (no hay oferta comercial hasta mañana),
Confianza 5 (contrapicados), Mensajes calificados 4 (falta filtro de zona/modelo).
Por eso los dos videos llevan en pantalla el filtro «Azcapotzalco y alrededores» y
el motivo para escribir es la PRUEBA DE MANEJO (no se inventa ningún precio ni bono).

Uso: python3 clientes/Rafael_BYD/armar_rafael_v5.py [A|B|AB]
"""
import json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

R = Path('/workspaces/Nexusv2.0launch18octubre'); sys.path.insert(0, str(R / 'clientes/_escenas_carlos'))
from subs_png import trozos, png_sub, overlays, FB
A = R / 'clientes/Rafael_BYD'; D = A / 'v5_20261104'; T = D / 'tmp'; T.mkdir(parents=True, exist_ok=True)
FF = imageio_ffmpeg.get_ffmpeg_exe(); SFX = R / 'clientes/Guillermo/video/sfx'
WA = R / 'clientes/Rafael_BYD/whatsapp/del_cliente'
CARA = WA / '20261103_122142_video_0001A1F1.mp4'      # 8.7 s «gasolina cara…» (Glimmer: sirve tal cual, 8)
KING = WA / '20261103_125015_video_78148F8F.mp4'      # 16.3 s «te presento el nuevo BYD King 2027…»
AUTO = WA / '20261103_130520_video_CC74BCE2.mp4'      # 42.9 s recorrido: exterior, interior, volante (horizontal)
FRENTE = WA / '20261103_125222_video_B32B0973.mp4'    # 11.8 s auto de frente (horizontal)
W, H = 720, 1280; TEL = '55 7386 9438'
dur = lambda p: (lambda e: sum(float(x) * 60 ** i for i, x in enumerate(reversed(e.split('Duration: ')[1].split(',')[0].split(':')))))(
    subprocess.run([FF, '-i', str(p)], capture_output=True, text=True).stderr)


def rotulo(texto, ruta, tam=46, ancho=W, color='white', fondo=None):
    f = ImageFont.truetype(FB, tam)
    im = Image.new('RGBA', (ancho, tam + 34), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    while d.textlength(texto, font=f) > ancho - 40: tam -= 2; f = ImageFont.truetype(FB, tam)
    x = (ancho - d.textlength(texto, font=f)) / 2
    if fondo: d.rounded_rectangle([x - 18, 6, x + d.textlength(texto, font=f) + 18, tam + 28], radius=14, fill=fondo)
    d.text((x, 12), texto, font=f, fill=color, stroke_width=4, stroke_fill='black'); im.save(ruta); return ruta


def tarjeta(ruta):
    c = Image.new('RGB', (W, H), (12, 18, 32)); d = ImageDraw.Draw(c)
    t = lambda y, s, tam, col: d.text(((W - d.textlength(s, font=ImageFont.truetype(FB, tam))) / 2, y), s,
                                      font=ImageFont.truetype(FB, tam), fill=col)
    t(300, 'Rafael Hernández Ortiz', 46, 'white'); t(368, 'Asesor BYD Azcapotzalco', 34, (200, 210, 225))
    t(470, 'Song Plus · King · Dolphin', 36, 'white')
    t(530, 'Híbridos y eléctricos', 32, (200, 210, 225))
    d.rounded_rectangle([90, 650, 630, 762], radius=56, fill=(37, 211, 102))
    t(676, 'WhatsApp ' + TEL, 36, 'white')
    t(800, 'Agenda tu prueba de manejo', 38, (255, 214, 0))
    t(862, 'Escribe «BYD»', 34, 'white'); c.save(ruta); return ruta


def correr(ent, fc, mapv, mapa_a, total, out):
    subprocess.run([FF, '-v', 'error', '-y'] + ent + ['-filter_complex', fc, '-map', mapv, '-map', mapa_a,
                    '-t', f'{total:.2f}', '-c:v', 'libx264', '-profile:v', 'main', '-pix_fmt', 'yuv420p',
                    '-crf', '21', '-preset', 'fast', '-c:a', 'aac', '-b:a', '128k', '-ar', '48000',
                    '-movflags', '+faststart', str(out)], check=True)
    print(out, f'{total:.1f}s')


def tiempos(video, frase):
    """segundo en que empieza y acaba la frase dentro del clip (Whisper)."""
    from faster_whisper import WhisperModel
    seg, _ = WhisperModel('medium', compute_type='int8').transcribe(str(video), language='es')
    ss = [s for s in seg if s.text.strip()]
    return (ss[0].start, ss[-1].end) if ss else (0.0, dur(video))


def video_b():
    """Sus 3 tomas reales, con su voz grabada. Cierre con voz clonada + tarjeta."""
    a1, b1 = tiempos(CARA, ''); a2, b2 = tiempos(KING, '')
    i1 = max(a1 - 0.25, 0); d1 = min(min(b1 + 0.35, dur(CARA)) - i1, 8.6)
    i2 = max(a2 - 0.25, 0); d2 = min(min(b2 + 0.35, dur(KING)) - i2, 8.5)   # 4 nov: el clip del King trae mucho paseo mudo
    VOZ6, VOZ4 = A / 'voz/R6.wav', A / 'voz/R4.wav'
    d3, d4 = dur(VOZ6) + 0.5, dur(VOZ4) + 0.6
    TARJ = 3.2; total = d1 + d2 + d3 + d4 + TARJ
    g1 = rotulo('¿Gasolina cara?', T / 'b_g1.png', 58)
    g2 = rotulo('Azcapotzalco y alrededores', T / 'b_g2.png', 38, fondo=(0, 0, 0, 150))
    g3 = rotulo('BYD King 2027 · 205 hp', T / 'b_g3.png', 42, fondo=(0, 0, 0, 150))
    tj = tarjeta(T / 'b_tarjeta.png')
    s6 = trozos(VOZ6, 'Tengo Song Plus, King y Dolphin, híbridos y eléctricos, con autonomía de hasta mil ciento cuarenta y cinco kilómetros.', desfase=d1 + d2)
    s4 = trozos(VOZ4, 'Agenda tu prueba de manejo. Escríbeme la palabra BYD por WhatsApp y te enseño el modelo que va contigo.', desfase=d1 + d2 + d3)
    subs = s6 + s4
    for k, (_, _, s) in enumerate(subs): png_sub(s, T / f'b_s{k}.png')
    ent = ['-ss', f'{i1}', '-t', f'{d1}', '-i', str(CARA), '-ss', f'{i2}', '-t', f'{d2}', '-i', str(KING),
           '-ss', '2', '-t', f'{d3}', '-i', str(AUTO), '-ss', '1', '-t', f'{d4}', '-i', str(FRENTE),
           '-loop', '1', '-t', f'{TARJ}', '-i', str(tj),
           '-loop', '1', '-i', str(g1), '-loop', '1', '-i', str(g2), '-loop', '1', '-i', str(g3)] + \
          sum([['-loop', '1', '-i', str(T / f'b_s{k}.png')] for k in range(len(subs))], [])
    esc = lambda i: (f"[{i}:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps=30,"
                     f"unsharp=5:5:0.6[c{i}];")
    fc = ''.join(esc(i) for i in range(4)) + f"[4:v]scale={W}:{H},setsar=1,fps=30[c4];"
    fc += "[c0][c1][c2][c3][c4]concat=n=5:v=1:a=0[b0];"
    n_s = 8
    fc += f"[b0][5:v]overlay=x=0:y=180:enable='between(t,0.2,{min(3.2, d1):.2f})'[b1];"
    fc += f"[b1][6:v]overlay=x=0:y=H-330:enable='between(t,1.2,{d1:.2f})'[b2];"
    fc += f"[b2][7:v]overlay=x=0:y=180:enable='between(t,{d1 + .4:.2f},{d1 + min(d2, 4.5):.2f})'[b3];"
    fc += overlays([(a, b, n_s + k) for k, (a, b, _) in enumerate(subs)], 'b3', 'v')
    pistas = [(VOZ6, d1 + d2 + 0.25, 1.25), (VOZ4, d1 + d2 + d3 + 0.3, 1.25),
              (SFX / 'whoosh.wav', d1, 0.5), (SFX / 'whoosh.wav', d1 + d2, 0.5), (SFX / 'boom.wav', d1 + d2 + d3 + d4, 0.5)]
    n0 = n_s + len(subs); ent += sum([['-i', str(p)] for p, _, _ in pistas], [])
    fc += f"[0:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{d1:.2f},volume=1.6[a0];"
    fc += f"[1:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{d2:.2f},volume=1.6,adelay={int(d1 * 1000)}|{int(d1 * 1000)}[a1];"
    fc += ''.join(f"[{n0 + i}:a]aresample=48000,aformat=channel_layouts=stereo,volume={v},adelay={int(s * 1000)}|{int(s * 1000)}[p{i}];"
                  for i, (_, s, v) in enumerate(pistas))
    fc += "[a0][a1]" + ''.join(f'[p{i}]' for i in range(len(pistas)))
    fc += f"amix=inputs={2 + len(pistas)}:duration=longest:normalize=0,apad,atrim=0:{total:.2f},loudnorm=I=-14:TP=-1.5[a]"
    correr(ent, fc, '[v]', '[a]', total, D / 'Rafael_BYD_v5B_sus_tomas.mp4')


def video_a():
    """Guion nuestro (v2) con su voz clonada sobre su material nuevo."""
    VOZ = A / 'voz/R3.wav'
    GUION = ('¿Estás listo para comprar un auto eléctrico o híbrido este mes? Soy Rafael Hernández Ortiz, '
             'asesor de BYD Azcapotzalco. Manejamos Song Plus, King y Dolphin. Escríbeme por WhatsApp con la palabra BYD.')
    ZOOM = [1.0, 1.35, 1.75, 2.2]; DC = 0.45; T_IN = len(ZOOM) * DC
    DV = dur(VOZ) + 0.5; TARJ = 3.2; total = T_IN + DV + TARJ
    g1 = rotulo('¿Listo para estrenar auto?', T / 'a_g1.png', 52)
    g2 = rotulo('Azcapotzalco y alrededores', T / 'a_g2.png', 36, fondo=(0, 0, 0, 150))
    tj = tarjeta(T / 'a_tarjeta.png')
    subs = trozos(VOZ, GUION, desfase=T_IN)
    for k, (_, _, s) in enumerate(subs): png_sub(s, T / f'a_s{k}.png')
    mitad = DV / 2
    ent = ['-i', str(CARA), '-ss', '3', '-t', f'{mitad:.2f}', '-i', str(AUTO),
           '-ss', '18', '-t', f'{DV - mitad:.2f}', '-i', str(AUTO), '-loop', '1', '-t', f'{TARJ}', '-i', str(tj),
           '-loop', '1', '-i', str(g1), '-loop', '1', '-i', str(g2)] + \
          sum([['-loop', '1', '-i', str(T / f'a_s{k}.png')] for k in range(len(subs))], [])
    fc = ''
    for j, z in enumerate(ZOOM):
        fc += (f"[0:v]trim={j * DC}:{(j + 1) * DC},setpts=PTS-STARTPTS,scale={W}:{H}:force_original_aspect_ratio=increase,"
               f"crop={W}:{H},crop=iw/{z}:ih/{z}:(iw-iw/{z})*0.5:(ih-ih/{z})*0.45,scale={W}:{H},setsar=1,fps=30[z{j}];")
    fc += (f"[1:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps=30,unsharp=5:5:0.6[m1];"
           f"[2:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps=30,unsharp=5:5:0.6[m2];"
           f"[3:v]scale={W}:{H},setsar=1,fps=30[tj];")
    fc += ''.join(f'[z{j}]' for j in range(len(ZOOM))) + f"[m1][m2][tj]concat=n={len(ZOOM) + 3}:v=1:a=0[b0];"
    fc += f"[b0][4:v]overlay=x=0:y=190:enable='between(t,0,{T_IN:.2f})'[b1];"
    fc += f"[b1][5:v]overlay=x=0:y=H-430:enable='between(t,0.6,{T_IN:.2f})'[b2];"
    fc += overlays([(a, b, 6 + k) for k, (a, b, _) in enumerate(subs)], 'b2', 'v')
    pistas = [(SFX / 'clic.wav', j * DC, 0.6) for j in range(len(ZOOM))] + \
             [(SFX / 'whoosh.wav', T_IN - 0.15, 0.7), (VOZ, T_IN, 1.3), (SFX / 'boom.wav', T_IN + DV, 0.55)]
    n0 = 6 + len(subs); ent += sum([['-i', str(p)] for p, _, _ in pistas], [])
    fc += ''.join(f"[{n0 + i}:a]aresample=48000,aformat=channel_layouts=stereo,volume={v},adelay={int(s * 1000)}|{int(s * 1000)}[p{i}];"
                  for i, (_, s, v) in enumerate(pistas))
    fc += ''.join(f'[p{i}]' for i in range(len(pistas)))
    fc += f"amix=inputs={len(pistas)}:duration=longest:normalize=0,apad,atrim=0:{total:.2f},loudnorm=I=-14:TP=-1.5[a]"
    correr(ent, fc, '[v]', '[a]', total, D / 'Rafael_BYD_v5A_guion_nuestro.mp4')


if __name__ == '__main__':
    q = (sys.argv[1] if len(sys.argv) > 1 else 'AB').upper()
    if 'B' in q: video_b()
    if 'A' in q: video_a()
