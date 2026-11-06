"""Adrián (tatuador) v4: aplica las sugerencias de Glimmer sobre la v3 (que calificó 5/10 → 9/10).
Cambios:
  1. Subtítulos en FRASES de 2 a 4 palabras, no palabra suelta: Glimmer dijo que el texto salía
     fragmentado («¿BUSCAS», «MUNICIPAL») y que eso baja claridad y calidad visual.
  2. Cierre nuevo de 3 s con el CTA concreto que pidió: «Escríbeme CITA y te mando la disponibilidad
     de esta semana» (lo que más sube: oferta y mensajes calificados).
  3. Se conservan las tarjetas de nombre y ubicación, color y audio normalizado de la v3.
Falta para el 9: los testimonios reales que debe mandar él (prueba social).
Salida: clientes/Tatuador9983316522/v3_subs/Adrian_v4_cta.mp4
"""
import json
import pathlib
import subprocess

AQUI = pathlib.Path(__file__).resolve().parent
ORIG = AQUI.parent / "del_cliente_1104/tatu_b.mp4"
PAL = AQUI.parent / "del_cliente_1104/palabras.json"
FUENTES = pathlib.Path("/workspaces/Nexusv2.0launch18octubre/visionagenciaIAV2.0-main 2/entregables/modelos_modal/fuentes")
W, H = 720, 1280
VERDE, ORO = (18, 46, 36), (236, 200, 90)
MAX_PAL, MAX_SEG = 3, 2.2      # frases de hasta 3 palabras o 2.2 s


def ff(a):
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", *a], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr[-1500:])


def fu(t, peso=900):
    from PIL import ImageFont
    f = ImageFont.truetype(str(FUENTES / "Montserrat.ttf"), t)
    try:
        f.set_variation_by_axes([peso])
    except Exception:
        pass
    return f


def tiempo(s):
    return f"{int(s//3600)}:{int(s%3600//60):02d}:{s%60:05.2f}"


def frases(palabras):
    """Agrupa palabras en frases cortas para que se lean completas."""
    out, actual = [], []
    for p in palabras:
        if actual and (len(actual) >= MAX_PAL or p["f"] - actual[0]["t"] > MAX_SEG
                       or actual[-1]["p"].endswith((".", ",", "?", "!"))):
            out.append(actual); actual = []
        actual.append(p)
    if actual:
        out.append(actual)
    return out


def ass(palabras, ruta):
    cab = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Viral,Montserrat,58,&H00FFFFFF,&H00241E12,&H96000000,1,1,5,2,2,60,60,165,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    filas = []
    for g in frases(palabras):
        ini, fin = g[0]["t"], max(g[-1]["f"], g[0]["t"] + 0.4)
        texto = " ".join(p["p"] for p in g).upper()
        filas.append(f"Dialogue: 0,{tiempo(ini)},{tiempo(fin)},Viral,,0,0,0,,{texto}")
    ruta.write_text(cab + "\n".join(filas) + "\n", encoding="utf-8")


def tarjeta(grande, chico, ruta, y0=120):
    from PIL import Image, ImageDraw
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    f = fu(38, 800)
    an = d.textlength(grande, font=f) + 76
    x0 = (W - an) / 2
    alto = 124 if chico else 72
    d.rounded_rectangle((x0, y0, x0 + an, y0 + alto), 34, fill=VERDE + (235,), outline=ORO + (255,), width=3)
    d.text((W / 2, y0 + (38 if chico else 36)), grande, font=f, fill="white", anchor="mm")
    if chico:
        d.text((W / 2, y0 + 86), chico, font=fu(27, 600), fill=ORO, anchor="mm")
    im.save(ruta)


def cierre(ruta):
    from PIL import Image, ImageDraw
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, H), fill=(10, 14, 12, 180))
    d.text((W / 2, H / 2 - 150), "ESCRÍBEME", font=fu(66, 900), fill="white", anchor="mm")
    d.text((W / 2, H / 2 - 76), "LA PALABRA «CITA»", font=fu(52, 900), fill=ORO, anchor="mm")
    d.text((W / 2, H / 2 - 6), "y te mando la disponibilidad", font=fu(32, 600), fill="white", anchor="mm")
    d.text((W / 2, H / 2 + 36), "de esta semana", font=fu(32, 600), fill="white", anchor="mm")
    d.text((W / 2, H / 2 + 104), "Adrián Santana · Cancún Centro", font=fu(28, 600), fill=ORO, anchor="mm")
    an = 400
    d.rounded_rectangle(((W - an) / 2, H / 2 + 150, (W + an) / 2, H / 2 + 236), 43, fill=(37, 211, 102, 255))
    d.ellipse(((W - an) / 2 + 28, H / 2 + 172, (W - an) / 2 + 70, H / 2 + 214), fill="white")
    d.text((W / 2 + 32, H / 2 + 193), "Enviar WhatsApp", font=fu(34, 800), fill=(10, 40, 24), anchor="mm")
    im.save(ruta)


def main():
    tmp = AQUI / "tmp_v4"; tmp.mkdir(exist_ok=True)
    palabras = json.loads(PAL.read_text())
    a = tmp / "subs.ass"; ass(palabras, a)
    t1, t2, tc = tmp / "c1.png", tmp / "c2.png", tmp / "cierre.png"
    tarjeta("ADRIÁN SANTANA", "Tatuador en Cancún Centro", t1)
    tarjeta("FRENTE AL PALACIO MUNICIPAL", "Av. Azucenas · Cancún Centro", t2)
    cierre(tc)

    cuerpo = tmp / "cuerpo.mp4"
    filtro = ("[0:v]eq=contrast=1.06:saturation=1.08,"
              f"subtitles='{a}':fontsdir='{FUENTES}'[v0];"
              "[v0][1:v]overlay=0:0:enable='between(t,0.3,4.5)'[v1];"
              "[v1][2:v]overlay=0:0:enable='between(t,6.6,10.6)'[v]")
    ff(["-i", str(ORIG), "-i", str(t1), "-i", str(t2), "-filter_complex", filtro,
        "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-crf", "20", "-preset", "medium",
        "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-b:a", "128k", str(cuerpo)])

    ultimo = tmp / "ultimo.png"
    ff(["-sseof", "-0.2", "-i", str(cuerpo), "-frames:v", "1", str(ultimo)])
    fin = tmp / "cierre.mp4"
    ff(["-loop", "1", "-i", str(ultimo), "-i", str(tc), "-filter_complex",
        "[0:v]scale=720:1280,fps=30,setsar=1[a];[a][1:v]overlay=0:0,format=yuv420p",
        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", "3",
        "-c:v", "libx264", "-crf", "20", "-c:a", "aac", "-b:a", "128k", "-shortest", str(fin)])

    (tmp / "lista.txt").write_text(f"file '{cuerpo}'\nfile '{fin}'\n")
    salida = AQUI / "Adrian_v4_cta.mp4"
    ff(["-f", "concat", "-safe", "0", "-i", str(tmp / "lista.txt"),
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
        "-c:v", "libx264", "-profile:v", "main", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(salida)])
    print("listo", salida)


if __name__ == "__main__":
    main()
