"""Mariano · Vizcaíno v5 «gancho estilo Spiderman» (reel DbtClvhPXju) con la calidad de Lisbeth v7:
salto desde el techo de la Salvia REAL → aterrizaje en pose de superhéroe → «¿Buscas casa en Rosarito? Vizcaíno Residencial, ¡mira esto!» (labios con su voz
clonada, subtítulos virales palabra por palabra) → brazo al cielo + whoosh + DROP del beat → dron (visualización) → los 4 modelos con tomas REALES de sus
recorridos y precios REALES (Sotol 1.4M, Bugambilia 2.4M, Benjamina 2.8M, Salvia 4 rec. 3.1M) → privada/pádel/Infonavit → Mariano con el CTA → tarjeta WhatsApp.
Uso: python3 armar_spiderman.py rN vN      (rN = carpeta de tomas IA en spiderman/, vN = versión de salida)"""
import json, subprocess, sys
from pathlib import Path
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/XV')
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/_productor')
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from armar_xv import fu
from kinetic import palabras
import subs_virales
from spiderman_voces import FRASES, duracion
from spiderman_musica import beat

AQUI = Path(__file__).resolve().parent
SP = AQUI / 'spiderman'
DC = AQUI.parent / 'whatsapp' / 'del_cliente'
VID = {'sotol': DC / '20261015_145738_video.mp4', 'benjamina': DC / '20261017_173518_video.mp4', 'bugambilia': DC / '20261017_173615_video.mp4',
       'salvia': DC / '20261017_173640_video.mp4', 'caballos': DC / '20261022_122700_video_hoy_en_vizcaino.mp4'}
SFX = AQUI.parents[1] / 'Guillermo' / 'video' / 'sfx'
FF = imageio_ffmpeg.get_ffmpeg_exe()
PF = Path('/workspaces/Nexusv2.0launch18octubre/clientes/_productor/fuentes')
W, H, FPS = 720, 1280, 30
XD = 0.22            # duración de las transiciones entre secciones
VEL_VO = 1.06        # voz en off un poco más ágil (no afecta labios: sólo frases sin cara)
# ---- parámetros que se ajustan por ronda (cfg_vN.json los puede sobrescribir) ----
CFG = {
    'salto': [0.0, 5.2, 2.6],       # S_salto: desde, hasta, velocidad
    'habla_fin': 5.15,               # S_habla se corta aquí (después del «¡mira esto!» y con el brazo arriba)
    'aereo': [0.0, 4.0, 1.9],
    'noche': [0.4, 4.4, 2.2],
    'cierre_fin': 3.55,
    'final': 2.4,
    # tramos REALES (video, desde, duración, velocidad) por frase
    'sotol': [['sotol', 4.3, 1.1, 1.3], ['sotol', 7.6, 1.1, 1.3], ['sotol', 25.4, 1.2, 1.3]],
    'bugambilia': [['bugambilia', 14.0, 1.1, 1.3], ['bugambilia', 19.6, 1.2, 1.3], ['bugambilia', 42.0, 1.2, 1.3]],
    'benjamina': [['benjamina', 0.0, 0.55, 1.0], ['benjamina', 8.4, 1.2, 1.3], ['benjamina', 21.8, 1.4, 1.3]],
    'salvia': [['salvia', 0.0, 0.55, 1.0], ['salvia', 15.4, 1.2, 1.3], ['salvia', 47.2, 1.2, 1.3], ['salvia', 50.0, 1.3, 1.3]],
    'privada': [['salvia', 12.7, 1.6, 1.2], ['IA:S_noche', 0, 0, 0]],
    'caballos': False,
}
PRECIOS = {'sotol': ('SOTOL', '2 recámaras', '$1.4 MDP'), 'bugambilia': ('BUGAMBILIA', 'casa de 2 pisos', '$2.4 MDP'),
           'benjamina': ('BENJAMINA', 'casa de 2 pisos', '$2.8 MDP'), 'salvia': ('SALVIA', '4 recámaras', '$3.1 MDP')}
DORADO = (244, 196, 98)


def ff(a):
    r = subprocess.run([FF, '-nostdin', '-v', 'error', '-y', *a], capture_output=True, text=True, stdin=subprocess.DEVNULL)
    if r.returncode: raise SystemExit(f'rc={r.returncode} salida={a[-1]}\n' + r.stderr[-2500:])


def pf(est, tam):
    ruta, var = {'M': ('PlayfairDisplay[wght].ttf', b'Black'), 'i': ('PlayfairDisplay-Italic[wght].ttf', b'SemiBold Italic')}[est]
    f = ImageFont.truetype(str(PF / ruta), tam); f.set_variation_by_name(var); return f


def sombra_texto(img, xy, t, f, fill=(255, 255, 255, 255), blur=8):
    sh = Image.new('L', img.size, 0); ImageDraw.Draw(sh).text((xy[0], xy[1] + 4), t, font=f, fill=210)
    img.paste((0, 0, 0, 255), mask=sh.filter(ImageFilter.GaussianBlur(blur)))
    ImageDraw.Draw(img).text(xy, t, font=f, fill=fill)


AJ = f'scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},setsar=1'
PUNCH = f"zoompan=z='if(lt(on,7),1.10-0.0143*on,1)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS}"
GRADO_REAL = 'eq=contrast=1.06:saturation=1.12:gamma=0.98,unsharp=5:5:0.5'


def seg_real(nombre, tramos, ruta, dur):
    """Varios tramos reales con corte seco + punch-in en cada uno; se ajusta exacto a `dur`."""
    ent, fl = [], ''
    for i, (v, a, d, vel) in enumerate(tramos):
        ent += ['-ss', str(a), '-t', str(d), '-i', str(VID[v])]
        fl += f'[{i}:v]{AJ},setpts=(PTS-STARTPTS)/{vel},fps={FPS},{PUNCH},{GRADO_REAL},format=yuv420p[t{i}];'
    fl += ''.join(f'[t{i}]' for i in range(len(tramos))) + f'concat=n={len(tramos)}:v=1:a=0,tpad=stop_mode=clone:stop_duration=3,trim=duration={dur:.3f},setpts=PTS-STARTPTS[o]'
    ff(ent + ['-filter_complex', fl, '-map', '[o]', '-an', '-c:v', 'libx264', '-crf', '14', '-preset', 'fast', '-r', str(FPS), str(ruta)])


def seg_ia(clip, a, b, vel, ruta, dur, extra=''):
    ff(['-i', str(clip), '-filter_complex', f'[0:v]trim=start={a}:end={b},setpts=(PTS-STARTPTS)/{vel},{AJ},fps={FPS},{extra}tpad=stop_mode=clone:stop_duration=3,'
        f'trim=duration={dur:.3f},setpts=PTS-STARTPTS,format=yuv420p[o]', '-map', '[o]', '-an', '-c:v', 'libx264', '-crf', '14', '-preset', 'fast', str(ruta)])


def tarjeta_precio(clave, ruta):
    nom, sub, precio = PRECIOS[clave]
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    for y in range(int(H * 0.58), H):
        d.line([(0, y), (W, y)], fill=(5, 8, 16, int(200 * min(1, (y - H * 0.58) / (H * 0.2)))))
    f = pf('M', 104)
    while d.textlength(nom, font=f) > W - 80: f = pf('M', f.size - 4)
    sombra_texto(img, ((W - d.textlength(nom, font=f)) / 2, 905), nom, f)
    fi = pf('i', 44); t = sub
    sombra_texto(img, ((W - d.textlength(t, font=fi)) / 2, 1030), t, fi, (235, 235, 235, 255))
    fd = fu(34, 'Bold'); fp = fu(76, 'Black'); a, b = 'DESDE ', precio
    x = (W - d.textlength(a, font=fd) - d.textlength(b, font=fp)) / 2
    sombra_texto(img, (x, 1118), a, fd); sombra_texto(img, (x + d.textlength(a, font=fd), 1088), b, fp, DORADO + (255,))
    img.save(ruta)


def etiqueta(txt, ruta, abajo=True):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img); f = fu(22, 'Bold')
    w = d.textlength(txt, font=f) + 28; y = H - 70 if abajo else 40
    d.rounded_rectangle((W - w - 24, y, W - 24, y + 38), 19, fill=(0, 0, 0, 120)); d.text((W - w - 10, y + 8), txt, font=f, fill=(255, 255, 255, 230))
    img.save(ruta)


def marca(ruta):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    f1, f2 = pf('M', 34), fu(17, 'Bold')
    sombra_texto(img, (34, 64), 'VIZCAÍNO', f1, blur=6); sombra_texto(img, (36, 110), 'RESIDENCIAL · ROSARITO, B.C.', f2, (255, 255, 255, 235), blur=5)
    img.save(ruta)


def boton_wa(ruta, y=1090):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    t1 = 'Escribe «VIZCAÍNO»'; f = fu(40, 'ExtraBold'); a = d.textlength(t1, font=f) + 150
    sh = Image.new('L', (W, H), 0); ImageDraw.Draw(sh).rounded_rectangle(((W - a) / 2, y + 8, (W + a) / 2, y + 108), 50, fill=150)
    img.paste((0, 0, 0, 255), mask=sh.filter(ImageFilter.GaussianBlur(14)))
    d.rounded_rectangle(((W - a) / 2, y, (W + a) / 2, y + 100), 50, fill=(37, 211, 102))
    cx, cy = (W - a) / 2 + 58, y + 50   # ícono simple de chat
    d.ellipse((cx - 26, cy - 26, cx + 26, cy + 26), outline=(255, 255, 255), width=5); d.polygon([(cx - 22, cy + 14), (cx - 30, cy + 30), (cx - 8, cy + 24)], fill=(255, 255, 255))
    d.text(((W - a) / 2 + 100, y + 24), t1, font=f, fill=(255, 255, 255))
    img.save(ruta)


def tarjeta_final(fondo, ruta):
    im = Image.open(fondo).convert('RGB').resize((W, H)).filter(ImageFilter.GaussianBlur(14))
    im = Image.blend(im, Image.new('RGB', (W, H), (6, 10, 22)), 0.62).convert('RGBA'); d = ImageDraw.Draw(im)
    def c(t, y, f, col=(255, 255, 255, 255)):
        sombra_texto(im, ((W - d.textlength(t, font=f)) / 2, y), t, f, col)
    c('VIZCAÍNO', 170, pf('M', 110)); c('Residencial · Rosarito, B.C.', 305, pf('i', 46), DORADO + (255,))
    y = 420
    for k in ('sotol', 'bugambilia', 'benjamina', 'salvia'):
        nom, sub, precio = PRECIOS[k]
        f1, f2 = fu(40, 'Black'), fu(40, 'Black')
        d.text((110, y), nom, font=f1, fill=(255, 255, 255)); t = 'desde ' + precio; fd = fu(30, 'Bold')
        d.text((W - 110 - d.textlength(precio, font=f2), y), precio, font=f2, fill=DORADO)
        d.text((W - 110 - d.textlength(precio, font=f2) - d.textlength('desde ', font=fd) - 4, y + 9), 'desde', font=fd, fill=(220, 220, 220))
        d.line([(110, y + 66), (W - 110, y + 66)], fill=(255, 255, 255, 60), width=2); y += 92
    c('En privada · cancha de pádel', y + 20, fu(30, 'Bold')); c('Infonavit y crédito hipotecario', y + 62, fu(30, 'Bold'))
    im.save(ruta)


def componer(base, capas, total, sal, fx=None):
    """Capas RGBA (png, desde, hasta, fade, subida) sobre el video base, cuadro por cuadro en Python (memoria constante)."""
    import numpy as np
    ims = {}
    def carga(p):
        if p not in ims:
            a = np.asarray(Image.open(p).convert('RGBA')).astype(np.float32) / 255
            ys, xs = np.nonzero(a[..., 3] > 0.003)
            if len(ys) == 0: ims[p] = None
            else:
                y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
                ims[p] = (y0, x0, a[y0:y1, x0:x1])
        return ims[p]
    n = int(round(total * FPS)); fb = W * H * 3
    dec = subprocess.Popen([FF, '-nostdin', '-v', 'error', '-i', str(base), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    enc = subprocess.Popen([FF, '-nostdin', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-c:v', 'libx264', '-crf', '14', '-preset', 'medium', '-pix_fmt', 'yuv420p', str(sal)], stdin=subprocess.PIPE)
    ultimo = None
    for i in range(n):
        b = dec.stdout.read(fb)
        if len(b) == fb: ultimo = b
        fr = np.frombuffer(ultimo, np.uint8).reshape(H, W, 3).astype(np.float32) / 255
        t = i / FPS
        for p, a, z, fd, rise in capas:
            if not (a <= t <= z): continue
            c = carga(p)
            if c is None: continue
            y0, x0, im = c; al = min(1.0, (t - a) / fd) if fd else 1.0
            y0 = int(y0 + rise * (1 - al)); h, w = im.shape[:2]
            y1 = min(H, y0 + h); 
            if y1 <= y0: continue
            sub = im[:y1 - y0]; m = sub[..., 3:4] * al
            fr[y0:y1, x0:x0 + w] = fr[y0:y1, x0:x0 + w] * (1 - m) + sub[..., :3] * m
        if fx: fr = fx(fr, t)
        enc.stdin.write((fr * 255 + 0.5).clip(0, 255).astype(np.uint8).tobytes())
    enc.stdin.close(); enc.wait(); dec.kill()
    if enc.returncode: raise SystemExit('falló componer')


def main():
    ronda, ver = sys.argv[1], sys.argv[2]
    cfgp = SP / f'cfg_{ver}.json'
    if cfgp.exists(): CFG.update(json.loads(cfgp.read_text()))
    IA = SP / ronda
    def ia(n):
        p = IA / f'{n}.mp4'
        if p.exists(): return p
        hechos = sorted(SP.glob(f'r*/{n}.mp4'), key=lambda q: q.stat().st_mtime); return hechos[-1]
    TMP = Path(f'/tmp/claude-1000/-workspaces-Nexusv2-0launch18octubre/b4c6325f-3619-4737-92c5-2c71e199d91e/scratchpad/sp_{ver}'); TMP.mkdir(parents=True, exist_ok=True)
    VOZ = SP / 'voz'
    # voces: gancho y cta con labios (velocidad original); el resto en off un poco más rápido
    dv = {}
    for n in FRASES:
        src = VOZ / f'{n}.wav'
        if n in ('gancho', 'cta'): dv[n] = duracion(src); continue
        ff(['-i', str(src), '-af', f'atempo={VEL_VO}', '-ar', '44100', str(TMP / f'{n}.wav')]); dv[n] = duracion(TMP / f'{n}.wav')
    s0, s1, sv = CFG['salto']; d_salto = (s1 - s0) / sv
    d_habla = CFG['habla_fin']
    a0, a1, av = CFG['aereo']; d_aereo = (a1 - a0) / av
    # secciones: (nombre, duración visible, voz que empieza con ella)
    secs = [('salto', d_salto, None), ('habla', d_habla, 'gancho'), ('aereo', d_aereo, None)]
    for k in ('sotol', 'bugambilia', 'benjamina', 'salvia', 'privada'):
        secs.append((k, dv[k] + 0.12, k))
    secs += [('cierre', CFG['cierre_fin'], 'cta'), ('final', CFG['final'], None)]
    # cada sección se renderiza XD más larga (salvo la última) para que la transición no robe tiempo
    rutas = []
    for i, (n, d, _) in enumerate(secs):
        dd = d + XD; r = TMP / f's{i:02d}_{n}.mp4'; rutas.append(r)
        if n == 'salto': seg_ia(ia('S_salto'), s0, s1, sv, r, dd)
        elif n == 'habla': seg_ia(ia('S_habla'), 0, CFG['habla_fin'] + 1, 1.0, r, dd)
        elif n == 'aereo': seg_ia(ia('S_aereo'), a0, a1, av, r, dd)
        elif n == 'cierre': seg_ia(ia('S_cierre'), 0, CFG['cierre_fin'] + 1, 1.0, r, dd)
        elif n == 'final':
            fondo = TMP / 'fondo_final.png'; ff(['-ss', '1.0', '-i', str(ia('S_noche')), '-frames:v', '1', str(fondo)])
            tarjeta_final(fondo, TMP / 'final.png')
            ff(['-loop', '1', '-t', f'{dd:.3f}', '-i', str(TMP / 'final.png'), '-vf', f"scale={W}:{H},zoompan=z='1+0.0006*on':d=1:s={W}x{H}:fps={FPS},format=yuv420p",
                '-c:v', 'libx264', '-crf', '14', '-preset', 'fast', str(r)])
        else:
            tramos = CFG[n]; reales = [t for t in tramos if not t[0].startswith('IA:')]; ias = [t for t in tramos if t[0].startswith('IA:')]
            if ias:   # parte real + parte IA (p. ej. la Salvia de noche)
                dr = sum(t[2] / t[3] for t in reales); seg_real(n, reales, TMP / f'{n}_a.mp4', dr)
                n0, n1, nv = CFG['noche']; seg_ia(ia(ias[0][0][3:]), n0, n1, nv, TMP / f'{n}_b.mp4', max(0.5, dd - dr), f'{PUNCH},')
                ff(['-i', str(TMP / f'{n}_a.mp4'), '-i', str(TMP / f'{n}_b.mp4'), '-filter_complex', '[0:v][1:v]concat=n=2:v=1:a=0[o]', '-map', '[o]', '-c:v', 'libx264', '-crf', '14', str(r)])
            else:
                seg_real(n, tramos, r, dd)
    # inicio de cada sección en la línea de tiempo final (las transiciones se comen XD de la sección anterior)
    ini, t = [], 0.0
    for i, (n, d, _) in enumerate(secs):
        ini.append(t); t += d
    TOTAL = t
    TRANS = {2: 'zoomin', 3: 'slideup', 4: 'hblur', 5: 'hblur', 6: 'hblur', 7: 'slideleft', 8: 'hblur', 9: 'fadeblack'}
    # unión por pasos (un xfade por llamada) para no llenar la RAM con todos los clips decodificados a la vez
    acc = rutas[0]
    for i in range(1, len(rutas)):
        tr = TRANS.get(i); nuevo = TMP / f'acc{i:02d}.mp4'
        if tr:
            f2 = f'[0:v]fps={FPS},format=yuv420p[a];[1:v]fps={FPS},format=yuv420p[b];[a][b]xfade=transition={tr}:duration={XD}:offset={ini[i] - XD / 2:.3f}[o]'
        else:   # salto→habla: corte seco en el impacto (continuidad del aterrizaje)
            f2 = f'[0:v]trim=duration={ini[i]:.3f},setpts=PTS-STARTPTS[a];[1:v]setpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=1:a=0,fps={FPS},format=yuv420p[o]'
        ff(['-i', str(acc), '-i', str(rutas[i]), '-filter_complex', f2, '-map', '[o]', '-c:v', 'libx264', '-crf', '11', '-preset', 'veryfast', str(nuevo)])
        acc = nuevo
    # capas: marca arriba en el b-roll, etiquetas de visualización, tarjetas de precio, subtítulos virales, botón de WhatsApp
    marca(TMP / 'marca.png'); etiqueta('Visualización', TMP / 'visual.png'); boton_wa(TMP / 'wa.png')
    capas = []   # (png, desde, hasta, fade, subida)
    idx = {n: i for i, (n, _, _) in enumerate(secs)}
    capas.append((TMP / 'marca.png', ini[idx['aereo']] + 0.1, ini[idx['cierre']], 0.25, 0))
    capas.append((TMP / 'visual.png', ini[idx['aereo']] + 0.1, ini[idx['aereo'] + 1], 0.2, 0))
    dr_priv = sum(t[2] / t[3] for t in CFG['privada'] if not t[0].startswith('IA:'))
    capas.append((TMP / 'visual.png', ini[idx['privada']] + dr_priv, ini[idx['cierre']], 0.2, 0))
    for kk in PRECIOS:
        tarjeta_precio(kk, TMP / f'p_{kk}.png'); capas.append((TMP / f'p_{kk}.png', ini[idx[kk]] + 0.12, ini[idx[kk]] + secs[idx[kk]][1], 0.18, 16))
    capas.append((TMP / 'wa.png', ini[idx['cierre']] + 0.5, ini[idx['final']] + CFG['final'], 0.2, 20))
    # subtítulos virales: gancho, privada y cta (los modelos llevan su tarjeta)
    ws = []
    for n, carpeta in (('gancho', VOZ), ('privada', TMP), ('cta', VOZ)):
        t0 = ini[idx[{'gancho': 'habla', 'privada': 'privada', 'cta': 'cierre'}[n]]]
        ws += [(w, a + t0, z + t0) for w, a, z in palabras(carpeta / f'{n}.wav', FRASES[n].replace('¿', '').replace('¡', '').replace('«', '').replace('»', ''))]
    subs = subs_virales.capas(ws, TMP / 'sv', y=CFG.get('subs_y', 0.70), W=W, H=H)
    capas += [(png, a, z, 0.17, 12) for png, a, z in subs]
    componer(acc, capas, TOTAL, TMP / 'video.mp4')
    # audio: voces en su sitio + beat con drop en la transición al dron + whoosh/golpes
    t_drop = ini[idx['aereo']]
    beat(TMP / 'beat.wav', t_drop, TOTAL)
    pistas = [(VOZ / 'gancho.wav', ini[idx['habla']], 1.0)] + [(TMP / f'{n}.wav', ini[idx[n]] + 0.06, 1.0) for n in ('sotol', 'bugambilia', 'benjamina', 'salvia', 'privada')] \
        + [(VOZ / 'cta.wav', ini[idx['cierre']], 1.0), (SFX / 'whoosh.wav', 0.0, 0.7), (SFX / 'golpe.wav', ini[idx['habla']] - 0.04, 1.0),
           (SFX / 'boom.wav', ini[idx['habla']] - 0.04, 0.5), (SFX / 'whoosh.wav', t_drop - 0.3, 0.9)] \
        + [(SFX / 'whoosh.wav', ini[idx[n]] - 0.15, 0.35) for n in ('sotol', 'bugambilia', 'benjamina', 'salvia', 'privada', 'cierre')]
    ent, fa = [], ''
    for j, (p, t0, g) in enumerate(pistas):
        ent += ['-i', str(p)]
        fa += f'[{j}:a]aresample=44100,aformat=channel_layouts=stereo,volume={g},adelay={int(max(0, t0) * 1000)}|{int(max(0, t0) * 1000)}[a{j}];'
    ent += ['-i', str(TMP / 'beat.wav')]; jb = len(pistas)
    # la música baja (ducking) mientras hay voz
    fa += ''.join(f'[a{j}]' for j in range(len(pistas))) + f'amix=inputs={len(pistas)}:duration=longest:normalize=0,apad=whole_dur={TOTAL:.3f},asplit=2[vz][key];'
    fa += f'[{jb}:a]aresample=44100,volume={CFG.get("musica", 0.55)}[mu];[mu][key]sidechaincompress=threshold=0.04:ratio=5:attack=20:release=300[mud];'
    fa += f'[vz][mud]amix=inputs=2:duration=longest:normalize=0,atrim=0:{TOTAL:.3f},loudnorm=I=-14:TP=-1.5[a]'
    ff(ent + ['-filter_complex', fa, '-map', '[a]', '-ar', '44100', str(TMP / 'mezcla.wav')])
    hd = TMP / 'video.mp4'
    sal = AQUI / f'Vizcaino_v5_gancho_spiderman_{ver}.mp4'
    for crf in (21, 23, 25, 27):
        ff(['-i', str(hd), '-i', str(TMP / 'mezcla.wav'), '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-pix_fmt', 'yuv420p', '-crf', str(crf), '-preset', 'slow',
            '-maxrate', '4M', '-bufsize', '8M', '-c:a', 'aac', '-b:a', '160k', '-ar', '44100', '-shortest', '-movflags', '+faststart', str(sal)])
        if sal.stat().st_size < 15.5e6: break
    (SP / f'tiempos_{ver}.json').write_text(json.dumps({n: round(ini[i], 2) for i, (n, _, _) in enumerate(secs)} | {'TOTAL': round(TOTAL, 2)}, indent=1))
    print(sal, sal.stat().st_size // 1024, 'KB', f'{TOTAL:.2f}s', {n: round(ini[i], 2) for i, (n, _, _) in enumerate(secs)})


if __name__ == '__main__':
    main()
