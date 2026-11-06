"""José · Grupo JR · 3 anuncios de RETARGETING (para quien ya vio «Puede llover»). Reutiliza los clips J1..J4 (sin Modal) + voz nueva de José (Fish) +
subtítulos palabra por palabra + tarjeta final distinta por anuncio.   Uso: python3 armar_retargeting.py [1|2|3 ...]"""
import json, subprocess, sys, urllib.request
from pathlib import Path
import av, imageio_ffmpeg, numpy as np
from faster_whisper import WhisperModel
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
FUENTE = str(AQUI.parent / 'modelos_modal' / 'fuentes' / 'Montserrat.ttf')
W, H = 1080, 1920
AZUL, AMARILLO, VERDE_WA = (12, 38, 104), (255, 214, 60), (37, 211, 102)
KEY = [l.split('=', 1)[1].strip().strip('"\'') for l in open('/workspaces/Nexusv2.0launch18octubre/.env') if l.startswith('FISH_API_KEY=')][0]
VOZ_ID = '74cae190c2c84b0caaca073f42f5de54'      # José / Grupo JR (voz clonada en Fish)
TMP = AQUI / 'tmp_retarget'; TMP.mkdir(exist_ok=True); (AQUI / 'voz_retarget').mkdir(exist_ok=True)
D_TARJETA = 3.4

# clips en orden de aparición, voz, y tarjeta final (título, subtítulo, viñetas)
ANUNCIOS = {
    1: dict(nombre='A1_durabilidad', clips=['J3', 'J1', 'J2'], letreros=[['CÓMO QUEDA DESPUÉS', 'DE UNA TORMENTA'], ['PROTEGE LA ESTRUCTURA', 'DE TU CASA EN PUEBLA'], ['SISTEMA INDUSTRIAL', 'SELLADOR + 2 CAPAS']],
            voz='Doce años es mucho tiempo. Nuestro sistema industrial no solo impermeabiliza, protege la estructura de tu casa en Puebla. Mira cómo queda después de una tormenta. Escríbeme por WhatsApp.',
            tarjeta=('12 AÑOS', 'DE PROTECCIÓN', [('Sistema industrial', 'Poliuretano acrílico afibratado'), ('Sellador + 2 manos', 'Blanco que rebota el sol'), ('Protege tu estructura', 'Casas en Puebla y alrededores')])),
    2: dict(nombre='A2_ahorro', clips=['J2', 'GRAFICO', 'J3'], letreros=[['MÁS DE 100 m²', '10 % DE DESCUENTO'], None, ['CALIDAD INDUSTRIAL', 'DESDE $150 POR m²']],
            voz='¿Tienes más de cien metros cuadrados? Aprovecha el diez por ciento de descuento. Calidad industrial desde ciento cincuenta pesos el metro. Lo barato sale caro cuando vuelve a llover. Escríbeme por WhatsApp.',
            tarjeta=('10 % DE', 'DESCUENTO', [('Más de 100 m²', 'Descuento inmediato'), ('Desde $150 por m²', 'Calidad industrial'), ('Lo barato sale caro', 'cuando vuelve a llover')])),
    3: dict(nombre='A3_urgencia', clips=['J1', 'J4', 'J3'], letreros=[['NO ESPERES', 'A LA PRIMERA GOTERA'], ['PROTEGE TU PATRIMONIO', 'HOY'], ['OLVÍDATE DEL PROBLEMA', 'POR UNA DÉCADA']],
            voz='No esperes a que aparezca la primera gotera. Protege tu patrimonio hoy y olvídate del problema por una década. Escríbeme por WhatsApp.',
            tarjeta=('PROTEGE', 'TU PATRIMONIO HOY', [('Antes de la gotera', 'Actúa antes de que llueva'), ('12 años de vida útil', 'Poliuretano acrílico afibratado'), ('Desde $150 por m²', '10 % de descuento en más de 100 m²')])),
}


def ff(a):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1500:])


def fu(t, peso='Black'):
    f = ImageFont.truetype(FUENTE, t); f.set_variation_by_name(peso); return f


def dur(ruta):
    e = subprocess.run([FF, '-i', str(ruta)], capture_output=True, text=True).stderr
    h, m, s = e.split('Duration: ')[1].split(',')[0].split(':'); return int(h) * 3600 + int(m) * 60 + float(s)


def tts(texto, ruta):
    if ruta.exists(): return
    r = urllib.request.Request('https://api.fish.audio/v1/tts', method='POST', data=json.dumps({'text': texto, 'format': 'mp3', 'reference_id': VOZ_ID, 'prosody': {'speed': 1.0}}).encode(),
                               headers={'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json', 'model': 's2-pro'})
    ruta.write_bytes(urllib.request.urlopen(r, timeout=300).read())


_WH = None
def palabras(ruta):
    global _WH
    _WH = _WH or WhisperModel('small', device='cpu', compute_type='int8')
    c = av.open(str(ruta)); rs = av.AudioResampler(format='s16', layout='mono', rate=16000)
    a = np.concatenate([x.to_ndarray().ravel() for fr in c.decode(audio=0) for x in rs.resample(fr)]).astype(np.float32) / 32768
    segs, _ = _WH.transcribe(a, language='es', word_timestamps=True)
    out, ult = [], -1.0
    for s in segs:
        for w in s.words:
            ini = max(w.start + 0.3, ult + 0.08); out.append((w.word.strip(), ini, w.end + 0.3)); ult = ini
    return out


def sub(txt, ruta):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img); tam = 90
    while d.textlength(txt, font=fu(tam)) > W - 80: tam -= 4
    f = fu(tam); d.text(((W - d.textlength(txt, font=f)) / 2, 1230), txt, font=f, fill=(255, 255, 255), stroke_width=8, stroke_fill=(10, 20, 50)); img.save(ruta)


def letrero(lineas, ruta, y=1470, tam=50):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    for yy in range(y - 90, H): d.line([(0, yy), (W, yy)], fill=(4, 12, 30, int(170 * min(1, (yy - y + 90) / 200))))
    d.rectangle((70, y, 76, y + len(lineas) * (tam + 6) + 8), fill=AMARILLO)
    for i, l in enumerate(lineas):
        f = fu(tam if i == 0 else int(tam * .72), 'Bold' if i == 0 else 'Medium')
        while d.textlength(l, font=f) > W - 190: f = fu(f.size - 2, 'Bold' if i == 0 else 'Medium')
        d.text((105, y + i * (tam + 8)), l, font=f, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))
    img.save(ruta)


def centrado(d, t, y, tam, col, peso='Black'):
    f = fu(tam, peso)
    while d.textlength(t, font=f) > W - 100: tam -= 2; f = fu(tam, peso)
    d.text(((W - d.textlength(t, font=f)) / 2, y), t, font=f, fill=col)


def tarjeta(datos, ruta):
    t1, t2, items = datos
    img = Image.new('RGB', (W, H), AZUL); d = ImageDraw.Draw(img)
    logo = Image.open(AQUI / 'refs' / 'logo_jr.png').convert('RGB').resize((250, 250), Image.LANCZOS); img.paste(logo, ((W - 250) // 2, 130))
    centrado(d, t1, 470, 150, AMARILLO); centrado(d, t2, 650, 70, (255, 255, 255))
    for i, (a, b) in enumerate(items):
        y = 880 + i * 120; d.rounded_rectangle((90, y, W - 90, y + 104), 20, fill=(255, 255, 255))
        d.text((125, y + 10), a, font=fu(40, 'ExtraBold'), fill=(12, 30, 80)); d.text((125, y + 62), b, font=fu(28, 'Medium'), fill=(70, 80, 110))
    t = 'Escríbeme por WhatsApp'; f = fu(48, 'ExtraBold'); a = d.textlength(t, font=f) + 110
    d.rounded_rectangle(((W - a) / 2, 1360, (W + a) / 2, 1476), 58, fill=VERDE_WA); d.text(((W - a) / 2 + 55, 1388), t, font=f, fill=(255, 255, 255))
    centrado(d, 'Puebla y alrededores', 1540, 38, (200, 215, 255), 'Medium'); img.save(ruta)


def grafico(ruta):
    """Comparativo sencillo (cualitativo, sin cifras inventadas del otro producto)."""
    img = Image.new('RGB', (W, H), AZUL); d = ImageDraw.Draw(img)
    centrado(d, '¿CUÁL SALE MÁS CARO?', 130, 80, (255, 255, 255)); centrado(d, 'Lo barato sale caro cuando vuelve a llover', 250, 38, (200, 215, 255), 'Medium')
    for x0, x1, tit, col, tc, filas, ok in [(60, 520, 'COMÚN', (232, 236, 246), (60, 70, 100), ['Barato hoy', 'Se vuelve a aplicar', 'La gotera regresa'], False),
                                            (560, 1020, 'POLIURETANO JR', AMARILLO, (12, 30, 80), ['12 años de vida útil', 'Sellador + 2 capas', 'Calidad industrial'], True)]:
        d.rounded_rectangle((x0, 380, x1, 1090), 30, fill=col); f = fu(46, 'Black')
        while d.textlength(tit, font=f) > x1 - x0 - 40: f = fu(f.size - 2, 'Black')
        d.text(((x0 + x1) / 2 - d.textlength(tit, font=f) / 2, 420), tit, font=f, fill=tc)
        for i, fila in enumerate(filas):
            y = 560 + i * 170; d.ellipse((x0 + 30, y, x0 + 100, y + 70), fill=(40, 170, 90) if ok else (200, 60, 60))
            if ok: d.line([(x0 + 48, y + 36), (x0 + 62, y + 50), (x0 + 84, y + 20)], fill=(255, 255, 255), width=8)
            else:
                d.line([(x0 + 50, y + 22), (x0 + 80, y + 50)], fill=(255, 255, 255), width=8); d.line([(x0 + 80, y + 22), (x0 + 50, y + 50)], fill=(255, 255, 255), width=8)
            f2 = fu(34, 'ExtraBold')
            while d.textlength(fila, font=f2) > x1 - x0 - 150: f2 = fu(f2.size - 2, 'ExtraBold')
            d.text((x0 + 118, y + 14), fila, font=f2, fill=tc)
    centrado(d, 'Desde $150 por m²', 1120, 60, AMARILLO); img.save(ruta)


def armar(n):
    a = ANUNCIOS[n]; nombre = a['nombre']
    voz = AQUI / 'voz_retarget' / f'{nombre}.mp3'; tts(a['voz'], voz)
    dv = dur(voz); lista = palabras(voz)
    visual = dv + 0.4 + D_TARJETA - 1.0                  # la tarjeta arranca ~1 s antes de que termine la voz (junto a «Escríbeme por WhatsApp»)
    t_tar = visual - D_TARJETA; dc = (t_tar + 0.4) / len(a['clips'])
    segs = []
    for k, c in enumerate(a['clips']):
        s = TMP / f'{nombre}_{k}.mp4'
        if c == 'GRAFICO':
            g = TMP / 'grafico.png'; grafico(g); ff(['-loop', '1', '-i', str(g), '-t', f'{dc:.2f}', '-vf', f'scale={W}:{H},fps=30,format=yuv420p', '-an', '-c:v', 'libx264', '-crf', '17', str(s)])
        else:
            real = dur(AQUI / 'clips' / f'{c}.mp4')
            ff(['-i', str(AQUI / 'clips' / f'{c}.mp4'), '-vf', f'setpts=PTS*{dc / real:.4f},scale={W}:{H}:flags=lanczos,setsar=1,fps=30,format=yuv420p', '-t', f'{dc:.2f}', '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '17', str(s)])
        segs.append(s)
    (TMP / f'{nombre}_lista.txt').write_text(''.join(f"file '{s}'\n" for s in segs))
    tarjeta(a['tarjeta'], TMP / f'{nombre}_tarjeta.png')
    entr = ['-f', 'concat', '-safe', '0', '-i', str(TMP / f'{nombre}_lista.txt'), '-i', str(voz), '-loop', '1', '-t', f'{D_TARJETA + 0.5}', '-i', str(TMP / f'{nombre}_tarjeta.png')]
    fl, prev, idx = '', '0:v', 3
    for k, l in enumerate(a['letreros']):
        if not l: continue
        letrero(l, TMP / f'{nombre}_l{k}.png'); entr += ['-i', str(TMP / f'{nombre}_l{k}.png')]
        fl += f"[{prev}][{idx}:v]overlay=0:0:enable='between(t,{k * dc + .3:.2f},{(k + 1) * dc - .2:.2f})'[c{k}];"; prev = f'c{k}'; idx += 1
    for i, (p, ini, fin) in enumerate(lista):
        if ini > t_tar: break
        sub(p, TMP / f'{nombre}_p{i}.png'); entr += ['-i', str(TMP / f'{nombre}_p{i}.png')]
        sig = min(max(lista[i + 1][1] if i + 1 < len(lista) else fin + .3, ini + .15), t_tar)
        fl += f"[{prev}][{idx}:v]overlay=0:0:enable='gte(t,{ini:.3f})*lt(t,{sig:.3f})'[s{i}];"; prev = f's{i}'; idx += 1
    fl += (f"[{prev}]format=yuv420p,settb=1/30,fps=30[vh];[2:v]scale={W}:{H},setsar=1,fps=30,format=yuv420p,settb=1/30[vt];"
           f"[vh][vt]xfade=transition=fade:duration=0.4:offset={t_tar:.2f}[v];[1:a]adelay=300|300,loudnorm=I=-15:TP=-1.5,apad[a]")
    hd = TMP / f'{nombre}_hd.mp4'; sal = AQUI / 'final' / f'Jose_JR_retargeting_{nombre}.mp4'
    ff(entr + ['-filter_complex', fl, '-map', '[v]', '-map', '[a]', '-t', f'{t_tar + D_TARJETA + 0.4:.2f}', '-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', str(hd)])
    ff(['-i', str(hd), '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-pix_fmt', 'yuv420p', '-crf', '22', '-c:a', 'copy', '-movflags', '+faststart', str(sal)])
    print(sal, sal.stat().st_size // 1024, 'KB', round(dur(sal), 1), 's', flush=True)


if __name__ == '__main__':
    for n in ([int(x) for x in sys.argv[1:]] or [1, 2, 3]): armar(n)
