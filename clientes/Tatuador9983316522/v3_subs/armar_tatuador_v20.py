"""Adrián v13 (de la v10, que sacó 9/10) con los tres cambios que pidió Glimmer para llegar a 9.5:
  a) la pregunta de filtro aparece también temprano, a los 5.6 s, no solo al final
  b) la ráfaga deja 1.1 s por pieza (6 trabajos) para que se retenga, no 0.30
  c) el WhatsApp queda visible abajo todo el video
Original v10 (5 nov 2026) — versión limpia, hecha de cero para arreglar tres cosas que marcó Carlos:
  1. Los testimonios van en la BURBUJA que generó Codex (PNG con fondo transparente), cayendo una tras otra.
  2. Los subtítulos ya no se cortan: letra más chica, márgenes anchos y salto de línea automático.
  3. Se rehace TODO el audio para quitar los ruidos del final: cada tramo se codifica igual
     (AAC 44.1 kHz estéreo) y se pegan sin volver a comprimir, y el loudnorm se aplica solo a la voz,
     no sobre los silencios (ahí era donde "bombeaba" y sonaba raro).
Salida: clientes/Tatuador9983316522/v3_subs/Adrian_v20_base.mp4
"""
import json, math, pathlib, struct, subprocess, wave

AQUI = pathlib.Path(__file__).resolve().parent
BASE = AQUI.parent / "del_cliente_1104/tatu_b.mp4"
PAL = AQUI.parent / "del_cliente_1104/palabras.json"
TRABAJOS = AQUI.parent / "trabajos_1105"
BURBUJA = AQUI.parent / "tarjetas/burbuja_comentario.png"
FUENTES = pathlib.Path("/workspaces/Nexusv2.0launch18octubre/visionagenciaIAV2.0-main 2/entregables/modelos_modal/fuentes")
W, H, FPS, SR = 720, 1280, 30, 44100
VERDE, ORO = (18, 46, 36), (236, 200, 90)
DUR_T = 1.10            # Glimmer: 1.2 s por pieza retiene más que la ráfaga muy rápida
MAX_PAL, MAX_SEG = 3, 2.2
TESTIMONIOS = [
    ("Miki SA", "Tatúa muy bien, lo mejor de lo mejor.|Lo recomiendo 10/10"),
    ("Víctor Sánchez", "Su trabajo es increíble: rápido,|vibrante y súper profesional"),
    ("Surianne Santana", "Muy bueno"),
    ("L-gan L-gan", "La indicada se encuentra|cuando estás en serio"),
    ("Lucy Benítez", "El mejor"),
    ("Rolando Castro", "Tengo que ir a México|a tatuarme"),
]


def ff(a):
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", *a], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr[-1800:])


def fu(t, peso=700):
    from PIL import ImageFont
    f = ImageFont.truetype(str(FUENTES / "Montserrat.ttf"), t)
    try:
        f.set_variation_by_axes([peso])
    except Exception:
        pass
    return f


def tiempo(s):
    return f"{int(s//3600)}:{int(s%3600//60):02d}:{s%60:05.2f}"


def ass(ruta):
    """Subtítulos en frases cortas. WrapStyle 0 + márgenes anchos = ninguna palabra se corta."""
    pal = json.loads(PAL.read_text())
    grupos, actual = [], []
    for p in pal:
        if actual and (len(actual) >= MAX_PAL or p["f"] - actual[0]["t"] > MAX_SEG
                       or actual[-1]["p"].endswith((".", ",", "?", "!"))):
            grupos.append(actual); actual = []
        actual.append(p)
    if actual:
        grupos.append(actual)
    cab = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Viral,Montserrat,52,&H00FFFFFF,&H00241E12,&H96000000,1,1,4,2,2,90,90,150,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    filas = [f"Dialogue: 0,{tiempo(g[0]['t'])},{tiempo(max(g[-1]['f'], g[0]['t'] + 0.4))},Viral,,0,0,0,,"
             + " ".join(p["p"] for p in g).upper() for g in grupos]
    ruta.write_text(cab + "\n".join(filas) + "\n", encoding="utf-8")


def tarjeta(grande, chico, ruta, y0=120):
    from PIL import Image, ImageDraw
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    f = fu(38, 800); an = d.textlength(grande, font=f) + 76
    alto = 124 if chico else 72
    d.rounded_rectangle(((W - an) / 2, y0, (W + an) / 2, y0 + alto), 34, fill=VERDE + (235,), outline=ORO + (255,), width=3)
    d.text((W / 2, y0 + (38 if chico else 36)), grande, font=f, fill="white", anchor="mm")
    if chico:
        d.text((W / 2, y0 + 86), chico, font=fu(27, 600), fill=ORO, anchor="mm")
    im.save(ruta)


def franja(ruta):
    """Contacto abajo SIN caja (5 nov 2026, Carlos: «el letrero grande sale casi todo el video»).

    Antes era una pastilla con borde dorado que salía los 28 s y pesaba demasiado. Las dos
    referencias que mandó Carlos no usan barras: ponen el texto limpio sobre el video, con sombra
    para que se lea sobre cualquier fondo. Así el contacto sigue presente y deja ver el tatuaje.
    """
    from PIL import Image, ImageDraw
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    t = "WhatsApp 998 331 6522 · escribe CITA"
    f = fu(22, 700)
    for dx, dy in ((0, 2), (2, 0), (0, -2), (-2, 0), (2, 2), (-2, -2), (2, -2), (-2, 2)):
        d.text((W / 2 + dx, H - 52 + dy), t, font=f, fill=(0, 0, 0, 165), anchor="mm")
    d.text((W / 2, H - 52), t, font=f, fill=(255, 255, 255, 238), anchor="mm")
    im.save(ruta)


def filtro_temprano(ruta):
    """La pregunta de filtro, en tarjeta chica, a los 5.6 s (Glimmer: moverla al inicio sube a 9.5)."""
    from PIL import Image, ImageDraw
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    g, c = "¿PEQUEÑO O PROYECTO GRANDE?", "Dime cuál y te paso precio y fecha"
    f = fu(32, 800); an = d.textlength(g, font=f) + 70
    d.rounded_rectangle(((W - an) / 2, 980, (W + an) / 2, 1086), 30, fill=VERDE + (238,), outline=ORO + (255,), width=3)
    d.text((W / 2, 1014), g, font=f, fill="white", anchor="mm")
    d.text((W / 2, 1060), c, font=fu(24, 600), fill=ORO, anchor="mm")
    im.save(ruta)


def tapa(ruta):
    from PIL import Image, ImageDraw
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 352), fill=(10, 14, 12, 242))
    t = "ADRIÁN SANTANA · CANCÚN CENTRO"
    f = fu(34, 800); an = d.textlength(t, font=f) + 70
    d.rounded_rectangle(((W - an) / 2, 150, (W + an) / 2, 222), 34, fill=VERDE + (242,), outline=ORO + (255,), width=3)
    d.text((W / 2, 186), t, font=f, fill="white", anchor="mm")
    d.text((W / 2, 280), "Escríbeme la palabra CITA por WhatsApp", font=fu(28, 600), fill=ORO, anchor="mm")
    im.save(ruta)


def burbuja(nombre, texto, ruta):
    """Notificación flotante, como la referencia que mandó Carlos (reel DfJYUfRx-eo).

    Antes eran tarjetas blancas de reseña, grandes y apretadas. La referencia usa una pastilla
    oscura translúcida, baja y compacta, como las notificaciones del celular: se lee de un vistazo
    y no tapa el video.
    """
    from PIL import Image, ImageDraw
    AN, AL = 560, 92
    b = Image.new("RGBA", (AN, AL + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(b)
    d.rounded_rectangle((6, 12, AN - 2, AL + 12), 26, fill=(0, 0, 0, 80))      # sombra
    d.rounded_rectangle((0, 6, AN - 8, AL + 6), 26, fill=(26, 28, 30, 234))    # pastilla
    cy = (AL + 12) / 2
    cx, r = 46, 23
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(18, 46, 36, 255))
    d.text((cx, cy), nombre[0], font=fu(23, 900), fill="white", anchor="mm")
    d.text((82, cy - 19), nombre, font=fu(21, 800), fill=(255, 255, 255, 246), anchor="lm")
    d.text((82, cy + 15), texto.replace("|", " "), font=fu(18, 500), fill=(203, 207, 211, 236), anchor="lm")
    d.text((AN - 28, cy - 19), "ahora", font=fu(14, 500), fill=(148, 152, 156, 215), anchor="rm")
    b.save(ruta)


GOLPE = AQUI.parent / "audio_rafaga/golpe_carlos.wav"


def golpes_de_carlos(n, dur, ruta):
    """Pone el golpe que mandó Carlos en cada cambio de foto de la ráfaga.

    Antes eran clics sintéticos. Carlos mandó el sonido que quiere por WhatsApp (0.84 s), así
    que se usa ese tal cual, copiado en cada corte. Si el archivo no estuviera, se cae a los
    clics de antes para no dejar la ráfaga muda.
    """
    if not GOLPE.exists():
        return clics(n, ruta)
    with wave.open(str(GOLPE), "rb") as g:
        sr_g = g.getframerate()
        crudo = g.readframes(g.getnframes())
        muestras = list(struct.unpack("<%dh" % (len(crudo) // 2), crudo))
    if sr_g != SR:  # remuestreo simple, suficiente para un golpe corto
        paso = sr_g / SR
        muestras = [muestras[min(len(muestras) - 1, int(i * paso))] for i in range(int(len(muestras) / paso))]
    total = n * dur + 0.4
    m = [0.0] * int(total * SR)
    for k in range(n):
        i0 = int(k * dur * SR)
        for j, v in enumerate(muestras):
            if i0 + j < len(m):
                m[i0 + j] += v / 32768
    pico = max(abs(x) for x in m) or 1
    m = [x / pico * 0.92 for x in m]
    with wave.open(str(ruta), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, c)) * 32767)) for c in m))


def clics(n, ruta, extra=0.2):
    total = n * DUR_T + extra
    m = [0.0] * int(total * SR)
    for k in range(n):
        i0 = int(k * DUR_T * SR)
        for j in range(int(0.035 * SR)):
            if i0 + j < len(m):
                m[i0 + j] += 0.5 * math.exp(-j / (0.006 * SR)) * math.sin(2 * math.pi * 2000 * j / SR)
    with wave.open(str(ruta), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, c)) * 32767)) for c in m))


VID = ["-c:v", "libx264", "-profile:v", "main", "-crf", "20", "-preset", "medium",
       "-pix_fmt", "yuv420p", "-r", str(FPS), "-video_track_timescale", "15360"]
AUD = ["-c:a", "aac", "-b:a", "128k", "-ar", str(SR), "-ac", "2"]


def main():
    tmp = AQUI / "tmp_v20"; tmp.mkdir(exist_ok=True)
    a = tmp / "subs.ass"; ass(a)
    t1, t2, tp = tmp / "c1.png", tmp / "c2.png", tmp / "tapa.png"
    tarjeta("ADRIÁN SANTANA", "Tatuador en Cancún Centro", t1)
    tarjeta("FRENTE AL PALACIO MUNICIPAL", "Av. Azucenas · Cancún Centro", t2)
    tapa(tp)
    fr = tmp / "franja.png"; franja(fr)
    fe = tmp / "filtro_temprano.png"; filtro_temprano(fe)

    # --- cuerpo: subtítulos + tarjetas + tapa + testimonios cayendo ---
    entradas = ["-i", str(BASE), "-i", str(t1), "-i", str(t2), "-i", str(tp), "-i", str(fr), "-i", str(fe)]
    cad = (f"[0:v]eq=contrast=1.06:saturation=1.08,subtitles='{a}':fontsdir='{FUENTES}'[v0];"
           "[v0][1:v]overlay=0:0:enable='between(t,3.4,7.0)'[v1];"   # tarjeta de nombre, después del gancho
           "[v1][2:v]overlay=0:0:enable='between(t,6.6,10.6)'[v2];"
           "[v2][3:v]overlay=0:0:enable='gte(t,14.6)'[v3];"
           "[v3][4:v]overlay=0:0[v4];"                                   # franja de WhatsApp todo el video
           "[v4][5:v]overlay=0:0:enable='between(t,5.6,5.6)'[v5]")     # 5 nov: desactivada. La pregunta
    # de tamaño ahora va en capa justo antes de la ráfaga (Glimmer), y salía dos veces.
    prev = "v5"
    for i, (nombre, texto) in enumerate(TESTIMONIOS):
        p = tmp / f"b{i}.png"; burbuja(nombre, texto, p)
        entradas += ["-i", str(p)]
        # 5 nov 2026, Carlos: «se ve muy saturado el inicio, primero el gancho textual y luego
        # los testimonios, que no se sobrepongan». Antes empezaban a caer en el segundo 1 y
        # chocaban con el gancho. Ahora arrancan en 3.4, cuando el gancho ya salió de cuadro.
        t0 = 3.4 + i * 0.40
        yf = 150 + i * 112
        x = 80 if i % 2 == 0 else 96
        y = f"if(lt(t,{t0}),-220,min({yf},-220+(t-{t0})*{(yf+220)/0.40:.0f}))"
        sal = f"t{i}"
        cad += f";[{prev}][{i+6}:v]overlay=x={x}:y='{y}':enable='between(t,{t0},8.6)'[{sal}]"
        prev = sal
    cuerpo = tmp / "cuerpo.mp4"
    ff(entradas + ["-filter_complex", cad, "-map", f"[{prev}]", "-map", "0:a",
                   "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", *VID, *AUD, str(cuerpo)])

    # --- ráfaga de trabajos terminados ---
    # 5 nov 2026, Carlos: «pon todos sus trabajos». Son 13; a 1.10 s cada uno la ráfaga duraría
    # 14 s, demasiado, así que se acorta el tiempo por pieza. 0.70 s sigue dejando ver el tatuaje
    # y mantiene el golpe de sonido marcando cada cambio.
    fotos = sorted(TRABAJOS.glob("*.jpg"))
    DUR_R = 0.70 if len(fotos) > 8 else DUR_T
    partes = []
    n = int(DUR_R * FPS) + 1
    for i, f in enumerate(fotos):
        p = tmp / f"r{i}.mp4"
        z = "min(zoom+0.0018,1.12)" if i % 2 == 0 else "if(eq(on,1),1.12,max(zoom-0.0018,1))"
        ff(["-loop", "1", "-i", str(f), "-vf",
            f"scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2},"
            f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps={FPS},setsar=1",
            "-frames:v", str(n), "-an", "-c:v", "libx264", "-crf", "19", "-pix_fmt", "yuv420p", str(p)])
        partes.append(p)
    (tmp / "lista.txt").write_text("".join(f"file '{p}'\n" for p in partes))
    muda = tmp / "muda.mp4"
    ff(["-f", "concat", "-safe", "0", "-i", str(tmp / "lista.txt"), "-c", "copy", str(muda)])
    tr = tmp / "tr.png"; tarjeta("TRABAJOS DE ADRIÁN", "", tr)
    # el golpe que mandó Carlos por WhatsApp, repetido en cada cambio de foto
    cl = tmp / "golpes.wav"; golpes_de_carlos(len(fotos), DUR_R, cl)
    rafaga = tmp / "rafaga.mp4"
    ff(["-i", str(muda), "-i", str(tr), "-i", str(cl), "-filter_complex",
        "[0:v][1:v]overlay=0:0,format=yuv420p[v];[2:a]aformat=channel_layouts=stereo,volume=0.9[a]",
        "-map", "[v]", "-map", "[a]", *VID, *AUD, "-shortest", str(rafaga)])

    # --- filtro y cierre, con silencio limpio del mismo formato ---
    from PIL import Image, ImageDraw
    fi = tmp / "filtro.png"
    im = Image.new("RGB", (W, H), (12, 16, 14)); d = ImageDraw.Draw(im)
    d.text((W / 2, 470), "¿TATUAJE PEQUEÑO", font=fu(56, 900), fill="white", anchor="mm")
    d.text((W / 2, 540), "O PROYECTO GRANDE?", font=fu(56, 900), fill="white", anchor="mm")
    d.text((W / 2, 640), "Dime cuál y te paso precio y fecha", font=fu(32, 600), fill=ORO, anchor="mm")
    im.save(fi)
    ci = tmp / "cierre.png"
    im = Image.new("RGB", (W, H), (10, 14, 12)); d = ImageDraw.Draw(im)
    d.text((W / 2, 430), "ESCRÍBEME", font=fu(66, 900), fill="white", anchor="mm")
    d.text((W / 2, 505), "LA PALABRA «CITA»", font=fu(52, 900), fill=ORO, anchor="mm")
    d.text((W / 2, 585), "y te mando la disponibilidad", font=fu(32, 600), fill="white", anchor="mm")
    d.text((W / 2, 627), "de esta semana", font=fu(32, 600), fill="white", anchor="mm")
    d.text((W / 2, 700), "Adrián Santana · Cancún Centro", font=fu(28, 600), fill=ORO, anchor="mm")
    an = 400
    d.rounded_rectangle(((W - an) / 2, 760, (W + an) / 2, 846), 43, fill=(37, 211, 102))
    d.ellipse(((W - an) / 2 + 28, 782, (W - an) / 2 + 70, 824), fill="white")
    d.text((W / 2 + 32, 803), "Enviar WhatsApp", font=fu(34, 800), fill=(10, 40, 24), anchor="mm")
    im.save(ci)
    finales = []
    for nombre, png, dur in (("filtro", fi, 1.8), ("cierre", ci, 3.0)):
        p = tmp / f"{nombre}.mp4"
        ff(["-loop", "1", "-i", str(png), "-f", "lavfi", "-i", f"anullsrc=r={SR}:cl=stereo",
            "-t", str(dur), "-vf", f"fps={FPS},setsar=1", *VID, *AUD, "-shortest", str(p)])
        finales.append(p)

    (tmp / "final.txt").write_text("".join(f"file '{p}'\n" for p in [cuerpo, rafaga] + finales))
    salida = AQUI / "Adrian_v20_base.mp4"
    ff(["-f", "concat", "-safe", "0", "-i", str(tmp / "final.txt"), "-c", "copy",
        "-movflags", "+faststart", str(salida)])
    print("listo", salida)


if __name__ == "__main__":
    main()
