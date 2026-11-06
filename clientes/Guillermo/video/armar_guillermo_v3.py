"""Guillermo (Proyectos Metálicos Vicens) · 3 videos con SU voz clonada: gancho con IA → 2 escenas → montaje de obras reales en cortes secos con efectos
de sonido (whoosh + golpe) → tarjeta de WhatsApp. Uso: python3 armar_guillermo_v3.py [P|T|Z]"""
import subprocess, sys
from pathlib import Path
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/XV')
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageOps
from armar_xv import fu, tex

AQUI = Path(__file__).resolve().parent
OBRAS = AQUI.parent / 'whatsapp' / 'del_cliente'
FF = imageio_ffmpeg.get_ffmpeg_exe()
MUSICA = AQUI.parents[1] / 'XV' / 'musica_suave_s7.wav'
W, H = 1080, 1920
D_ESC, D_CORTE, TARJ = 4.4, 0.34, 3.6
FOTOS = ['170425', '170743', '170712', '170426', '164359', '170524', '170744', '170428', '170717', '164400']
VIDEOS = {  # escenas (archivo, texto), voces por escena, palabra del CTA, orden del montaje empezando por lo más parecido
    'P': ([('tomas_v3/H_pergola_se_arma', ['ASÍ SE ARMA', 'TU PÉRGOLA EN PUEBLA']), ('tomas/G2_colocacion', ['TECHO TRANSLÚCIDO', 'INSTALADO POR NUESTRO EQUIPO']),
           ('tomas/G4_cielo', ['ASÍ QUEDA', 'ESTRUCTURA DE ACERO'])], ['P1', 'P2', 'P3'], 'PÉRGOLA', 'CP', ['170425', '170743', '164359', '170744', '170428', '170426', '164400', '170712', '170524', '170717']),
    'T': ([('tomas_v3/H_techo_se_arma', ['¿NECESITAS TECHAR', 'TU PATIO, ESCUELA O NAVE?']), ('tomas_v3/T2_techumbre', ['ESTRUCTURA DE ACERO', 'Y LÁMINA']),
           ('tomas_v3/T3_nave', ['TECHUMBRES GRANDES', 'TERMINADAS Y SEGURAS'])], ['T1', 'T2', 'T3'], 'TECHO', 'CT', ['170712', '170524', '170717', '170426', '170743', '164359', '170425', '170744', '164400', '170428']),
    'Z': ([('tomas_v3/H_zaguan_se_arma', ['ZAGUANES Y PORTONES', 'CON CELOSÍA']), ('tomas_v3/Z2_celosia', ['ACERO HECHO EN PUEBLA', 'FUERTE Y ELEGANTE']),
           ('tomas/G3_terminada', ['BIEN TERMINADOS', 'DE PRINCIPIO A FIN'])], ['Z1', 'Z2', 'Z3'], 'ZAGUÁN', 'CZ', ['170428', '170425', '170427', '170743', '170712', '164359', '170524', '170426', '170744', '170717']),
    'C': ([('tomas_v3/N3_zaguan', ['ZAGUANES, CORTINAS', 'Y PUERTAS DE ACERO']), ('tomas_v3/N1_cortina', ['CORTINAS METÁLICAS', 'PARA TU NEGOCIO']),
           ('tomas_v3/N2_puerta', ['PUERTAS DE HERRERÍA', 'PARA TU CASA'])], ['C1', 'C2', 'C3'], '«COTIZAR»', 'CC', ['170428', '170425', '170743', '170712', '164359', '170524', '170426', '170744', '170717', '170427']),
}


def ff(a):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1800:])


def tarjeta(ruta, palabra):
    img = Image.new('RGB', (W, H), (14, 14, 16)); d = ImageDraw.Draw(img)
    ORO, VERDE = (255, 196, 60), (37, 211, 102)
    def c(t, y, tam, col, peso='Black'):
        f = fu(tam, peso)
        while d.textlength(t, font=f) > W - 110: tam -= 2; f = fu(tam, peso)
        d.text(((W - d.textlength(t, font=f)) / 2, y), t, font=f, fill=col)
    c('PROYECTOS METÁLICOS', 560, 92, (255, 255, 255)); c('VICENS', 670, 120, ORO)
    c('PUEBLA · +15 AÑOS DE EXPERIENCIA', 830, 44, (255, 255, 255), 'Bold')
    t = f'ESCRIBE {palabra} POR WHATSAPP'; f = fu(46, 'ExtraBold'); a = d.textlength(t, font=f) + 110
    d.rounded_rectangle(((W - a) / 2, 960, (W + a) / 2, 1090), 65, fill=VERDE); d.text(((W - a) / 2 + 55, 997), t, font=f, fill=(255, 255, 255))
    c('231 231 1066', 1160, 96, ORO)
    img.save(ruta)


def main(clave):
    escenas, voces, palabra, cta, orden = VIDEOS[clave]
    tmp = Path(f'/tmp/claude-1000/-workspaces-Nexusv2-0launch18octubre/7f4b01e6-9d5b-409e-acca-ec7fedd1520c/scratchpad/guillermo_{clave}'); tmp.mkdir(parents=True, exist_ok=True)
    tarjeta(tmp / 'tarjeta.png', palabra)
    for i, f in enumerate(orden):   # cuadros del montaje: 9:16 llenos
        im = ImageOps.fit(ImageOps.exif_transpose(Image.open(OBRAS / f'20261022_{f}_image.jpg')).convert('RGB'), (W, H), Image.LANCZOS); im.save(tmp / f'm{i:02d}.jpg')
    T_MONT = len(escenas) * D_ESC; D_MONT = len(orden) * D_CORTE; T_TARJ = T_MONT + D_MONT; TOTAL = T_TARJ + TARJ
    ent, fl = [], ''
    for i, (n, _) in enumerate(escenas):
        ent += ['-i', str(AQUI / f'{n}.mp4')]
        fl += f'[{i}:v]scale={W}:{H}:flags=lanczos,unsharp=5:5:0.6,eq=contrast=1.05:saturation=1.1,fps=30,setsar=1,format=yuv420p,tpad=stop_mode=clone:stop_duration=1,trim=duration={D_ESC},setpts=PTS-STARTPTS[e{i}];'
    k = len(escenas)
    for j in range(len(orden)):
        ent += ['-loop', '1', '-t', str(D_CORTE), '-i', str(tmp / f'm{j:02d}.jpg')]
        fl += f"[{k + j}:v]scale={int(W * 1.08)}:{int(H * 1.08)},crop={W}:{H},fps=30,setsar=1,format=yuv420p,trim=duration={D_CORTE},setpts=PTS-STARTPTS[m{j}];"
    k2 = k + len(orden)
    ent += ['-loop', '1', '-t', str(TARJ), '-i', str(tmp / 'tarjeta.png')]
    fl += f'[{k2}:v]scale={W}:{H},fps=30,setsar=1,format=yuv420p[tj];'
    fl += ''.join(f'[e{i}]' for i in range(k)) + ''.join(f'[m{j}]' for j in range(len(orden))) + f'[tj]concat=n={k + len(orden) + 1}:v=1:a=0[base];'
    textos = [(lin, i * D_ESC + 0.15, (i + 1) * D_ESC - 0.1) for i, (_, lin) in enumerate(escenas)] + [(['OBRAS REALES', '+15 AÑOS DE EXPERIENCIA'], T_MONT, T_TARJ)]
    cur, b = 'base', k2 + 1
    for j, (lin, a, z) in enumerate(textos):
        p = tmp / f't{j}.png'; tex(lin, p, 1380, tam=74); ent += ['-loop', '1', '-t', f'{TOTAL:.1f}', '-i', str(p)]
        fl += f"[{cur}][{b + j}:v]overlay=0:0:enable='between(t,{a:.2f},{z:.2f})'[o{j}];"; cur = f'o{j}'
    a0 = b + len(textos)
    VOZ = AQUI / 'voz' / 'v3'; SFX = AQUI / 'sfx'
    pistas = [(VOZ / f'{v}.mp3', i * D_ESC + 0.3) for i, v in enumerate(voces)] + [(VOZ / 'EXP.mp3', T_MONT + 0.15), (VOZ / f'{cta}.mp3', T_TARJ + 0.4)]
    pistas += [(SFX / 'clic.wav', T_MONT + j * D_CORTE) for j in range(len(orden))] + [(SFX / 'boom.wav', T_TARJ)]   # clic de cámara por foto, golpe grave a la tarjeta
    ent += ['-i', str(MUSICA)] + [x for p, _ in pistas for x in ('-i', str(p))]
    fl += f"[{a0}:a]aresample=44100,aloop=loop=-1:size=2147483647,volume=0.2,afade=t=in:st=0:d=0.6,afade=t=out:st={TOTAL - 1.2:.2f}:d=1.2,atrim=0:{TOTAL:.2f}[mu];"
    fl += ''.join(f"[{a0 + 1 + i}:a]aresample=44100,{'volume=0.5,' if 'clic' in str(p) else ''}adelay={int(s * 1000)}|{int(s * 1000)}[p{i}];" for i, (p, s) in enumerate(pistas))
    fl += '[mu]' + ''.join(f'[p{i}]' for i in range(len(pistas))) + f'amix=inputs={len(pistas) + 1}:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]'
    nombres = {'P': 'Vicens_pergolas_v3', 'T': 'Vicens_techos_v2', 'Z': 'Vicens_zaguanes_v2', 'C': 'Vicens_zaguanes_cortinas_puertas_v1'}
    hd = tmp / 'hd.mp4'; sal = AQUI / f'{nombres[clave]}.mp4'
    ff(ent + ['-filter_complex', fl, '-map', f'[{cur}]', '-map', '[a]', '-t', f'{TOTAL:.2f}', '-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', str(hd)])
    ff(['-i', str(hd), '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-pix_fmt', 'yuv420p', '-crf', '24', '-preset', 'slow', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(sal)])
    print(sal, sal.stat().st_size // 1024, 'KB', f'{TOTAL:.1f}s')


if __name__ == '__main__':
    for c in (sys.argv[1:] or ['P', 'T', 'Z', 'C']):
        main(c)
