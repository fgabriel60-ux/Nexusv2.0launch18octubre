"""Fernando (Anegocios) v6: plan Glimmer 10/10/10 (gancho A «bola de nieve», frase REAL de Fernando de su nota de la nevería, oferta clara, CTA WhatsApp).
Todo con material real/pantallas y texto en capa (sin IA nueva). Voz clonada Fish (voz 5bec805f...), voz real recortada de su nota. Uso: python3 armar_fernando_v6.py"""
import json, subprocess, sys, urllib.request
from pathlib import Path
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/XV'); sys.path.insert(0, str(Path(__file__).resolve().parent))
import imageio_ffmpeg
from PIL import Image
from armar_fernando_v4 import TMP, dur, diapo, W, H, CL, MUSICA
from armar_fernando_v7 import tarjeta   # tarjeta con el WhatsApp correcto (55 4358 3070)
from armar_xv import tex

AQUI = Path(__file__).resolve().parent; FF = imageio_ffmpeg.get_ffmpeg_exe()
NOTA = CL / '1021_221426_ptt.ogg'; NOTA_INI, NOTA_DUR = 52.55, 5.0   # «si quiere lo podemos ver funcionando en este momento en la computadora»
VOZ = '6e856af2b690406691b0f8c2743659d1'
K = [l.split('=', 1)[1].strip().strip('"\'') for l in open('/workspaces/Nexusv2.0launch18octubre/.env') if l.startswith('FISH_API_KEY=')][0]
CADENA = 'highpass=f=80,equalizer=f=3000:t=q:w=1:g=2.5,acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=4,alimiter=limit=0.95'
SEG = {'G': '¿Una bola de nieve con más o menos gramos? Así se controla sin pelearse con la báscula.',
       'M': 'En Anegocios llevas inventario por gramos y por vasos, ventas al momento, cortes claros y varias cajas en una vista.',
       'K': 'Si ya tienes computadora, te llevamos software, impresora térmica, lector de códigos, instalación y capacitación personal en tu negocio.',
       'P': 'Primero lo tienes funcionando, después pagas. Tres mil quinientos pesos más impuestos por un año.',
       'C': 'Escríbeme por WhatsApp y lo vemos hoy.'}


def ff(a):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[:700])


def tts(k, t):
    p = AQUI / 'voz' / f'v6_{k}.mp3'
    if not p.exists():
        r = urllib.request.Request('https://api.fish.audio/v1/tts', method='POST', data=json.dumps({'text': t, 'format': 'mp3', 'reference_id': VOZ, 'prosody': {'speed': 1.1}}).encode(),
                                   headers={'Authorization': 'Bearer ' + K, 'Content-Type': 'application/json', 'model': 's2-pro'})
        p.write_bytes(urllib.request.urlopen(r, timeout=300).read())
    return p


def main():
    for k, t in SEG.items(): tts(k, t)
    D = {k: dur(AQUI / 'voz' / f'v6_{k}.mp3') for k in SEG}
    G = 0.2
    # orden del audio: G, NOTA (real), M, K, P, C
    orden = [('G', D['G']), ('N', NOTA_DUR), ('M', D['M']), ('K', D['K']), ('P', D['P']), ('C', D['C'])]
    ini, t = {}, 0.0
    for k, d in orden: ini[k] = t; t += d + G
    TOTAL = t + 2.2
    P = lambda n: Image.open(CL / n)
    yo = P('image_16_10-20_1845.jpg'); w, h = yo.size; yo_v = yo.crop((int(w * 0.25), 0, int(w * 0.25) + int(h * 0.75), h))
    sis = P('doc_06.png'); kit = P('doc_01.png'); inst = P('doc_02.png')
    SL = {'yo': yo_v, 'sis': sis, 'kit': kit, 'imp': P('image_03_10-20_1842.jpg'), 'lec': P('image_07_10-20_1842.jpg'), 'rol': P('image_09_10-20_1842.jpg'), 'ins': inst}
    for k, v in SL.items(): diapo(v, TMP / f'e_{k}.png', caja=(900, 1250) if k in ('yo', 'kit', 'ins') else (940, 1000))
    tarjeta(TMP / 'e_tarj.png')
    # (diapositiva, inicio, texto)
    kd = D['K']
    S = [('yo', 0, ['¿BOLA DE NIEVE CON', 'MÁS O MENOS GRAMOS?']),
         ('yo', ini['N'], ['«LO VEMOS FUNCIONANDO', 'EN ESTE MOMENTO»']),
         ('sis', ini['M'], ['INVENTARIO POR', 'GRAMOS Y POR VASOS']),
         ('imp', ini['K'], ['SOFTWARE + IMPRESORA', 'TÉRMICA']), ('lec', ini['K'] + kd * 0.33, ['LECTOR DE CÓDIGOS', '']),
         ('ins', ini['K'] + kd * 0.62, ['INSTALACIÓN Y CAPACITACIÓN', 'PERSONAL EN TU NEGOCIO']),
         ('kit', ini['P'], ['PRIMERO LO TIENES FUNCIONANDO', 'DESPUÉS PAGAS']), ('rol', ini['P'] + D['P'] * 0.5, ['$3,500 MXN + IMPUESTOS', '1 AÑO · SOFTWARE + KIT']),
         ('tarj', ini['C'], None)]
    S[4] = ('lec', S[4][1], ['LECTOR DE CÓDIGOS'])
    Xd = 0.2
    ends = [s[1] for s in S[1:]] + [TOTAL]
    ent, fl = [], ''
    for i, (n, a, _) in enumerate(S):
        L = ends[i] - a + (Xd if i < len(S) - 1 else 0)
        ent += ['-framerate', '30', '-loop', '1', '-t', f'{L + 0.1:.2f}', '-i', str(TMP / f'e_{n}.png')]
        fl += (f'[{i}:v]scale=1188:2112,zoompan=z=\'min(1.0+0.0008*on,1.07)\':x=\'(iw-iw/zoom)/2\':y=\'(ih-ih/zoom)/2\':d=1:s={W}x{H}:fps=30,'
               f'setsar=1,format=yuv420p,trim=duration={L:.2f},setpts=PTS-STARTPTS,fps=30,settb=1/30[s{i}];')
    cur = 's0'
    for i in range(1, len(S)):
        fl += f'[{cur}][s{i}]xfade=transition=slideleft:duration={Xd}:offset={S[i][1] - Xd:.2f}[x{i}];'; cur = f'x{i}'
    j0 = len(S); textos = [(s[2], s[1], ends[i]) for i, s in enumerate(S) if s[2]]
    for j, (lin, a, z) in enumerate(textos):
        lin = [x for x in lin if x]
        p = TMP / f'te{j}.png'; tex(lin, p, 1470, tam=64); ent += ['-loop', '1', '-t', f'{TOTAL:.1f}', '-i', str(p)]
        fl += f"[{cur}][{j0 + j}:v]overlay=0:0:enable='between(t,{a + 0.1:.2f},{z - 0.05:.2f})'[o{j}];"; cur = f'o{j}'
    a0 = j0 + len(textos)
    ent += ['-i', str(MUSICA), '-ss', str(NOTA_INI), '-t', str(NOTA_DUR), '-i', str(NOTA)] + [x for k in 'GMKPC' for x in ('-i', str(AQUI / 'voz' / f'v6_{k}.mp3'))]
    ms = lambda k: int(ini[k] * 1000)
    fl += f"[{a0}:a]aresample=48000,aloop=loop=-1:size=2147483647,aformat=channel_layouts=mono,volume=0.10,afade=t=in:st=0:d=0.6,afade=t=out:st={TOTAL - 1.2:.2f}:d=1.2,atrim=0:{TOTAL:.2f}[mu];"
    fl += f"[{a0 + 1}:a]aresample=48000,aformat=channel_layouts=mono,afade=t=in:d=0.05,afade=t=out:st={NOTA_DUR - 0.08}:d=0.08,adelay={ms('N')}|{ms('N')}[vN];"
    for q, k in enumerate('GMKPC'):
        fl += f"[{a0 + 2 + q}:a]aresample=48000,aformat=channel_layouts=mono,adelay={ms(k)}|{ms(k)}[v{k}];"
    fl += f"[vG][vN][vM][vK][vP][vC]amix=inputs=6:duration=longest:normalize=0,{CADENA}[vz];"
    fl += f'[vz][mu]amix=inputs=2:duration=longest:normalize=0,atrim=0:{TOTAL:.2f},loudnorm=I=-14:TP=-1.5[a]'
    hd = TMP / 'hd6.mp4'; sal = AQUI / 'Anegocios_Fernando_v6.mp4'
    ff(ent + ['-filter_complex', fl, '-map', f'[{cur}]', '-map', '[a]', '-t', f'{TOTAL:.2f}', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', str(hd)])
    ff(['-i', str(hd), '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-pix_fmt', 'yuv420p', '-crf', '24', '-preset', 'slow', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(sal)])
    print(sal, sal.stat().st_size // 1024, 'KB', f'{TOTAL:.1f}s', {k: round(v, 1) for k, v in D.items()})


if __name__ == '__main__':
    main()
