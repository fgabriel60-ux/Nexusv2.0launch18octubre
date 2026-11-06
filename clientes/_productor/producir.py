"""Productor rápido de videos de muestra: Qwen3-VL (Modal) mira el material real del cliente y escribe el plan → voz Fish por frase →
escenas con IA (Qwen-Image-Edit + MiniMax H3) solo donde el plan las pide → armado 9:16 con textos y tarjeta de WhatsApp.

Uso: python3 producir.py <carpeta del cliente> [--voz ID_FISH] [--solo-plan]
La carpeta necesita datos.txt (qué vende, qué dijo el cliente, teléfono, qué NO inventar) y su material en whatsapp/ o material/.
Deja en <carpeta>/video/: plan_qwen.json, voz/, escenas/ y <Carpeta>_qwen_v1.mp4."""
import argparse, io, json, re, subprocess, sys, urllib.request
from pathlib import Path
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/XV')
import imageio_ffmpeg
import modal
from PIL import Image, ImageDraw, ImageOps
from armar_xv import fu, tex

FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H = 1080, 1920
TARJ = 3.6
MUSICA = Path('/workspaces/Nexusv2.0launch18octubre/clientes/XV/musica_suave_s7.wav')
LOCUTOR = 'def180b161a3498db94025d5124fcb2a'   # voz por defecto de Fish cuando el cliente no mandó audio
LLAVE = [l.split('=', 1)[1].strip().strip('"\'') for l in open('/workspaces/Nexusv2.0launch18octubre/.env') if l.startswith('FISH_API_KEY=')][0]
CADENA = ('highpass=f=80,equalizer=f=180:t=q:w=1:g=2,equalizer=f=3200:t=q:w=1:g=3.5,'
          'acompressor=threshold=-20dB:ratio=3.5:attack=5:release=80:makeup=5,alimiter=limit=0.95,loudnorm=I=-14:TP=-1.0')
MAX_IA = 3

INSTRUCCIONES = """Eres productor de anuncios verticales de 25 a 32 segundos para anuncios de Meta que llevan a WhatsApp (fórmula: oferta clara + confianza + calidad).
Arriba van {n} imágenes, una por cada pieza de material REAL del cliente, en este orden:
{lista}

DATOS DEL NEGOCIO (no inventes nada fuera de esto: ni precios, ni años, ni ciudad, ni garantías, ni marcas):
{datos}

Escribe el plan del video. Reglas:
- 5 a 7 frases de voz en español de México, cada una de 3 a 5 segundos hablada (8 a 14 palabras). La primera es el gancho y nombra a quien busca ese servicio o su problema.
- La última frase pide escribir por WhatsApp.
- Cada frase lleva una toma. Prefiere material real ("foto" o "video" con su clave M01, M02...). Usa cada clave una sola vez; para un "video" indica en qué segundo empieza.
- Puedes pedir como máximo {max_ia} tomas "ia" (escena generada) solo donde el material real no alcanza, sobre todo para el gancho. Una toma "ia" lleva:
  "refs": 1 o 2 claves de FOTOS reales en las que se basa, "cuadro": cómo es el primer cuadro (en español, una escena realista vertical basada en esas fotos, sin texto),
  "movimiento": cómo se mueve la cámara y qué pasa en 4 segundos (en inglés, sin habla).
- "pantalla": 1 o 2 líneas cortas en MAYÚSCULAS (máximo 26 caracteres cada una) que refuercen la frase.
- La tarjeta final usa solo nombre y teléfono que estén en los datos.
Responde SOLO con JSON válido, sin explicación, con esta forma:
{{"frases": [{{"voz": "...", "pantalla": ["...", "..."], "toma": {{"tipo": "foto", "clave": "M03"}}}},
             {{"voz": "...", "pantalla": ["..."], "toma": {{"tipo": "video", "clave": "M05", "inicio": 2.0}}}},
             {{"voz": "...", "pantalla": ["..."], "toma": {{"tipo": "ia", "refs": ["M01"], "cuadro": "...", "movimiento": "..."}}}}],
 "tarjeta": {{"nombre": "...", "subtitulo": "...", "linea": "...", "telefono": "..."}},
 "pedir_al_cliente": ["dato o toma que falta para la versión final"]}}"""


def ff(a):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1800:])


def duracion(ruta):
    t = subprocess.run([FF, '-i', str(ruta)], capture_output=True, text=True).stderr.split('Duration: ')[1].split(',')[0].split(':')
    return int(t[0]) * 3600 + int(t[1]) * 60 + float(t[2])


def material(carpeta):
    """Claves M01.. → (ruta, tipo, segundos) y una miniatura jpg por pieza para que Qwen la vea."""
    piezas, miniaturas = {}, []
    archivos = sorted(p for d in ('whatsapp', 'material') for p in (carpeta / d).rglob('*') if p.suffix.lower() in ('.jpg', '.jpeg', '.png', '.mp4'))
    for i, p in enumerate(archivos[:24], 1):
        k = f'M{i:02d}'
        if p.suffix.lower() == '.mp4':
            seg = duracion(p); piezas[k] = (p, 'video', seg)
            raw = subprocess.run([FF, '-v', 'error', '-ss', str(min(1.0, seg / 2)), '-i', str(p), '-frames:v', '1', '-f', 'image2pipe', '-vcodec', 'mjpeg', '-'], capture_output=True).stdout
            im = Image.open(io.BytesIO(raw))
        else:
            piezas[k] = (p, 'foto', 0); im = ImageOps.exif_transpose(Image.open(p))
        im = im.convert('RGB'); im.thumbnail((512, 512)); b = io.BytesIO(); im.save(b, 'JPEG', quality=85); miniaturas.append(b.getvalue())
    return piezas, miniaturas


def planear(carpeta, piezas, miniaturas):
    lista = '\n'.join(f'{k}: {t}' + (f' de {s:.0f} s' if t == 'video' else '') for k, (_, t, s) in piezas.items())
    prompt = INSTRUCCIONES.format(n=len(piezas), lista=lista, datos=(carpeta / 'datos.txt').read_text().strip(), max_ia=MAX_IA)
    Productor = modal.Cls.from_name('qwen-productor', 'Productor')
    for intento in range(3):   # Qwen a veces entrega 3 frases: se le vuelve a pedir
        texto = Productor().planear.remote([{'prompt': prompt + ('' if not intento else '\n\nOJO: tu plan anterior no cumplió. Deben ser de 5 a 7 frases y la última pide escribir por WhatsApp.'),
                                            'imagenes': miniaturas}])[0]
        m = re.search(r'\{.*\}', texto, re.S)
        try:
            plan = json.loads(m.group(0))
        except Exception:
            continue
        if 4 <= len(plan.get('frases', [])) <= 7:
            break
    else:
        raise SystemExit('Qwen no dio un plan válido en 3 intentos:\n' + texto[:2000])
    if 'whatsapp' not in plan['frases'][-1]['voz'].lower():   # Qwen casi nunca cierra con WhatsApp aunque se le pida: el cierre se agrega aquí
        usadas = {f['toma'].get('clave') for f in plan['frases']}
        libre = next((k for k, (_, t, _) in piezas.items() if t == 'foto' and k not in usadas), next(iter(piezas)))
        plan['frases'].append({'voz': 'Escríbeme por WhatsApp y te doy toda la información.', 'pantalla': ['ESCRÍBEME', 'POR WHATSAPP'],
                               'toma': {'tipo': 'foto', 'clave': libre}})
    ia = [f for f in plan['frases'] if f['toma']['tipo'] == 'ia']
    for f in ia[MAX_IA:]:   # tope de escenas con IA: las de más pasan a la primera foto real sin usar
        libre = next((k for k, (_, t, _) in piezas.items() if t == 'foto' and k not in {x['toma'].get('clave') for x in plan['frases']}), None)
        f['toma'] = {'tipo': 'foto', 'clave': libre or next(iter(piezas))}
    for f in plan['frases']:
        t = f['toma']
        if t['tipo'] in ('foto', 'video') and t.get('clave') not in piezas: raise SystemExit(f'Clave inexistente en el plan: {t}')
        if t['tipo'] == 'ia' and not [r for r in t.get('refs', []) if r in piezas and piezas[r][1] == 'foto']: raise SystemExit(f'Escena IA sin foto real de referencia: {t}')
    return plan


def voces(plan, voz, dest):
    """Una pista por frase para que cada toma dure exactamente lo que se habla."""
    dest.mkdir(parents=True, exist_ok=True)
    for i, f in enumerate(plan['frases']):
        mp3 = dest / f'f{i}.mp3'
        r = urllib.request.Request('https://api.fish.audio/v1/tts', method='POST',
                                   data=json.dumps({'text': f['voz'], 'format': 'mp3', 'reference_id': voz, 'prosody': {'speed': 1.06}, 'temperature': 0.65, 'top_p': 0.8}).encode(),
                                   headers={'Authorization': 'Bearer ' + LLAVE, 'Content-Type': 'application/json', 'model': 's2-pro'})
        mp3.write_bytes(urllib.request.urlopen(r, timeout=300).read())
        ff(['-i', str(mp3), '-af', f'{CADENA},apad=pad_dur=0.25', '-ar', '48000', '-ac', '2', str(dest / f'f{i}.wav')])
        f['segundos'] = round(duracion(dest / f'f{i}.wav'), 2)


def escenas_ia(carpeta, plan, piezas, dest):
    ia = [(i, f['toma']) for i, f in enumerate(plan['frases']) if f['toma']['tipo'] == 'ia']
    if not ia: return
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from escenas_modal import app, escenas
    refs, cuadros, tomas = {}, {}, []
    for i, t in ia:
        for r in t['refs']:
            refs[r] = piezas[r][0].read_bytes()
        cuadros[f'C{i}'] = ([r for r in t['refs'] if r in piezas], t['cuadro'] + ' Foto vertical 9:16, realista, nítida, sin texto, sin letras.')
        tomas.append((f'T{i}', f'C{i}', t['movimiento'] + ' Vertical 9:16, realistic, no text. Audio: soft ambience, no speech.', plan['frases'][i]['segundos']))
    with app.run():
        res = escenas.remote(re.sub(r'\W', '_', carpeta.name.lower()), refs, cuadros, tomas)
    dest.mkdir(parents=True, exist_ok=True)
    for n, b in res.items():
        (dest / n).write_bytes(b)


def tarjeta(ruta, t):
    img = Image.new('RGB', (W, H), (14, 14, 16)); d = ImageDraw.Draw(img)
    AMAR, VERDE = (255, 196, 0), (37, 211, 102)
    def c(s, y, tam, col, peso='Black'):
        if not s: return
        f = fu(tam, peso)
        while d.textlength(s, font=f) > W - 110: tam -= 2; f = fu(tam, peso)
        d.text(((W - d.textlength(s, font=f)) / 2, y), s, font=f, fill=col)
    c(t.get('nombre', '').upper(), 560, 110, (255, 255, 255)); c(t.get('subtitulo', '').upper(), 690, 60, AMAR)
    c(t.get('linea', '').upper(), 800, 42, (255, 255, 255), 'Bold')
    s = 'ESCRÍBENOS POR WHATSAPP'; f = fu(50, 'ExtraBold'); a = d.textlength(s, font=f) + 110
    d.rounded_rectangle(((W - a) / 2, 960, (W + a) / 2, 1090), 65, fill=VERDE); d.text(((W - a) / 2 + 55, 995), s, font=f, fill=(255, 255, 255))
    c(t.get('telefono', ''), 1160, 104, AMAR)
    img.save(ruta)


def armar(carpeta, plan, piezas, vdir, tmp):
    tmp.mkdir(parents=True, exist_ok=True)
    tarjeta(tmp / 'tarjeta.png', plan['tarjeta'])
    frases = plan['frases']; T = sum(f['segundos'] for f in frases); TOTAL = T + TARJ
    ent, fl = [], ''
    AJUSTE = f'scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},unsharp=5:5:0.6,eq=contrast=1.06:saturation=1.12'
    for i, f in enumerate(frases):
        t, d = f['toma'], f['segundos']
        if t['tipo'] == 'video':
            ini = min(float(t.get('inicio', 0)), max(0, piezas[t['clave']][2] - d))
            ent += ['-ss', f'{ini:.2f}', '-t', f'{d:.2f}', '-i', str(piezas[t['clave']][0])]
            fl += f'[{i}:v]{AJUSTE},fps=30,setsar=1,format=yuv420p,tpad=stop_mode=clone:stop_duration=2,trim=duration={d:.2f},setpts=PTS-STARTPTS[c{i}];'
        elif t['tipo'] == 'ia':
            ent += ['-i', str(vdir / 'escenas' / f'T{i}.mp4')]
            fl += f'[{i}:v]{AJUSTE},fps=30,setsar=1,format=yuv420p,tpad=stop_mode=clone:stop_duration=2,trim=duration={d:.2f},setpts=PTS-STARTPTS[c{i}];'
        else:   # foto real con acercamiento lento
            foto = tmp / f'foto{i}.jpg'
            ImageOps.fit(ImageOps.exif_transpose(Image.open(piezas[t['clave']][0])).convert('RGB'), (int(W * 1.12), int(H * 1.12)), Image.LANCZOS).save(foto, quality=95)
            ent += ['-loop', '1', '-t', f'{d:.2f}', '-i', str(foto)]
            fl += (f"[{i}:v]crop={W}:{H}:x='(iw-{W})/2*(1-t/{d:.2f})':y='(ih-{H})/2*(1-t/{d:.2f})',unsharp=5:5:0.4,fps=30,setsar=1,format=yuv420p,"
                   f"trim=duration={d:.2f},setpts=PTS-STARTPTS[c{i}];")
    k = len(frases)
    ent += ['-loop', '1', '-t', str(TARJ), '-i', str(tmp / 'tarjeta.png')]
    fl += f'[{k}:v]scale={W}:{H},fps=30,setsar=1,format=yuv420p[tj];' + ''.join(f'[c{i}]' for i in range(k)) + f'[tj]concat=n={k + 1}:v=1:a=0[base];'
    cur, t0 = 'base', 0.0
    for j, f in enumerate(frases):
        p = tmp / f't{j}.png'; tex([s.upper() for s in f['pantalla'][:2]], p, 1380, tam=74); ent += ['-loop', '1', '-t', f'{TOTAL:.1f}', '-i', str(p)]
        fl += f"[{cur}][{k + 1 + j}:v]overlay=0:0:enable='between(t,{t0 + 0.1:.2f},{t0 + f['segundos'] - 0.05:.2f})'[o{j}];"; cur = f'o{j}'; t0 += f['segundos']
    a0 = k + 1 + k
    voz = tmp / 'voz.wav'
    lista = tmp / 'voces.txt'; lista.write_text(''.join(f"file '{vdir / 'voz' / f'f{i}.wav'}'\n" for i in range(k)))
    ff(['-f', 'concat', '-safe', '0', '-i', str(lista), '-c', 'copy', str(voz)])
    ent += ['-i', str(MUSICA), '-i', str(voz)]
    fl += (f"[{a0}:a]aresample=48000,aloop=loop=-1:size=2147483647,volume=0.16,afade=t=in:st=0:d=0.5,afade=t=out:st={TOTAL - 1.2:.2f}:d=1.2,atrim=0:{TOTAL:.2f}[mu];"
           f"[{a0 + 1}:a]aresample=48000[vz];[mu][vz]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]")
    hd = tmp / 'hd.mp4'; sal = vdir / f'{carpeta.name}_qwen_v1.mp4'
    ff(ent + ['-filter_complex', fl, '-map', f'[{cur}]', '-map', '[a]', '-t', f'{TOTAL:.2f}', '-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', str(hd)])
    ff(['-i', str(hd), '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-pix_fmt', 'yuv420p', '-crf', '24', '-preset', 'slow', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(sal)])
    return sal, TOTAL


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('carpeta'); ap.add_argument('--voz', default=LOCUTOR); ap.add_argument('--solo-plan', action='store_true')
    a = ap.parse_args()
    carpeta = Path(a.carpeta).resolve(); vdir = carpeta / 'video'; vdir.mkdir(exist_ok=True)
    piezas, miniaturas = material(carpeta)
    print(len(piezas), 'piezas de material', flush=True)
    plan = planear(carpeta, piezas, miniaturas)
    (vdir / 'plan_qwen.json').write_text(json.dumps(plan, ensure_ascii=False, indent=1))
    print(json.dumps(plan, ensure_ascii=False, indent=1), flush=True)
    if a.solo_plan: return
    voces(plan, a.voz, vdir / 'voz')
    (vdir / 'plan_qwen.json').write_text(json.dumps(plan, ensure_ascii=False, indent=1))
    escenas_ia(carpeta, plan, piezas, vdir / 'escenas')
    sal, total = armar(carpeta, plan, piezas, vdir, Path('/tmp/claude-1000/-workspaces-Nexusv2-0launch18octubre/3f2c6b79-5aa7-409f-95e2-6c1cf5560d47/scratchpad/productor') / carpeta.name)
    print(sal, sal.stat().st_size // 1024, 'KB', f'{total:.1f}s')


if __name__ == '__main__':
    main()
