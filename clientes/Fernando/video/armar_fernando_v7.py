"""Fernando (Anegocios) v7 «4 pasos» (formato del reel de referencia DasdFyGlBeq): Fernando a cuadro con SU voz real (video del taller + su nota de la nevería), encabezado amarillo fijo por paso,
subtítulos blancos palabra por palabra y cortes a detalle (pantalla del sistema, lector, impresora, rollos) mientras habla la voz clonada de Fernando (Fish 6e856af2...). Sin IA de imagen.
WhatsApp del cierre: 55 4358 3070 (número de Fernando en sus chats; el 55 7645 6707 de v3/v4/v6 era de otro contacto). Uso: python3 armar_fernando_v7.py"""
import json, subprocess, sys, urllib.request
from pathlib import Path
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/XV'); sys.path.insert(0, str(Path(__file__).resolve().parent))
import imageio_ffmpeg, numpy as np, av
from PIL import Image, ImageDraw
from armar_fernando_v4 import TMP, dur, diapo, W, H, CL, MUSICA
from armar_xv import fu

AQUI = Path(__file__).resolve().parent; FF = imageio_ffmpeg.get_ffmpeg_exe()
VID = CL / '1021_014550_video.mp4'; NOTA = CL / '1021_221426_ptt.ogg'
VOZ = '6e856af2b690406691b0f8c2743659d1'
WHATSAPP = '55 4358 3070'
K = [l.split('=', 1)[1].strip().strip('"\'') for l in open('/workspaces/Nexusv2.0launch18octubre/.env') if l.startswith('FISH_API_KEY=')][0]
CADENA = 'highpass=f=80,equalizer=f=3000:t=q:w=1:g=2.5,acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=4,alimiter=limit=0.95'
AMARILLO = (255, 214, 10)
CLON = {'1': 'Uno: registra cada venta al momento, con tu lector de códigos.',
        '2': 'Dos: inventario por piezas, gramos o vasos.',
        '3': 'Tres: corte de caja claro, con tu ticket en la impresora térmica.',
        '4': 'Te lo instalamos y te capacitamos en tu negocio. Primero lo tienes funcionando, después pagas. Tres mil quinientos pesos más impuestos, por un año.',
        'C': 'Escríbeme por WhatsApp y lo vemos hoy.'}
HOOK = ['LOS 4 PASOS PARA CONTROLAR', 'TU NEGOCIO SIN LIBRETA']
# (tipo, fuente, inicio, fin, encabezado, visuales[(fracción, slide)])  — real: voz y cara de Fernando; nota: su voz sobre detalle; clon: voz clonada sobre detalle
CHUNKS = [('real', VID, 0.80, 7.35, HOOK, [(0, 'vid')]),
          ('clon', '1', 0, 0, ['1# REGISTRA CADA VENTA', 'AL MOMENTO'], [(0, 'sis'), (0.5, 'lec')]),
          ('clon', '2', 0, 0, ['2# INVENTARIO POR PIEZAS,', 'GRAMOS O VASOS'], [(0, 'sis')]),
          ('real', NOTA, 45.98, 50.50, ['2# INVENTARIO POR PIEZAS,', 'GRAMOS O VASOS'], [(0, 'sis')]),
          ('clon', '3', 0, 0, ['3# CORTE DE CAJA CLARO'], [(0, 'imp'), (0.55, 'rol')]),
          ('real', VID, 30.40, 37.65, ['4# TE LO INSTALAMOS', 'Y TE CAPACITAMOS'], [(0, 'vid')]),
          ('clon', '4', 0, 0, ['4# TE LO INSTALAMOS', 'Y TE CAPACITAMOS'], [(0, 'ins'), (0.45, 'kit'), (0.7, 'precio')]),
          ('clon', 'C', 0, 0, None, [(0, 'tarj')])]


def ff(a):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[:700])


def tts(k):
    p = AQUI / 'voz' / f'v7_{k}.mp3'
    if not p.exists():
        r = urllib.request.Request('https://api.fish.audio/v1/tts', method='POST', data=json.dumps({'text': CLON[k], 'format': 'mp3', 'reference_id': VOZ, 'prosody': {'speed': 1.1}}).encode(),
                                   headers={'Authorization': 'Bearer ' + K, 'Content-Type': 'application/json', 'model': 's2-pro'})
        p.write_bytes(urllib.request.urlopen(r, timeout=300).read())
    return p


_WM = None
def palabras(path, ss=0.0, t=None):
    """[(palabra, ini, fin)] relativos al recorte, con faster-whisper."""
    global _WM
    from faster_whisper import WhisperModel
    _WM = _WM or WhisperModel('small', device='cpu', compute_type='int8')
    c = av.open(str(path)); rs = av.AudioResampler(format='s16', layout='mono', rate=16000)
    x = np.concatenate([a.to_ndarray().ravel() for f in c.decode(audio=0) for a in rs.resample(f)]).astype(np.float32) / 32768
    segs, _ = _WM.transcribe(x, language='es', word_timestamps=True)
    return [(w.word.strip(), float(w.start) - ss, float(w.end) - ss) for s in segs for w in s.words if ss - 0.05 <= w.start < (ss + t if t else 1e9)]


def tarjeta(ruta):
    img = Image.new('RGB', (W, H), (12, 30, 60)); d = ImageDraw.Draw(img)
    def c(t, y, tam, col, peso='Black'):
        f = fu(tam, peso)
        while d.textlength(t, font=f) > W - 110: tam -= 2; f = fu(tam, peso)
        d.text(((W - d.textlength(t, font=f)) / 2, y), t, font=f, fill=col)
    c('ANEGOCIOS', 560, 130, (255, 255, 255)); c('PUNTO DE VENTA PARA TU NEGOCIO · CDMX', 720, 44, AMARILLO, 'Bold')
    t = 'ESCRÍBEME POR WHATSAPP'; f = fu(50, 'ExtraBold'); an = d.textlength(t, font=f) + 110
    d.rounded_rectangle(((W - an) / 2, 860, (W + an) / 2, 990), 65, fill=(37, 211, 102)); d.text(((W - an) / 2 + 55, 895), t, font=f, fill=(255, 255, 255))
    c(WHATSAPP, 1060, 96, AMARILLO)
    c('$3,500 MXN + IMPUESTOS · 1 AÑO', 1220, 46, (255, 255, 255), 'Bold')
    img.save(ruta)


def texto_png(lineas, ruta, y, tam, col, trazo=8, alto=330):
    """capa transparente 1080 x alto, líneas centradas con contorno negro."""
    im = Image.new('RGBA', (W, alto), (0, 0, 0, 0)); d = ImageDraw.Draw(im); yy = 10
    for l in lineas:
        t = tam; f = fu(t, 'Black')
        while d.textlength(l, font=f) > W - 90: t -= 2; f = fu(t, 'Black')
        d.text(((W - d.textlength(l, font=f)) / 2, yy), l, font=f, fill=col, stroke_width=trazo, stroke_fill=(0, 0, 0)); yy += int(t * 1.25)
    im.save(ruta)


def main():
    for k in CLON: tts(k)
    # duraciones y palabras por chunk
    info = []
    for tipo, src, a, b, hdr, vis in CHUNKS:
        if tipo == 'clon':
            p = AQUI / 'voz' / f'v7_{src}.mp3'; d = dur(p) + 0.12; pal = palabras(p)
        else:
            d = b - a + 0.0; pal = palabras(src, a, b - a)
        info.append((d, pal))
    # línea de tiempo
    t0, T = [], 0.0
    for d, _ in info: t0.append(T); T += d
    TOTAL = T + 1.8
    P = lambda n: Image.open(CL / n)
    yo = P('doc_06.png')
    SL = {'sis': P('doc_06.png'), 'lec': P('image_07_10-20_1842.jpg'), 'imp': P('image_03_10-20_1842.jpg'), 'rol': P('image_09_10-20_1842.jpg'),
          'ins': P('doc_02.png'), 'kit': P('doc_01.png'), 'precio': P('image_09_10-20_1842.jpg')}
    for k, v in SL.items(): diapo(v, TMP / f'g_{k}.png', caja=(900, 1150) if k in ('ins', 'kit') else (940, 1000))
    tarjeta(TMP / 'g_tarj.png')
    # visuales: lista (nombre, ini, fin, video(ss) | None)
    VIS = []
    for i, (tipo, src, a, b, hdr, vis) in enumerate(CHUNKS):
        d = info[i][0]; ends = [v[0] for v in vis[1:]] + [1.0]
        for (fr, n), fe in zip(vis, ends):
            VIS.append((n, t0[i] + fr * d, t0[i] + fe * d, a if n == 'vid' else None, (fr * d if n == 'vid' else 0)))
    ent, fl, vs = [], '', []
    for j, (n, a, z, ss, off) in enumerate(VIS):
        L = z - a
        if n == 'vid':
            ent += ['-ss', f'{ss + off:.2f}', '-t', f'{L:.2f}', '-i', str(VID)]
            fl += f'[{j}:v]scale={W}:{H}:flags=lanczos,unsharp=5:5:0.7,eq=contrast=1.04:saturation=1.05,fps=30,setsar=1,format=yuv420p,trim=duration={L:.3f},setpts=PTS-STARTPTS[v{j}];'
        else:
            ent += ['-framerate', '30', '-loop', '1', '-t', f'{L + 0.1:.2f}', '-i', str(TMP / f'g_{n}.png')]
            fl += (f'[{j}:v]scale=1188:2112,zoompan=z=\'min(1.0+0.0007*on,1.06)\':x=\'(iw-iw/zoom)/2\':y=\'(ih-ih/zoom)/2\':d=1:s={W}x{H}:fps=30,setsar=1,format=yuv420p,'
                   f'trim=duration={L:.3f},setpts=PTS-STARTPTS,fps=30[v{j}];')
        vs.append(f'[v{j}]')
    fl += ''.join(vs) + f'concat=n={len(vs)}:v=1:a=0[base];'
    # encabezados (fijos) y subtítulos palabra por palabra
    caps = []   # (png, y, ini, fin)
    for i, (tipo, src, a, b, hdr, vis) in enumerate(CHUNKS):
        if hdr:
            p = TMP / f'h{i}.png'; texto_png(hdr, p, 0, 70 if len(hdr) > 1 and i else 66, AMARILLO, alto=320); caps.append((p, 120, t0[i], t0[i] + info[i][0]))
        pal = info[i][1]; fin_chunk = t0[i] + info[i][0]
        for q, (w, s, e) in enumerate(pal):
            ini = t0[i] + max(0, s)
            fin = t0[i] + max(0, pal[q + 1][1]) if q + 1 < len(pal) else fin_chunk
            fin = min(max(fin, ini + 0.12), ini + 0.7, fin_chunk)
            p = TMP / f'w{i}_{q}.png'; texto_png([w], p, 0, 118, (255, 255, 255), trazo=9, alto=190); caps.append((p, 1380, ini, fin))
    cur, b0 = 'base', len(VIS)
    for j, (p, y, a, z) in enumerate(caps):
        ent += ['-loop', '1', '-t', f'{TOTAL:.1f}', '-i', str(p)]
        fl += f"[{cur}][{b0 + j}:v]overlay=0:{y}:enable='between(t,{a:.2f},{z:.2f})'[o{j}];"; cur = f'o{j}'
    # audio: cada chunk recortado y rellenado a su duración
    a0 = b0 + len(caps); aud = []
    for i, (tipo, src, a, b, hdr, vis) in enumerate(CHUNKS):
        d = info[i][0]
        if tipo == 'clon': ent += ['-i', str(AQUI / 'voz' / f'v7_{src}.mp3')]
        else: ent += ['-ss', f'{a:.2f}', '-t', f'{d:.2f}', '-i', str(src)]
        fl += f'[{a0 + i}:a]aresample=48000,aformat=channel_layouts=mono,afade=t=in:d=0.03,afade=t=out:st={max(d - 0.1, 0):.2f}:d=0.08,apad=whole_dur={d:.3f},atrim=0:{d:.3f}[c{i}];'
        aud.append(f'[c{i}]')
    ent += ['-i', str(MUSICA)]
    fl += ''.join(aud) + f'concat=n={len(aud)}:v=0:a=1,{CADENA},apad=whole_dur={TOTAL:.2f}[vz];'
    fl += f'[{a0 + len(CHUNKS)}:a]aresample=48000,aloop=loop=-1:size=2147483647,aformat=channel_layouts=mono,volume=0.09,afade=t=in:st=0:d=0.6,afade=t=out:st={TOTAL - 1.2:.2f}:d=1.2,atrim=0:{TOTAL:.2f}[mu];'
    fl += f'[vz][mu]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]'
    hd = TMP / 'hd7.mp4'; sal = AQUI / 'Anegocios_Fernando_v7_capacitacion_pasos.mp4'
    ff(ent + ['-filter_complex', fl, '-map', f'[{cur}]', '-map', '[a]', '-t', f'{TOTAL:.2f}', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', str(hd)])
    ff(['-i', str(hd), '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-pix_fmt', 'yuv420p', '-crf', '24', '-preset', 'slow', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(sal)])
    print(sal, sal.stat().st_size // 1024, 'KB', f'{TOTAL:.1f}s', [round(d, 1) for d, _ in info])


if __name__ == '__main__':
    main()
