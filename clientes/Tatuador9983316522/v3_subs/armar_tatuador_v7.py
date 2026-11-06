"""Adrián v7 (5 nov 2026): los TESTIMONIOS reales entran CAYENDO sobre el plano del sillón del gancho,
uno tras otro, para que se vea que son muchos (idea de Carlos, inspirada en el reel que mandó).
Los textos son textuales de los comentarios de su publicación de Facebook (412 reacciones, 26 compartidos).
Lo demás queda igual que la v6: ráfaga con sus 10 trabajos + clics, pregunta de filtro y cierre.
Salida: clientes/Tatuador9983316522/v3_subs/Adrian_v7_testimonios.mp4
"""
import pathlib
import subprocess

AQUI = pathlib.Path(__file__).resolve().parent
V6 = AQUI / "Adrian_v6_trabajos.mp4"
FUENTES = pathlib.Path("/workspaces/Nexusv2.0launch18octubre/visionagenciaIAV2.0-main 2/entregables/modelos_modal/fuentes")
W, H = 720, 1280

# (nombre, texto) — textual de los comentarios de su publicación
TESTIMONIOS = [
    ("Miki SA", "Tatúa muy bien, lo mejor de lo mejor.\nLo recomiendo 10/10, ya me a echo varios"),
    ("Víctor Sánchez", "Su trabajo es increíble: rápido,\nvibrante y súper profesional"),
    ("Surianne Santana", "Muy bueno 🥰"),
    ("L-gan L-gan", "Bro, la indicada se encuentra\ncuando estás en serio"),
    ("Lucy Benítez", "El mejor"),
    ("Rolando Castro", "Definitivamente tengo que ir\na México a tatuarme"),
]
T0, PASO, CAIDA = 1.1, 0.42, 0.42     # cuándo empieza, cada cuánto cae otro, cuánto tarda en caer


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


def tarjeta(nombre, texto, ruta):
    """Tarjeta tipo comentario: fondo claro, nombre en negritas, texto, estrellas."""
    from PIL import Image, ImageDraw
    an, al = 560, 128 if "\n" in texto else 104
    im = Image.new("RGBA", (an, al), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, an - 1, al - 1), 26, fill=(252, 252, 250, 246), outline=(236, 200, 90, 255), width=2)
    d.ellipse((16, al / 2 - 22, 60, al / 2 + 22), fill=(18, 46, 36, 255))
    d.text((38, al / 2), nombre[0], font=fu(24, 900), fill="white", anchor="mm")
    d.text((76, 22), nombre, font=fu(21, 800), fill=(22, 30, 26))
    d.text((an - 22, 22), "★★★★★", font=fu(17, 700), fill=(228, 170, 40), anchor="ra")
    y = 50
    for ln in texto.split("\n"):
        d.text((76, y), ln, font=fu(21, 500), fill=(40, 46, 42))
        y += 28
    im.save(ruta)


def main():
    tmp = AQUI / "tmp_v7"; tmp.mkdir(exist_ok=True)
    entradas, filtros, prev = ["-i", str(V6)], [], "0:v"
    for i, (nombre, texto) in enumerate(TESTIMONIOS):
        p = tmp / f"t{i}.png"; tarjeta(nombre, texto, p)
        entradas += ["-i", str(p)]
        t0 = T0 + i * PASO
        yf = 150 + i * 118                     # se van apilando hacia abajo
        x = 80 if i % 2 == 0 else 100
        # cae desde arriba y se queda; se va al terminar el plano del sillón
        y = f"if(lt(t,{t0}),-200,min({yf},-200+( t-{t0})*{(yf+200)/CAIDA:.0f}))"
        sal = f"v{i}"
        filtros.append(f"[{prev}][{i+1}:v]overlay=x={x}:y='{y}':enable='between(t,{t0},5.75)'[{sal}]")
        prev = sal
    salida = AQUI / "Adrian_v7_testimonios.mp4"
    ff(entradas + ["-filter_complex", ";".join(filtros), "-map", f"[{prev}]", "-map", "0:a",
                   "-c:v", "libx264", "-profile:v", "main", "-crf", "20", "-preset", "medium",
                   "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", str(salida)])
    print("listo", salida)


if __name__ == "__main__":
    main()
