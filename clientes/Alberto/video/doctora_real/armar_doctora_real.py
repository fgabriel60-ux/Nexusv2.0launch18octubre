"""Veneers Dental · Dra. Ángeles: su video REAL (grabado de lado, 16 s) girado, sin el arranque desenfocado, con gradación negro/dorado de la marca,
subtítulos virales palabra por palabra (los de Lisbeth v7), sello del logo, nombre en dorado, música suave y tarjeta de cierre.
Uso: python3 armar_doctora_real.py [--texto "guion corregido"]"""
import argparse, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import imageio_ffmpeg
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/XV')
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/_productor')
from armar_xv import fu
import kinetic, subs_virales

AQUI = Path(__file__).resolve().parent
FOTOS = AQUI.parents[1] / 'whatsapp' / 'del_cliente'
SFX = AQUI.parents[2] / 'Guillermo' / 'video' / 'sfx'
MUSICA = AQUI.parents[2] / 'XV' / 'musica_suave_s7.wav'
FF = imageio_ffmpeg.get_ffmpeg_exe()
TMP = Path('/tmp/claude-1000/-workspaces-Nexusv2-0launch18octubre/de8cbd3b-e5b6-4c3a-a052-a750f25f287f/scratchpad/doctora_real'); TMP.mkdir(parents=True, exist_ok=True)
W, H = 720, 1280
T0, T1 = 5.45, 16.32          # recorte del original (antes de 5.45 está desenfocado y dice «Aquí está»)
D = T1 - T0
TARJ = 3.2
ORO = (212, 175, 55)
WHATS, DIREC = '631 165 1910', 'Av. Álvaro Obregón 695 · Nogales, Son.'


def ff(a):
    r = subprocess.run([FF, '-v', 'error', '-y', *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-2000:])


def logo():
    im = Image.open(FOTOS / 'doctora_4.jpg').convert('L'); w, h = im.size
    c = im.crop((int(w * .17), int(h * .012), int(w * .447), int(h * .138)))
    out = Image.new('RGBA', c.size, (255, 255, 255, 0)); out.putalpha(c.point(lambda v: max(0, min(255, int((v - 40) * 1.6))))); return out


def tinte(lg, col):
    o = Image.new('RGBA', lg.size, col + (255,)); o.putalpha(lg.getchannel('A')); return o


def capa_marca():
    """Sello arriba a la izquierda + placa dorada con el nombre (se ve los primeros 4 s)."""
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    lg = tinte(logo(), (255, 255, 255)); lg = lg.resize((200, int(200 * lg.height / lg.width)), Image.LANCZOS)
    sh = Image.new('L', im.size, 0); sh.paste(lg.getchannel('A'), (36, 52)); sh = sh.filter(ImageFilter.GaussianBlur(8))
    im.paste((0, 0, 0, 255), mask=sh.point(lambda v: int(v * .7))); im.alpha_composite(lg, (36, 52))
    d = ImageDraw.Draw(im)
    f1, f2 = fu(40, 'Black'), fu(26, 'SemiBold')
    t1, t2 = 'Dra. Ángeles', 'Veneers Dental · Nogales'
    w = int(max(d.textlength(t1, font=f1), d.textlength(t2, font=f2))) + 56
    x0, y0 = 36, 150
    pl = Image.new('RGBA', (w, 120), (0, 0, 0, 0)); pd = ImageDraw.Draw(pl)
    pd.rounded_rectangle((0, 0, w - 1, 119), 18, fill=(10, 10, 12, 215), outline=ORO + (255,), width=3)
    pd.text((28, 12), t1, font=f1, fill=ORO + (255,)); pd.text((28, 70), t2, font=f2, fill=(255, 255, 255, 255))
    im.alpha_composite(pl, (x0, y0)); return im


def tarjeta(fondo):
    img = fondo.convert('RGBA'); img.alpha_composite(Image.new('RGBA', (W, H), (8, 8, 10, 205)))
    d = ImageDraw.Draw(img)
    lg = tinte(logo(), (255, 255, 255)); lg = lg.resize((360, int(360 * lg.height / lg.width)), Image.LANCZOS); img.alpha_composite(lg, ((W - 360) // 2, 250))
    d.line([(W // 2 - 90, 360), (W // 2 + 90, 360)], fill=ORO + (255,), width=3)
    def c(txt, y, tam, col, peso):
        f = fu(tam, peso); d.text(((W - d.textlength(txt, font=f)) / 2, y), txt, font=f, fill=col + (255,))
    c('Mejora el color, la forma', 410, 38, (255, 255, 255), 'ExtraBold'); c('y la separación de tus dientes', 462, 38, (255, 255, 255), 'ExtraBold')
    c('Agenda tu valoración', 560, 50, ORO, 'Black')
    txt = f'WhatsApp  {WHATS}'; f = fu(40, 'ExtraBold'); a = int(d.textlength(txt, font=f)) + 90
    d.rounded_rectangle(((W - a) // 2, 690, (W + a) // 2, 780), 45, fill=(37, 211, 102, 255)); d.text(((W - a) // 2 + 45, 710), txt, font=f, fill=(255, 255, 255, 255))
    c(DIREC, 830, 28, (225, 225, 225), 'SemiBold')
    p = TMP / 'tarjeta.png'; img.convert('RGB').save(p); return p


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--texto', default=None); ap.add_argument('--salida', default='Veneers_Dra_Angeles_real_v1.mp4'); arg = ap.parse_args()
    orig = AQUI / 'video_0102.mp4'
    # audio recortado solo para alinear palabras
    ff(['-ss', str(T0), '-t', f'{D:.2f}', '-i', str(orig), '-vn', '-ac', '1', '-ar', '16000', str(TMP / 'v.wav')])
    ws = kinetic.palabras(TMP / 'v.wav', arg.texto)
    # Whisper oyó «Ven con nosotros a venir, te estamos esperando»: «a venir» no se entiende, se quita y se mantiene el tiempo de lo demás
    ws = [(w + ',' if w == 'nosotros' else w, a, b) for w, a, b in ws if w.lower().strip('.,¿?') not in ('a', 'venir')]
    print(ws)
    subs = subs_virales.capas(ws, TMP / 'sv', y=0.70, W=W, H=H)
    marca = TMP / 'marca.png'; capa_marca().save(marca)
    # último cuadro (ya girado) para el fondo de la tarjeta
    ff(['-ss', str(T1 - 0.1), '-i', str(orig), '-vf', 'transpose=2,scale=720:1280', '-frames:v', '1', str(TMP / 'ult.png')])
    tj = tarjeta(Image.open(TMP / 'ult.png').filter(ImageFilter.GaussianBlur(14)))
    # cara: ~42 % del ancho, ~25 % del alto → zoom 1.14 hacia ahí
    Z = 1.14; cw, ch = int(W / Z) // 2 * 2, int(H / Z) // 2 * 2; cx = max(0, min(W - cw, int(.46 * W - cw / 2))); cy = 0
    vid = (f"[0:v]transpose=2,crop={cw}:{ch}:{cx}:{cy},scale={W}:{H}:flags=lanczos,hqdn3d=2:2:3:3,"
           f"eq=contrast=1.08:saturation=1.08:gamma=0.95,colorbalance=rs=.05:gs=.01:bs=-.06:rm=.05:bm=-.04:rh=.03:bh=-.03,unsharp=5:5:0.7,"
           f"vignette=PI/4.5,trim=start={T0}:duration={D:.2f},setpts=PTS-STARTPTS,fps=30,format=yuv420p[g];"
           f"[g][1:v]overlay=0:0:enable='between(t,0.2,4.2)'[m]")
    ent, fl, cur = subs_virales.overlay(subs, 'm', 3, D, rise=12)
    # tarjeta: último segundo del video se congela y entra la tarjeta
    fl = vid + ';' + fl
    fl += (f"[{cur}]tpad=stop_mode=clone:stop_duration={TARJ}[b];[2:v]format=rgba,fade=t=in:st=0:d=0.35:alpha=1,setpts=PTS+{D:.2f}/TB[tj];"
           f"[b][tj]overlay=0:0:enable='gte(t,{D:.2f})'[v];")
    total = D + TARJ
    fl += (f"[0:a]atrim=start={T0}:duration={D:.2f},asetpts=PTS-STARTPTS,highpass=f=90,afftdn=nf=-28,acompressor=threshold=-20dB:ratio=3,aresample=44100,apad=whole_dur={total:.2f}[voz];"
           f"[{3 + len(subs)}:a]aresample=44100,volume=0.17,atrim=0:{total:.2f},afade=t=out:st={total - 0.8:.2f}:d=0.8[mu];"
           f"[{4 + len(subs)}:a]aresample=44100,volume=0.6,adelay={int(D * 1000)}|{int(D * 1000)}[wh];"
           f"[voz][mu][wh]amix=inputs=3:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]")
    sal = AQUI / arg.salida
    ff(['-i', str(orig), '-loop', '1', '-framerate', '30', '-t', f'{D:.2f}', '-i', str(marca), '-loop', '1', '-framerate', '30', '-t', f'{TARJ}', '-i', str(tj)] + ent
       + ['-i', str(MUSICA), '-i', str(SFX / 'whoosh.wav'), '-filter_complex', fl, '-map', '[v]', '-map', '[a]', '-t', f'{total:.2f}',
          '-c:v', 'libx264', '-profile:v', 'main', '-pix_fmt', 'yuv420p', '-crf', '20', '-preset', 'slow', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', str(sal)])
    print(sal, sal.stat().st_size // 1024, 'KB')


main()
