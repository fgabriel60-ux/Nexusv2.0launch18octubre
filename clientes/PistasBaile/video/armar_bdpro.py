"""BD Pro Monterrey (pistas de baile) v1 al estilo de su referencia de Instagram («El proceso vs. El resultado»): gancho con el salón vacío → SU equipo real
instalando → SUS diseños reales → EL RESULTADO: sus pistas reales transformadas en boda, XV y evento de empresa (Qwen + H3) → pareja real bailando → tarjeta.
Voz clonada del dueño (V1 a V5). Uso: python3 armar_bdpro.py"""
import subprocess, sys
from pathlib import Path
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/XV')
import imageio_ffmpeg
from PIL import Image, ImageDraw
from armar_xv import fu, tex

AQUI = Path(__file__).resolve().parent
MAT = AQUI.parent / 'material'
FF = imageio_ffmpeg.get_ffmpeg_exe()
TMP = Path('/tmp/claude-1000/-workspaces-Nexusv2-0launch18octubre/3f2c6b79-5aa7-409f-95e2-6c1cf5560d47/scratchpad/bdpro'); TMP.mkdir(parents=True, exist_ok=True)
MUSICA = AQUI.parents[1] / 'XV' / 'musica_suave_s7.wav'
W, H = 1080, 1920
TARJ = 3.6
VOCES = ['V1', 'V2', 'V3', 'V4', 'V5']
# por frase de voz: [(video, inicio, duración, texto en pantalla)]; las duraciones de cada frase suman lo que dura su voz
FRASES = [
    [('tomas/AD2_hacienda', 0.0, 3.32, ['¿TU SALÓN SE VE VACÍO?', 'PARA TU BODA O TUS XV'])],
    [(MAT / '17_1024_0029', 0.0, 3.97, ['EL PROCESO', 'PISTA PERSONALIZADA'])],
    [(MAT / '14_1024_0029', 2.0, 2.0, ['VINIL CON TU MONOGRAMA', 'TALAVERA · AJEDREZ']), (MAT / '16_1024_0029', 1.0, 2.0, None),   # el 15 trae marca de agua de InShot
     (MAT / '20_1024_0029', 0.5, 2.0, None), (MAT / '42_1024_0031', 3.0, 2.1, ['BLANCA, NEGRA', 'O ILUMINADA'])],
    [('tomas/AD1_jardin', 0.0, 5.0, ['EL RESULTADO', 'TU PISTA, TU MOMENTO']), ('tomas/AD3_empresa', 0.67, 4.33, ['AUDIO · ESCENARIO', 'PANTALLAS LED PARA EMPRESAS'])],
    [(MAT / '22_1024_0029', 5.0, 5.22, ['COTIZA POR MEDIDA', 'MONTERREY Y ÁREA METROPOLITANA'])],
]


def ff(a):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1800:])


def tarjeta(ruta):
    img = Image.new('RGB', (W, H), (12, 12, 14)); d = ImageDraw.Draw(img)
    ORO, VERDE = (226, 186, 98), (37, 211, 102)
    def c(t, y, tam, col, peso='Black'):
        f = fu(tam, peso)
        while d.textlength(t, font=f) > W - 110: tam -= 2; f = fu(tam, peso)
        d.text(((W - d.textlength(t, font=f)) / 2, y), t, font=f, fill=col)
    c('BD PRO', 540, 150, (255, 255, 255)); c('MONTERREY EVENTOS', 710, 60, ORO)
    c('PISTAS DE BAILE PERSONALIZADAS', 810, 44, (255, 255, 255), 'Bold')
    t = 'COTIZA POR WHATSAPP'; f = fu(50, 'ExtraBold'); a = d.textlength(t, font=f) + 110
    d.rounded_rectangle(((W - a) / 2, 960, (W + a) / 2, 1090), 65, fill=VERDE); d.text(((W - a) / 2 + 55, 995), t, font=f, fill=(255, 255, 255))
    c('81 3261 3554', 1160, 104, ORO)
    img.save(ruta)


def main():
    tarjeta(TMP / 'tarjeta.png')
    tomas = [t for fr in FRASES for t in fr]
    T = sum(t[2] for t in tomas); TOTAL = T + TARJ
    ent, fl = [], ''
    for i, (v, ini, dur, _) in enumerate(tomas):
        ruta = AQUI / f'{v}.mp4' if isinstance(v, str) else Path(f'{v}.mp4')
        ent += ['-ss', str(ini), '-t', f'{dur + 0.3:.2f}', '-i', str(ruta)]
        fl += (f'[{i}:v]scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},unsharp=5:5:0.6,eq=contrast=1.05:saturation=1.12,'
               f'fps=30,setsar=1,format=yuv420p,tpad=stop_mode=clone:stop_duration=2,trim=duration={dur:.2f},setpts=PTS-STARTPTS[c{i}];')
    k = len(tomas)
    ent += ['-loop', '1', '-t', str(TARJ), '-i', str(TMP / 'tarjeta.png')]
    fl += f'[{k}:v]scale={W}:{H},fps=30,setsar=1,format=yuv420p[tj];' + ''.join(f'[c{i}]' for i in range(k)) + f'[tj]concat=n={k + 1}:v=1:a=0[base];'
    textos, t0 = [], 0.0   # un texto dura hasta que aparece el siguiente
    for v, ini, dur, lin in tomas:
        if lin: textos.append([lin, t0, t0 + dur])
        elif textos: textos[-1][2] = t0 + dur
        t0 += dur
    cur, b = 'base', k + 1
    for j, (lin, a, z) in enumerate(textos):
        p = TMP / f't{j}.png'; tex(lin, p, 1380, tam=74); ent += ['-loop', '1', '-t', f'{TOTAL:.1f}', '-i', str(p)]
        fl += f"[{cur}][{b + j}:v]overlay=0:0:enable='between(t,{a + 0.1:.2f},{z - 0.05:.2f})'[o{j}];"; cur = f'o{j}'
    a0 = b + len(textos)
    voz = TMP / 'voz.wav'
    ff([x for v in VOCES for x in ('-i', str(AQUI / 'voz' / f'{v}.mp3'))] + ['-filter_complex',
       ''.join(f'[{i}:a]aresample=48000[a{i}];' for i in range(len(VOCES))) + ''.join(f'[a{i}]' for i in range(len(VOCES))) + f'concat=n={len(VOCES)}:v=0:a=1[v]',
       '-map', '[v]', str(voz)])
    ent += ['-i', str(MUSICA), '-i', str(voz)]
    fl += (f"[{a0}:a]aresample=48000,aloop=loop=-1:size=2147483647,volume=0.2,afade=t=in:st=0:d=0.5,afade=t=out:st={TOTAL - 1.2:.2f}:d=1.2,atrim=0:{TOTAL:.2f}[mu];"
           f"[{a0 + 1}:a]aresample=48000[vz];[mu][vz]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]")
    hd = TMP / 'hd.mp4'; sal = AQUI / 'BDPro_proceso_vs_resultado_v1.mp4'
    ff(ent + ['-filter_complex', fl, '-map', f'[{cur}]', '-map', '[a]', '-t', f'{TOTAL:.2f}', '-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', str(hd)])
    ff(['-i', str(hd), '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-pix_fmt', 'yuv420p', '-crf', '24', '-preset', 'slow', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(sal)])
    print(sal, sal.stat().st_size // 1024, 'KB', f'{TOTAL:.1f}s')


if __name__ == '__main__':
    main()
