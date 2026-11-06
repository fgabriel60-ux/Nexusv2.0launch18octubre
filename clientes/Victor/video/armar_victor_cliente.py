"""Servilin (Víctor): versiones _cliente de los 4 videos. Gancho al comprador (empresas), etiqueta fija «SERVICIO PARA EMPRESAS · NO ES VACANTE»,
cero lenguaje de reclutamiento, CTA con pregunta de filtro. Voz clonada Fish (voz_id_fish.txt); frases cacheadas por texto.
Uso: python3 armar_victor_cliente.py [v1|v2|v2sl|v3 ...]"""
import hashlib, json, subprocess, sys, urllib.request
from pathlib import Path
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/XV')
import imageio_ffmpeg
from PIL import Image, ImageDraw
from armar_xv import fu, tex

AQUI = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
TMP = Path('/tmp/claude-1000/-workspaces-Nexusv2-0launch18octubre/632e0195-4202-422b-a741-74f9ff894c0c/scratchpad/victor_cli'); TMP.mkdir(parents=True, exist_ok=True)
MUSICA = AQUI.parents[1] / 'XV' / 'musica_suave_s7.wav'
REAL = AQUI.parent / 'whatsapp' / 'nuevas' / '1023_122723_24316.mp4'
LLAVE = [l.split('=', 1)[1].strip().strip('"\'') for l in open('/workspaces/Nexusv2.0launch18octubre/.env') if l.startswith('FISH_API_KEY=')][0]
VID = (AQUI / 'voz' / 'voz_id_fish.txt').read_text().strip()
CADENA = ('highpass=f=80,equalizer=f=180:t=q:w=1:g=2,equalizer=f=3200:t=q:w=1:g=3.5,'
          'acompressor=threshold=-20dB:ratio=3.5:attack=5:release=80:makeup=5,alimiter=limit=0.95,loudnorm=I=-14:TP=-1.0')
W, H = 1080, 1920
ETIQUETA = 'SERVICIO PARA EMPRESAS · NO ES VACANTE'
CTA_V = 'Cotiza el servicio para tu empresa por WhatsApp. Dinos qué tipo de inmueble y cuántos metros cuadrados.'
CTA_T = ['COTIZA EL SERVICIO PARA', 'TU EMPRESA POR WHATSAPP']
FR_EMP = [  # (voz, texto en pantalla)
    ('¿Administras una empresa, oficina o planta? Servilín es un servicio de limpieza y mantenimiento para empresas.', ['¿ADMINISTRAS UNA EMPRESA,', 'OFICINA O PLANTA?']),
    ('Personal uniformado, capacitado y supervisado, a tu servicio.', ['PERSONAL UNIFORMADO', 'CAPACITADO Y SUPERVISADO']),
    ('Tú te enfocas en producir; nosotros en la limpieza y el mantenimiento de tu empresa.', ['LIMPIEZA Y MANTENIMIENTO', 'PARA TU EMPRESA']),
    (CTA_V, CTA_T),
]
T = lambda n: AQUI / 'tomas' / f'{n}.mp4'
S = lambda n: AQUI / 'v2' / f'{n}.mp4'
VIDEOS = {
    'v1': ('Servilin_equipo_real_v1_cliente', [T('V1_equipo'), T('V2_escucha'), T('V3_supervisor'), T('V4_listos')], [0, 0, 0, 0], FR_EMP,
           ['SERVILIN', 'LIMPIEZA Y MANTENIMIENTO', 'PARA EMPRESAS Y PLANTAS']),
    'v2': ('Servilin_escenas_v2_cliente', [S('S1_trapeo'), S('S2_ventanas'), S('S3_maquina'), S('S4_supervision')], [0] * 4, FR_EMP,
           ['SERVILIN', 'LIMPIEZA Y MANTENIMIENTO', 'PARA EMPRESAS Y PLANTAS']),
    'v2sl': ('Servilin_escenas_v2_sin_liquido_cliente', [S('S1_trapeo'), S('S2_ventanas'), S('S3_seco_kb'), S('S4_supervision')], [0] * 4, FR_EMP,
             ['SERVILIN', 'LIMPIEZA Y MANTENIMIENTO', 'PARA EMPRESAS Y PLANTAS']),
    'v3': ('Servilin_obra_fina_v3_cliente', [S('S1_trapeo'), S('S4_supervision'), REAL, REAL], [0, 0, 2.0, 14.0], [
        ('¿Eres constructora o administras un desarrollo? Servilín es limpieza de obra fina para empresas.', ['¿ERES CONSTRUCTORA O', 'ADMINISTRAS UN DESARROLLO?']),
        ('Dejamos tu obra lista para entregar, con personal uniformado, capacitado y supervisado, a tu servicio.', ['PERSONAL UNIFORMADO', 'CAPACITADO Y SUPERVISADO']),
        ('También damos servicio de limpieza a plantas, bodegas y empresas.', ['PLANTAS · BODEGAS', 'Y EMPRESAS']),
        (CTA_V, CTA_T)], ['SERVILIN', 'LIMPIEZA DE OBRA FINA PARA EMPRESAS', 'PLANTAS · BODEGAS · CONSTRUCTORAS']),
}


def ff(a):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1800:])


def duracion(p):
    t = subprocess.run([FF, '-i', str(p)], capture_output=True, text=True).stderr.split('Duration: ')[1].split(',')[0].split(':')
    return int(t[0]) * 3600 + int(t[1]) * 60 + float(t[2])


def voz(texto):
    h = hashlib.sha1(texto.encode()).hexdigest()[:10]
    mp3 = AQUI / 'voz' / f'cli_{h}.mp3'; wav = AQUI / 'voz' / f'cli_{h}.wav'
    if not wav.exists():
        r = urllib.request.Request('https://api.fish.audio/v1/tts', method='POST',
                                   data=json.dumps({'text': texto, 'format': 'mp3', 'reference_id': VID, 'prosody': {'speed': 1.05}, 'temperature': 0.65, 'top_p': 0.8}).encode(),
                                   headers={'Authorization': 'Bearer ' + LLAVE, 'Content-Type': 'application/json', 'model': 's2-pro'})
        mp3.write_bytes(urllib.request.urlopen(r, timeout=300).read())
        ff(['-i', str(mp3), '-af', f'{CADENA},apad=pad_dur=0.25', '-ar', '48000', '-ac', '2', str(wav)])
    return wav


def etiqueta(ruta):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    f = fu(36, 'ExtraBold'); a = d.textlength(ETIQUETA, font=f) + 56
    x0 = (W - a) / 2
    d.rounded_rectangle((x0, 215, x0 + a, 285), 35, fill=(10, 28, 64, 225), outline=(250, 214, 50, 255), width=3)
    d.text((x0 + 28, 230), ETIQUETA, font=f, fill=(250, 214, 50))
    img.save(ruta)


def tarjeta(ruta, lin):
    img = Image.new('RGB', (W, H), (10, 28, 64)); d = ImageDraw.Draw(img)
    AM, VE = (250, 214, 50), (37, 211, 102)
    def c(t, y, tam, col, peso='Black'):
        f = fu(tam, peso)
        while d.textlength(t, font=f) > W - 110: tam -= 2; f = fu(tam, peso)
        d.text(((W - d.textlength(t, font=f)) / 2, y), t, font=f, fill=col)
    c('SERVILIN', 470, 130, (255, 255, 255)); c(lin[1], 630, 48, AM); c(lin[2], 710, 40, (255, 255, 255), 'Bold')
    t = 'COTIZA EL SERVICIO POR WHATSAPP'; f = fu(40, 'ExtraBold'); a = d.textlength(t, font=f) + 110
    d.rounded_rectangle(((W - a) / 2, 860, (W + a) / 2, 990), 65, fill=VE); d.text(((W - a) / 2 + 55, 898), t, font=f, fill=(255, 255, 255))
    c('¿QUÉ TIPO DE INMUEBLE', 1060, 52, AM); c('Y CUÁNTOS M²?', 1130, 52, AM)
    c('SERVICIO PARA EMPRESAS · NO ES VACANTE', 1260, 32, (200, 210, 230), 'Bold')
    img.save(ruta)


def armar(k):
    nombre, tomas, inis, frases, tj = VIDEOS[k]
    wavs = [voz(t) for t, _ in frases]; durs = [round(duracion(w), 2) for w in wavs]
    n = len(frases); TARJ = 5.0; TOTAL = sum(durs) + TARJ
    tarjeta(TMP / 'tarjeta.png', tj); etiqueta(TMP / 'etiq.png')
    ent, fl = [], ''
    for i, (toma, ini, d) in enumerate(zip(tomas, inis, durs)):
        ent += ['-ss', str(ini), '-t', f'{d + 0.3:.2f}', '-i', str(toma)]
        fl += (f'[{i}:v]scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},unsharp=5:5:0.6,eq=contrast=1.05:saturation=1.1,'
               f'fps=30,setsar=1,format=yuv420p,tpad=stop_mode=clone:stop_duration=4,trim=duration={d:.2f},setpts=PTS-STARTPTS[c{i}];')
    ent += ['-loop', '1', '-t', str(TARJ), '-i', str(TMP / 'tarjeta.png')]
    fl += f'[{n}:v]scale={W}:{H},fps=30,setsar=1,format=yuv420p[tj];' + ''.join(f'[c{i}]' for i in range(n)) + f'[tj]concat=n={n + 1}:v=1:a=0[base];'
    ent += ['-loop', '1', '-t', f'{TOTAL:.1f}', '-i', str(TMP / 'etiq.png')]
    fl += f'[base][{n + 1}:v]overlay=0:0[cur0];'; cur = 'cur0'; t0 = 0.0
    for j, ((_, lin), d) in enumerate(zip(frases, durs)):
        if j < n - 1:   # la última frase (CTA) ya está en la tarjeta; su texto va sobre la toma
            pass
        p = TMP / f't{j}.png'; tex(lin, p, 1380, tam=70); ent += ['-loop', '1', '-t', f'{TOTAL:.1f}', '-i', str(p)]
        fl += f"[{cur}][{n + 2 + j}:v]overlay=0:0:enable='between(t,{t0 + 0.1:.2f},{t0 + d - 0.05:.2f})'[o{j}];"; cur = f'o{j}'; t0 += d
    a0 = n + 2 + n; vz = TMP / 'voz.wav'
    ff([x for w in wavs for x in ('-i', str(w))] + ['-filter_complex', ''.join(f'[{i}:a]' for i in range(n)) + f'concat=n={n}:v=0:a=1[v]', '-map', '[v]', str(vz)])
    ent += ['-i', str(MUSICA), '-i', str(vz)]
    fl += (f"[{a0}:a]aresample=48000,aloop=loop=-1:size=2147483647,volume=0.18,afade=t=in:st=0:d=0.5,afade=t=out:st={TOTAL - 1.2:.2f}:d=1.2,atrim=0:{TOTAL:.2f}[mu];"
           f"[{a0 + 1}:a]aresample=48000[vz];[mu][vz]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]")
    hd = TMP / f'{k}_hd.mp4'; sal = AQUI / f'{nombre}.mp4'
    ff(ent + ['-filter_complex', fl, '-map', f'[{cur}]', '-map', '[a]', '-t', f'{TOTAL:.2f}', '-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', str(hd)])
    ff(['-i', str(hd), '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-pix_fmt', 'yuv420p', '-crf', '24', '-preset', 'slow', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(sal)])
    ff(['-i', str(sal), '-vf', f'fps=1/2.5,scale=240:-1,tile=4x2', '-frames:v', '1', str(AQUI / 'cuadros' / f'hoja_{k}_cliente.jpg')])
    print(sal, sal.stat().st_size // 1024, 'KB', f'{TOTAL:.1f}s', durs)


if __name__ == '__main__':
    for k in (sys.argv[1:] or VIDEOS): armar(k)
