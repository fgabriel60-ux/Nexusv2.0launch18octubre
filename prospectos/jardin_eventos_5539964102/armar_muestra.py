"""Muestra para el prospecto Homau (jardín de eventos + food garden), 4 nov 2026.
Carlos autorizó hacer muestras de video a prospectos para cerrarlos.
Qué se le hace a SU video de 51 s (Glimmer lo calificó 4/10 → 8.5 proyectada):
  · se recorta a lo que vende: espacio y capacidad, área infantil, comida y cierre
  · se sube a 720x1280 con color y nitidez, y se nivela el audio
  · subtítulos limpios palabra por palabra (tiempos reales de Whisper) en vez de los de colores
  · tarjetas con SUS datos reales: nombre, capacidad, área infantil, comida
  · cierre con llamado a WhatsApp
No se inventa ciudad, precio ni promoción: no los dio.
"""
import json, pathlib, subprocess

AQUI = pathlib.Path(__file__).resolve().parent
ORIG = AQUI / "jardin_original.mp4"
FUENTES = pathlib.Path("/workspaces/Nexusv2.0launch18octubre/visionagenciaIAV2.0-main 2/entregables/modelos_modal/fuentes")
W, H, FPS = 720, 1280, 30
VERDE, ORO = (18, 46, 36), (236, 200, 90)
TRAMOS = [(5.15, 17.60), (17.60, 21.80), (26.05, 31.10), (43.40, 47.80)]


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
    """Tarjeta final de WhatsApp sobre el último cuadro."""
    from PIL import Image, ImageDraw
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, H), fill=(8, 14, 12, 170))
    d.text((W / 2, H / 2 - 120), "APARTA TU FECHA", font=fu(62, 900), fill="white", anchor="mm")
    d.text((W / 2, H / 2 - 52), "POR WHATSAPP", font=fu(62, 900), fill="white", anchor="mm")
    d.text((W / 2, H / 2 + 24), "Zona techada · hasta 50 personas", font=fu(30, 600), fill=ORO, anchor="mm")
    d.text((W / 2, H / 2 + 68), "Área infantil · taquiza o trae tu comida", font=fu(30, 600), fill=ORO, anchor="mm")
    an = 420
    d.rounded_rectangle(((W - an) / 2, H / 2 + 130, (W + an) / 2, H / 2 + 216), 43, fill=(37, 211, 102, 255))
    d.ellipse(((W - an) / 2 + 28, H / 2 + 152, (W - an) / 2 + 70, H / 2 + 194), fill="white")
    d.text((W / 2 + 36, H / 2 + 173), "Enviar WhatsApp", font=fu(36, 800), fill=(10, 40, 24), anchor="mm")
    im.save(ruta)


def tiempo(s):
    return f"{int(s//3600)}:{int(s%3600//60):02d}:{s%60:05.2f}"


def main():
    tmp = AQUI / "tmp"; tmp.mkdir(exist_ok=True)
    partes, mapa, acum = [], [], 0.0
    for i, (a, b) in enumerate(TRAMOS):
        p = tmp / f"t{i}.mp4"
        ff(["-ss", f"{a}", "-i", str(ORIG), "-t", f"{b-a:.3f}",
            "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                   f"eq=contrast=1.1:saturation=1.12:brightness=0.03,unsharp=5:5:0.6,fps={FPS},setsar=1",
            "-c:v", "libx264", "-crf", "19", "-c:a", "aac", "-b:a", "128k", str(p)])
        partes.append(p); mapa.append((a, b, acum)); acum += (b - a)
    (tmp / "lista.txt").write_text("".join(f"file '{p}'\n" for p in partes))
    base = tmp / "base.mp4"
    ff(["-f", "concat", "-safe", "0", "-i", str(tmp / "lista.txt"), "-c", "copy", str(base)])

    # subtítulos: se remapean los tiempos de las palabras a la nueva línea de tiempo
    pal = json.loads((AQUI / "palabras.json").read_text())
    filas = []
    for p in pal:
        for a, b, off in mapa:
            if p["t"] >= a - 0.05 and p["f"] <= b + 0.25:
                ini = p["t"] - a + off; fin = max(p["f"] - a + off, ini + 0.12)
                filas.append(f"Dialogue: 0,{tiempo(ini)},{tiempo(fin)},Viral,,0,0,0,,{p['p'].upper()}")
                break
    cab = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Viral,Montserrat,64,&H00FFFFFF,&H00241E12,&H96000000,1,1,5,2,2,40,40,180,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    subs = AQUI / "subs.ass"; subs.write_text(cab + "\n".join(filas) + "\n", encoding="utf-8")

    t1, t2, t3 = tmp / "c1.png", tmp / "c2.png", tmp / "c3.png"
    tarjeta("HOMAU · JARDÍN DE EVENTOS", "Zona techada para hasta 50 personas", t1)
    tarjeta("ÁREA INFANTIL AL LADO", "", t2)
    tarjeta("TACOS · COCHINITA · CREPAS", "Parrillada y taquiza, o trae tu comida", t3)
    tc = tmp / "cierre.png"; cierre(tc)

    # cierre: último cuadro congelado 3 s con la tarjeta de WhatsApp
    ultimo = tmp / "ultimo.png"
    ff(["-sseof", "-0.2", "-i", str(base), "-frames:v", "1", str(ultimo)])
    congelado = tmp / "cierre.mp4"
    ff(["-loop", "1", "-i", str(ultimo), "-i", str(tc), "-filter_complex",
        "[0:v]scale=720:1280,fps=30,setsar=1[a];[a][1:v]overlay=0:0,format=yuv420p",
        "-t", "3", "-c:v", "libx264", "-crf", "19", str(congelado)])

    b1, b2 = acum, acum  # tiempos de las tarjetas sobre la base
    filtro = (f"[0:v]subtitles='{subs}':fontsdir='{FUENTES}'[v0];"
              f"[v0][1:v]overlay=0:0:enable='between(t,0.3,4.5)'[v1];"
              f"[v1][2:v]overlay=0:0:enable='between(t,{12.45:.2f},{16.0:.2f})'[v2];"
              f"[v2][3:v]overlay=0:0:enable='between(t,{16.6:.2f},{21.0:.2f})'[v]")
    conSubs = tmp / "con_subs.mp4"
    ff(["-i", str(base), "-i", str(t1), "-i", str(t2), "-i", str(t3),
        "-filter_complex", filtro, "-map", "[v]", "-map", "0:a",
        "-c:v", "libx264", "-crf", "19", "-c:a", "aac", "-b:a", "128k", str(conSubs)])

    (tmp / "final.txt").write_text(f"file '{conSubs}'\nfile '{congelado}'\n")
    salida = AQUI / "Homau_muestra_v1.mp4"
    ff(["-f", "concat", "-safe", "0", "-i", str(tmp / "final.txt"),
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
        "-c:v", "libx264", "-profile:v", "main", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(salida)])
    print("listo", salida)


if __name__ == "__main__":
    main()
