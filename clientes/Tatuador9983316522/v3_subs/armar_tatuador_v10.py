"""Adrián v10 (5 nov 2026) — versión limpia, hecha de cero para arreglar tres cosas que marcó Carlos:
  1. Los testimonios van en la BURBUJA que generó Codex (PNG con fondo transparente), cayendo una tras otra.
  2. Los subtítulos ya no se cortan: letra más chica, márgenes anchos y salto de línea automático.
  3. Se rehace TODO el audio para quitar los ruidos del final: cada tramo se codifica igual
     (AAC 44.1 kHz estéreo) y se pegan sin volver a comprimir, y el loudnorm se aplica solo a la voz,
     no sobre los silencios (ahí era donde "bombeaba" y sonaba raro).
Salida: clientes/Tatuador9983316522/v3_subs/Adrian_v10.mp4
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
DUR_T = 0.30            # cada trabajo en la ráfaga
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
    """Usa la tarjeta transparente que hizo Codex y le escribe encima el comentario real."""
    from PIL import Image, ImageDraw
    b = Image.open(BURBUJA).convert("RGBA")
    b = b.resize((560, int(b.height * 560 / b.width)), Image.LANCZOS)
    d = ImageDraw.Draw(b)
    cx, cy, r = 61, b.height / 2, 24
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(18, 46, 36, 255))
    d.text((cx, cy), nombre[0], font=fu(24, 900), fill="white", anchor="mm")
    d.text((104, b.height / 2 - 34), nombre, font=fu(20, 800), fill=(22, 30, 26))
    d.text((b.width - 24, b.height / 2 - 34), "★★★★★", font=fu(16, 700), fill=(228, 170, 40), anchor="ra")
    y = b.height / 2 - 6
    for ln in texto.split("|"):
        d.text((104, y), ln, font=fu(19, 500), fill=(44, 50, 46))
        y += 24
    b.save(ruta)


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
    tmp = AQUI / "tmp_v10"; tmp.mkdir(exist_ok=True)
    a = tmp / "subs.ass"; ass(a)
    t1, t2, tp = tmp / "c1.png", tmp / "c2.png", tmp / "tapa.png"
    tarjeta("ADRIÁN SANTANA", "Tatuador en Cancún Centro", t1)
    tarjeta("FRENTE AL PALACIO MUNICIPAL", "Av. Azucenas · Cancún Centro", t2)
    tapa(tp)

    # --- cuerpo: subtítulos + tarjetas + tapa + testimonios cayendo ---
    entradas = ["-i", str(BASE), "-i", str(t1), "-i", str(t2), "-i", str(tp)]
    cad = (f"[0:v]eq=contrast=1.06:saturation=1.08,subtitles='{a}':fontsdir='{FUENTES}'[v0];"
           "[v0][1:v]overlay=0:0:enable='between(t,0.3,4.5)'[v1];"
           "[v1][2:v]overlay=0:0:enable='between(t,6.6,10.6)'[v2];"
           "[v2][3:v]overlay=0:0:enable='gte(t,14.6)'[v3]")
    prev = "v3"
    for i, (nombre, texto) in enumerate(TESTIMONIOS):
        p = tmp / f"b{i}.png"; burbuja(nombre, texto, p)
        entradas += ["-i", str(p)]
        t0 = 1.0 + i * 0.40
        yf = 150 + i * 112
        x = 80 if i % 2 == 0 else 96
        y = f"if(lt(t,{t0}),-220,min({yf},-220+(t-{t0})*{(yf+220)/0.40:.0f}))"
        sal = f"t{i}"
        cad += f";[{prev}][{i+4}:v]overlay=x={x}:y='{y}':enable='between(t,{t0},5.9)'[{sal}]"
        prev = sal
    cuerpo = tmp / "cuerpo.mp4"
    ff(entradas + ["-filter_complex", cad, "-map", f"[{prev}]", "-map", "0:a",
                   "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", *VID, *AUD, str(cuerpo)])

    # --- ráfaga de trabajos terminados ---
    fotos = sorted(TRABAJOS.glob("*.jpg"))[:10]
    partes = []
    n = int(DUR_T * FPS) + 1
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
    cl = tmp / "clics.wav"; clics(len(fotos), cl)
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
    salida = AQUI / "Adrian_v10.mp4"
    ff(["-f", "concat", "-safe", "0", "-i", str(tmp / "final.txt"), "-c", "copy",
        "-movflags", "+faststart", str(salida)])
    print("listo", salida)


if __name__ == "__main__":
    main()
