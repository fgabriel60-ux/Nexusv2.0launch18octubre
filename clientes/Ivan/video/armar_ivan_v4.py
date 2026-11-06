"""Fumicam (Iván) v4 = método del reel de Planet Plus (oferta + confianza + calidad): gancho «vamos al detalle», ACERCAMIENTOS de aplicación donde anidan
(gel en grietas y fregadero, aspersión en recámara y jardín, termitas de madera seca y subterráneas, generados en Modal desde fotos reales de sus técnicos),
técnicos reales en planos abiertos, SU voz clonada (Fish) y cotiza sin compromiso. La garantía queda pendiente de confirmar con Iván.
Antes: v3 al estilo de las referencias de Instagram que le gustaron (técnico real + niebla, cortes rápidos, título grande, subtítulos palabra por palabra).
Mismas 6 tomas reales animadas (tomas/*.mp4) y la misma voz de vendedor; cortes de 1.6 s con golpe de zoom, título de entrada en dos colores,
subtítulo con la palabra actual en amarillo, ✓ verde en «trabajo real» y tarjeta de WhatsApp al final.
Uso: python3 armar_ivan_v3.py"""
import json, subprocess, sys
from pathlib import Path
import av, imageio_ffmpeg, numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/XV')
from armar_xv import fu
from armar_ivan import tarjeta

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
TMP = Path('/tmp/claude-1000/-workspaces-Nexusv2-0launch18octubre/d5ed233e-f882-4c9b-a96a-df1463a68d1a/scratchpad/ivan4'); TMP.mkdir(parents=True, exist_ok=True)
W, H, FPS = 1080, 1920, 30
RET = 0.3                                        # la voz entra a los 0.3 s
VOZ = AQUI / 'v4' / 'voz_ivan.mp3'          # su voz clonada (Fish 2e7509fa…, de sus 2 notas de voz)


def palabras():
    j = AQUI / 'v4' / 'voz_palabras.json'
    if not j.exists():
        from faster_whisper import WhisperModel
        a = np.frombuffer(subprocess.run([FF, '-loglevel', 'error', '-i', str(VOZ), '-f', 's16le', '-ac', '1', '-ar', '16000', '-'], capture_output=True).stdout, np.int16).astype(np.float32) / 32768
        segs, _ = WhisperModel('small', device='cpu', compute_type='int8').transcribe(a, language='es', word_timestamps=True)
        j.write_text(json.dumps([(w.word.strip(), w.start, w.end) for s in segs for w in s.words], ensure_ascii=False))
    arreglo = {'enzimita,': 'encimita:', 'cuernabaca': 'Cuernavaca', 'cotizas': 'cotiza'}
    return [(arreglo.get(w.lower(), w), s + RET, e + RET) for w, s, e in json.loads(j.read_text())]


PAL = palabras()
TOTAL = PAL[-1][2] + 0.9
T_TARJ = next(s for w, s, e in PAL if w.lower().startswith('escr'))      # la tarjeta entra en «Escríbenos por WhatsApp…»
# cada tramo arranca cuando la voz dice su palabra ancla; sus tomas se reparten el tramo. ('v', clip) = acercamiento generado · ('r', toma real)
TRAMOS = [('aquí', [('r', 'I4_oficina', 0.3), ('r', 'I1_cuarto', 0.4)]),
          ('grieta', [('v', 'V1', 0.3)]), ('fregadero', [('v', 'V2', 0.3)]), ('rincón', [('v', 'V3', 0.3), ('r', 'I3_sala', 0.3)]),
          ('alacranes', [('v', 'V4', 0.3), ('r', 'I5_jardin', 0.4)]),
          ('termitas', [('v', 'V5', 0.3)]), ('subterránea', [('v', 'V6', 0.3)]),
          ('técnicos', [('r', 'I2_patio', 0.5), ('r', 'I6_pasillo', 0.5), ('r', 'I4_oficina', 2.6)]),
          ('escríbenos', [('r', 'I1_cuarto', 2.8)])]


def cortes():
    out = []
    ini = [next(s for w, s, e in PAL if w.lower().strip('¿¡,.:').startswith(a)) if k else 0.0 for k, (a, _) in enumerate(TRAMOS)]
    ini.append(TOTAL)
    for k, (_, tomas) in enumerate(TRAMOS):
        d = (ini[k + 1] - ini[k]) / len(tomas)
        for j, (tipo, n, i0) in enumerate(tomas): out.append((ini[k] + j * d, d, tipo, n, i0))
    return out


CORTES = cortes()
ROJO, AMARILLO, VERDE = (235, 40, 40), (255, 222, 0), (37, 211, 102)


def frames(n):
    c = av.open(str(AQUI / ('v4/clips' if n.startswith('V') else 'tomas') / f'{n}.mp4'))
    return [f.to_image().convert('RGB').resize((W, H), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.6, 70, 2)) for f in c.decode(video=0)]


def texto(d, t, y, tam, col, peso='Black', borde=10):
    f = fu(tam, peso)
    while d.textlength(t, font=f) > W - 80: tam -= 3; f = fu(tam, peso)
    d.text(((W - d.textlength(t, font=f)) / 2, y), t, font=f, fill=col, stroke_width=borde, stroke_fill=(0, 0, 0))
    return tam


def titulo(t):
    """Gancho tipo «VAPOR / CLAVE PARA EL CONTROL DE CHINCHES»: entra con rebote y se va a los 2.6 s."""
    if t > 2.7: return None
    k = min(1, t / 0.25); esc = 0.7 + 0.3 * k + 0.08 * np.sin(k * np.pi)
    capa = Image.new('RGBA', (W, 520), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    texto(d, 'FUMIGACIÓN', 20, 170, (255, 255, 255))
    texto(d, 'AL DETALLE', 215, 110, AMARILLO, 'Black', 9)
    texto(d, 'CUCARACHAS · ALACRANES · TERMITAS', 350, 70, (255, 255, 255), 'ExtraBold', 8)
    capa = capa.resize((int(W * esc), int(520 * esc)), Image.LANCZOS)
    if t > 2.4: capa.putalpha(capa.getchannel('A').point(lambda v: int(v * (2.7 - t) / 0.3)))
    return capa


def subtitulo(t):
    """3 palabras a la vez; la que se está diciendo va en amarillo y un poco más grande (como la ref. de chiripas)."""
    i = next((k for k, (_, s, e) in enumerate(PAL) if s - 0.05 <= t < (PAL[k + 1][1] if k + 1 < len(PAL) else e + 0.4)), None)
    if i is None or t >= T_TARJ: return None
    g0 = (i // 3) * 3; grupo = PAL[g0:g0 + 3]
    capa = Image.new('RGBA', (W, 260), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    tam, esp = 84, 26
    while True:
        f = fu(tam, 'Black'); fa = fu(int(tam * 1.16), 'Black')
        anchos = [d.textlength(w, font=(fa if g0 + j == i else f)) for j, (w, _, _) in enumerate(grupo)]
        total = sum(anchos) + esp * (len(grupo) - 1)
        if total <= W - 70 or tam <= 40: break
        tam -= 4
    x = (W - total) / 2
    for j, (w, _, _) in enumerate(grupo):
        act = g0 + j == i
        d.text((x, 60 if act else 72), w, font=fa if act else f, fill=AMARILLO if act else (255, 255, 255), stroke_width=9, stroke_fill=(0, 0, 0))
        x += anchos[j] + esp
    return capa


def palomita(t, t0=None):
    t0 = t0 if t0 is not None else next(s for w, s, e in PAL if w.lower().startswith('reales'))
    if not (t0 <= t < t0 + 1.6): return None
    k = min(1, (t - t0) / 0.2); r = int(90 * (0.6 + 0.4 * k + 0.1 * np.sin(k * np.pi)))
    capa = Image.new('RGBA', (2 * r + 20, 2 * r + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    d.ellipse((10, 10, 10 + 2 * r, 10 + 2 * r), fill=VERDE, outline=(255, 255, 255), width=8)
    d.line([(10 + r * .55, 10 + r * 1.05), (10 + r * .9, 10 + r * 1.4), (10 + r * 1.5, 10 + r * .7)], fill=(255, 255, 255), width=max(8, r // 5), joint='curve')
    return capa


def main():
    tarjeta(TMP / 'tarjeta.png'); tj = Image.open(TMP / 'tarjeta.png').convert('RGBA')
    cache = {}
    mudo = TMP / 'mudo.mp4'
    p = subprocess.Popen([FF, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', str(mudo)], stdin=subprocess.PIPE)
    for k in range(int(TOTAL * FPS)):
        t = k / FPS; t0, D, _, n, ini = next(x for x in reversed(CORTES) if x[0] <= t + 1e-6)
        if n not in cache: cache.clear(); cache[n] = frames(n)     # solo el clip actual en memoria
        fr = cache[n]; tl = t - t0
        base = fr[min(len(fr) - 1, int((ini + tl) * 24))]
        z = 1.0 + 0.10 * max(0, 1 - tl / 0.35) + 0.03 * tl / D          # golpe de zoom al entrar + empuje lento
        cw, ch = int(W / z), int(H / z)
        base = base.crop(((W - cw) // 2, (H - ch) // 2, (W + cw) // 2, (H + ch) // 2)).resize((W, H), Image.BICUBIC).convert('RGBA')
        if tl < 0.08: base = Image.blend(base, Image.new('RGBA', (W, H), (255, 255, 255, 255)), 0.35 * (1 - tl / 0.08))   # destello en el corte
        tit = titulo(t)
        if tit: base.alpha_composite(tit, ((W - tit.width) // 2, 300 + (520 - tit.height) // 2))
        s = subtitulo(t)
        if s and t > 2.5: base.alpha_composite(s, (0, 1300))
        pm = palomita(t)
        if pm: base.alpha_composite(pm, (W - pm.width - 60, 260))
        if t >= T_TARJ:
            a = min(1, (t - T_TARJ) / 0.35); x = tj.copy(); x.putalpha(x.getchannel('A').point(lambda v: int(v * a))); base.alpha_composite(x)
        p.stdin.write(np.asarray(base.convert('RGB')).tobytes())
    p.stdin.close(); p.wait()
    musica = AQUI.parents[1] / 'XV' / 'musica_suave_s7.wav'
    sal = AQUI / 'Fumicam_Ivan_v4_al_detalle.mp4'
    fl = (f"[1:a]aresample=44100,highpass=f=90,afftdn=nr=8:nf=-40,equalizer=f=3000:t=q:w=1:g=2.5,acompressor=threshold=-20dB:ratio=3:makeup=3,"
          f"adelay={int(RET * 1000)}|{int(RET * 1000)}[v];[2:a]aresample=44100,volume=0.28,afade=t=out:st={TOTAL - 1.2:.2f}:d=1.2[m];"
          f"[v][m]amix=inputs=2:duration=longest:normalize=0,atrim=0:{TOTAL:.2f},loudnorm=I=-14:TP=-1.5[a]")
    r = subprocess.run([FF, '-v', 'error', '-y', '-i', str(mudo), '-i', str(VOZ), '-i', str(musica), '-filter_complex', fl,
                        '-map', '0:v', '-map', '[a]', '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1',
                        '-pix_fmt', 'yuv420p', '-crf', '22', '-preset', 'slow', '-c:a', 'aac', '-b:a', '160k', '-t', f'{TOTAL:.2f}', '-movflags', '+faststart', str(sal)],
                       capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1500:])
    print(sal, sal.stat().st_size // 1024, 'KB', f'{TOTAL:.1f}s')


if __name__ == '__main__':
    main()
