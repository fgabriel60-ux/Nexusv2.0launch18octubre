"""Adrián (tatuador) v3: el video que él mismo grabó, llevado a calificación 8 sin volver a grabar.
Lo que se le hace (plan de Glimmer del 4 nov, que lo calificó 3/10 → 8/10 proyectada):
  · subtítulos palabra por palabra con los tiempos REALES de Whisper (word timestamps)
  · tarjeta de nombre 0.3-4.5 s y tarjeta de ubicación 6.6-10.6 s, en capa aparte
  · color un poco más contrastado y audio normalizado (loudnorm)
No se corta ni se reordena nada: la voz va continua y cortar la desincroniza.
Salida: clientes/Tatuador9983316522/v3_subs/Adrian_v3_subs.mp4
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


def ff(args):
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", *args], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr[-2000:])


def tiempo(s):
    h = int(s // 3600); m = int(s % 3600 // 60); seg = s % 60
    return f"{h}:{m:02d}:{seg:05.2f}"


def ass(palabras, ruta):
    """Una línea por palabra, como los subtítulos virales: entra y sale con la voz."""
    cab = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Viral,Montserrat,66,&H00FFFFFF,&H00241E12,&H96000000,1,1,5,2,2,40,40,170,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    filas = []
    for p in palabras:
        ini, fin = p["t"], max(p["f"], p["t"] + 0.12)
        texto = p["p"].replace("\n", " ").upper()
        filas.append(f"Dialogue: 0,{tiempo(ini)},{tiempo(fin)},Viral,,0,0,0,,{texto}")
    ruta.write_text(cab + "\n".join(filas) + "\n", encoding="utf-8")


def tarjeta(grande, chico, ruta, arriba=True):
    from PIL import Image, ImageDraw, ImageFont
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    def fu(t, peso=900):
        f = ImageFont.truetype(str(FUENTES / "Montserrat.ttf"), t)
        try:
            f.set_variation_by_axes([peso])
        except Exception:
            pass
        return f

    y0 = 120 if arriba else 980
    f = fu(38, 800)
    an = d.textlength(grande, font=f) + 76
    x0 = (W - an) / 2
    alto = 124 if chico else 70
    d.rounded_rectangle((x0, y0, x0 + an, y0 + alto), 34, fill=VERDE + (235,), outline=ORO + (255,), width=3)
    d.text((W / 2, y0 + (38 if chico else 35)), grande, font=f, fill="white", anchor="mm")
    if chico:
        fc = fu(27, 600)
        d.text((W / 2, y0 + 86), chico, font=fc, fill=ORO, anchor="mm")
    im.save(ruta)


def main():
    palabras = json.loads(PAL.read_text())
    a = AQUI / "subs.ass"
    ass(palabras, a)
    t1, t2 = AQUI / "tarjeta_nombre.png", AQUI / "tarjeta_lugar.png"
    tarjeta("ADRIÁN SANTANA", "Tatuador en Cancún Centro", t1)
    tarjeta("FRENTE AL PALACIO MUNICIPAL", "Av. Azucenas · Cancún Centro", t2)
    salida = AQUI / "Adrian_v3_subs.mp4"
    filtro = (
        "[0:v]eq=contrast=1.06:saturation=1.08,"
        f"subtitles='{a}':fontsdir='{FUENTES}'[v0];"
        "[v0][1:v]overlay=0:0:enable='between(t,0.3,4.5)'[v1];"
        "[v1][2:v]overlay=0:0:enable='between(t,6.6,10.6)'[v]"
    )
    ff(["-i", str(ORIG), "-i", str(t1), "-i", str(t2), "-filter_complex", filtro,
        "-map", "[v]", "-map", "0:a", "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
        "-c:v", "libx264", "-profile:v", "main", "-crf", "20", "-preset", "medium",
        "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart", str(salida)])
    print("listo", salida)


if __name__ == "__main__":
    main()
