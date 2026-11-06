"""Servilin (Víctor) v4_empresas: apertura «NO ES OFERTA DE EMPLEO» + gancho al comprador + insignias REPSE·ISO·STPS + «Solo empresas · No es vacante» + CTA.
Motor de segmentos: cada segmento es una toma (o tarjeta) con voz clonada propia, o un tramo del anuncio original con su audio.
Uso: python3 armar_victor_v4.py [v1|v2|obra]"""
import subprocess, sys
from pathlib import Path
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/XV')
from PIL import Image, ImageDraw
from armar_xv import fu, tex
from armar_victor_cliente import FF, voz, duracion, MUSICA, ff

AQUI = Path(__file__).resolve().parent
ACT = AQUI.parent / 'whatsapp' / 'anuncios_activos'
TMP = Path('/tmp/claude-1000/-workspaces-Nexusv2-0launch18octubre/632e0195-4202-422b-a741-74f9ff894c0c/scratchpad/victor_v4'); TMP.mkdir(parents=True, exist_ok=True)
W, H = 1080, 1920
AM, VE, AZ = (250, 214, 50), (37, 211, 102), (10, 28, 64)
T = lambda n: AQUI / 'tomas' / f'{n}.mp4'
S = lambda n: AQUI / 'v2' / f'{n}.mp4'
CTA_V = 'Solicita una propuesta para tu empresa por WhatsApp. Dinos qué tipo de inmueble y cuántos metros cuadrados.'


def insignias(ruta):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    f = fu(34, 'ExtraBold'); ws = [d.textlength(t, font=f) + 44 for t in ('REPSE', 'ISO', 'STPS')]
    x = (W - sum(ws) - 2 * 16) / 2
    for t, w in zip(('REPSE', 'ISO', 'STPS'), ws):
        d.rounded_rectangle((x, 130, x + w, 192), 31, fill=(255, 255, 255, 215)); d.text((x + 22, 141), t, font=f, fill=AZ); x += w + 16
    f2 = fu(30, 'ExtraBold'); t = 'SOLO EMPRESAS · NO ES VACANTE'; a = d.textlength(t, font=f2) + 48; x0 = (W - a) / 2
    d.rounded_rectangle((x0, 210, x0 + a, 266), 28, fill=AZ + (225,), outline=AM + (255,), width=3); d.text((x0 + 24, 222), t, font=f2, fill=AM)
    img.save(ruta)


def tarj_apertura(ruta):
    img = Image.new('RGB', (W, H), AZ); d = ImageDraw.Draw(img)
    cx, cy = W // 2, 640   # triángulo de advertencia dibujado (la fuente no trae emoji)
    d.polygon([(cx, cy - 150), (cx + 175, cy + 130), (cx - 175, cy + 130)], fill=AM)
    d.polygon([(cx, cy - 105), (cx + 128, cy + 108), (cx - 128, cy + 108)], fill=AZ)
    d.rounded_rectangle((cx - 14, cy - 55, cx + 14, cy + 30), 8, fill=AM); d.ellipse((cx - 15, cy + 50, cx + 15, cy + 80), fill=AM)
    def c(t, y, tam, col, peso='Black'):
        f = fu(tam, peso)
        while d.textlength(t, font=f) > W - 80: tam -= 2; f = fu(tam, peso)
        d.text(((W - d.textlength(t, font=f)) / 2, y), t, font=f, fill=col)
    c('NO ES OFERTA', 860, 150, (255, 255, 255)); c('DE EMPLEO', 1020, 170, AM)
    c('Servicio de limpieza para EMPRESAS', 1260, 52, (255, 255, 255), 'Bold')
    img.save(ruta)


def tarj_cta(ruta, l1, l2):
    img = Image.new('RGB', (W, H), AZ); d = ImageDraw.Draw(img)
    def c(t, y, tam, col, peso='Black'):
        f = fu(tam, peso)
        while d.textlength(t, font=f) > W - 110: tam -= 2; f = fu(tam, peso)
        d.text(((W - d.textlength(t, font=f)) / 2, y), t, font=f, fill=col)
    c('SERVILIN', 520, 130, (255, 255, 255)); c(l1, 680, 46, AM); c(l2, 755, 40, (255, 255, 255), 'Bold')
    t = 'SOLICITA UNA PROPUESTA POR WHATSAPP'; f = fu(36, 'ExtraBold'); a = d.textlength(t, font=f) + 100
    d.rounded_rectangle(((W - a) / 2, 900, (W + a) / 2, 1020), 60, fill=VE); d.text(((W - a) / 2 + 50, 938), t, font=f, fill=(255, 255, 255))
    c('PARA TU EMPRESA', 1075, 44, (255, 255, 255), 'Bold')
    c('¿QUÉ TIPO DE INMUEBLE', 1160, 52, AM); c('Y CUÁNTOS M²?', 1230, 52, AM)
    img.save(ruta)


def motor(nombre, segs):
    """segs: dict(tipo='png'|'clip'|'orig', src, ss, dur, cap, wav, golpe)"""
    insignias(TMP / 'ins.png')
    ent, fl, aud = [], '', []
    t0 = 0.0
    for i, s in enumerate(segs):
        d = s['dur']
        if s['tipo'] == 'png': ent += ['-loop', '1', '-t', f'{d:.2f}', '-i', str(s['src'])]
        else: ent += ['-ss', str(s.get('ss', 0)), '-t', f'{d + 0.3:.2f}', '-i', str(s['src'])]
        fl += (f'[{i}:v]scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},fps=30,setsar=1,format=yuv420p,'
               f'tpad=stop_mode=clone:stop_duration=4,trim=duration={d:.2f},setpts=PTS-STARTPTS[c{i}];')
        s['t0'] = t0; t0 += d
    n = len(segs); TOTAL = t0
    fl += ''.join(f'[c{i}]' for i in range(n)) + f'concat=n={n}:v=1:a=0[base];'
    k = n; ent += ['-loop', '1', '-t', f'{TOTAL:.1f}', '-i', str(TMP / 'ins.png')]
    fl += f'[base][{k}:v]overlay=0:0[cur0];'; cur = 'cur0'; k += 1
    for j, s in enumerate(segs):
        if not s.get('cap'): continue
        p = TMP / f'cap{j}.png'; tex(s['cap'], p, 1380, tam=70); ent += ['-loop', '1', '-t', f'{TOTAL:.1f}', '-i', str(p)]
        fl += f"[{cur}][{k}:v]overlay=0:0:enable='between(t,{s['t0'] + 0.1:.2f},{s['t0'] + s['dur'] - 0.05:.2f})'[oc{j}];"; cur = f'oc{j}'; k += 1
    # audio
    mudo = []
    for i, s in enumerate(segs):
        ms = int(s['t0'] * 1000)
        if s['tipo'] == 'orig':
            fl += f"[{i}:a]atrim=0:{s['dur']:.2f},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,afade=t=out:st={s['dur'] - 0.15:.2f}:d=0.15,adelay={ms}|{ms}[a{i}];"
            aud.append(f'[a{i}]'); mudo.append((s['t0'], s['t0'] + s['dur']))
        if s.get('wav'):
            ent += ['-i', str(s['wav'])]
            fl += f"[{k}:a]aresample=48000,adelay={ms + 120}|{ms + 120}[w{i}];"; aud.append(f'[w{i}]'); k += 1
    ent += ['-f', 'lavfi', '-t', '0.8', '-i', "aevalsrc='(sin(2*PI*70*t)*exp(-5*t)+0.4*sin(2*PI*140*t)*exp(-9*t))*0.9':s=48000"]
    fl += f'[{k}:a]aformat=channel_layouts=stereo,afade=t=out:st=0.5:d=0.3[th];'; aud.append('[th]'); k += 1
    ent += ['-i', str(MUSICA)]
    vol = '+'.join(f'between(t,{a:.2f},{b:.2f})' for a, b in mudo) or '0'
    fl += (f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo,aloop=loop=-1:size=2147483647,volume='if({vol},0,0.16)':eval=frame,afade=t=out:st={TOTAL - 1.2:.2f}:d=1.2,atrim=0:{TOTAL:.2f}[mu];")
    aud.append('[mu]')
    fl += ''.join(aud) + f'amix=inputs={len(aud)}:duration=longest:normalize=0,atrim=0:{TOTAL:.2f},loudnorm=I=-14:TP=-1.5[a]'
    sal = AQUI / f'{nombre}.mp4'; hd = TMP / f'{nombre}_hd.mp4'
    ff(ent + ['-filter_complex', fl, '-map', f'[{cur}]', '-map', '[a]', '-t', f'{TOTAL:.2f}', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', str(hd)])
    ff(['-i', str(hd), '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-profile:v', 'main', '-level', '3.1', '-pix_fmt', 'yuv420p', '-crf', '24', '-preset', 'medium', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(sal)])
    ff(['-i', str(sal), '-vf', 'fps=1/3.5,scale=240:-1,tile=4x2', '-frames:v', '1', str(AQUI / 'cuadros' / f'hoja_{nombre}.jpg')])
    ff(['-ss', '0.3', '-i', str(sal), '-frames:v', '1', str(AQUI / 'cuadros' / f'{nombre}_primer_cuadro.jpg')])
    print(sal, sal.stat().st_size // 1024, 'KB', f'{TOTAL:.1f}s')


def anuncio_original(nombre, orig, tomas_gancho, corte):
    tarj_apertura(TMP / 'apertura.png'); tarj_cta(TMP / 'cta.png', 'LIMPIEZA Y MANTENIMIENTO', 'PLANTAS · OFICINAS · BODEGAS')
    h1 = voz('¿Administras una planta, oficina o bodega?'); h2 = voz('Deja de batallar con el personal de limpieza: nosotros nos encargamos.'); wc = voz(CTA_V)
    segs = [dict(tipo='png', src=TMP / 'apertura.png', dur=2.2),
            dict(tipo='clip', src=tomas_gancho[0], dur=duracion(h1), wav=h1, cap=['¿ADMINISTRAS UNA PLANTA,', 'OFICINA O BODEGA?']),
            dict(tipo='clip', src=tomas_gancho[1], dur=duracion(h2), wav=h2, cap=['DEJA DE BATALLAR', 'NOSOTROS NOS ENCARGAMOS']),
            dict(tipo='orig', src=orig, dur=corte),
            dict(tipo='png', src=TMP / 'cta.png', dur=duracion(wc) + 1.2, wav=wc)]
    motor(nombre, segs)


def obra_fina():
    tarj_apertura(TMP / 'apertura.png'); tarj_cta(TMP / 'cta.png', 'LIMPIEZA DE OBRA FINA', 'CASAS · DEPARTAMENTOS · DESARROLLOS')
    V = AQUI / 'v4'
    fr = [('¿Eres constructora o desarrollador? Entregamos tus casas y departamentos listos: limpieza de obra fina.', 'O1_piso', ['¿ERES CONSTRUCTORA', 'O DESARROLLADOR?']),
          ('Retiramos el polvo de obra, el cemento y los restos de pintura.', 'O3_aspirar', ['POLVO DE OBRA FUERA', 'LIMPIEZA DE OBRA FINA']),
          ('Quitamos plásticos protectores y etiquetas de ventanas y cocina.', 'O4_plastico', ['QUITAMOS PLÁSTICOS', 'Y ETIQUETAS']),
          ('Con personal uniformado, capacitado y supervisado, a tu servicio. Tu obra lista para entregar.', 'O5_listo', ['PERSONAL UNIFORMADO', 'CAPACITADO Y SUPERVISADO'])]
    segs = [dict(tipo='png', src=TMP / 'apertura.png', dur=2.2)]
    for t, esc, cap in fr:
        w = voz(t); segs.append(dict(tipo='clip', src=V / f'{esc}.mp4', dur=duracion(w), wav=w, cap=cap))
    wc = voz(CTA_V); segs.append(dict(tipo='png', src=TMP / 'cta.png', dur=duracion(wc) + 1.2, wav=wc))
    motor('servilin_obra_fina_v4_empresas', segs)


if __name__ == '__main__':
    for k in sys.argv[1:] or ['v1', 'v2']:
        if k == 'v1': anuncio_original('servilin_v1_v4_empresas', ACT / 'servilin_v1.mp4', [T('V4_listos'), T('V2_escucha')], 13.5)
        if k == 'obra': obra_fina()
        if k == 'v2': anuncio_original('servilin_v2_v4_empresas', ACT / 'servilin_v2.mp4', [S('S2_ventanas'), S('S4_supervision')], 13.5)
