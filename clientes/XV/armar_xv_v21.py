"""Manuel · XV v21 (5 nov 2026): aplica lo que pidió Glimmer sobre la v20 (6/10 → 8/10 proyectada).
Cambio principal: los primeros 2.5 s (el letrero XV estático, gancho débil) se reemplazan por un
primer plano REAL de la quinceañera con corona y ramo, con push-in suave. La foto es de su propio
trabajo (frames_real/base_7_retrato.png), no generada: para un fotógrafo, enseñar su foto real vale más.
El audio no se toca: el cuadro nuevo va encima, así no se desincroniza la voz ni la música.
Salida: clientes/XV/final/XV_reel_v21_manuel.mp4
"""
import pathlib
import subprocess

AQUI = pathlib.Path(__file__).resolve().parent
ORIG = AQUI / "final/XV_reel_v20_manuel.mp4"
FOTO = AQUI / "frames_real/base_7_retrato.png"
FUENTES = pathlib.Path("/workspaces/Nexusv2.0launch18octubre/visionagenciaIAV2.0-main 2/entregables/modelos_modal/fuentes")
W, H, FPS, DUR = 720, 1280, 25, 2.5


def ff(a):
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", *a], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr[-1500:])


def fu(t, peso=800):
    from PIL import ImageFont
    f = ImageFont.truetype(str(FUENTES / "Montserrat.ttf"), t)
    try:
        f.set_variation_by_axes([peso])
    except Exception:
        pass
    return f


def capa(ruta):
    """Mismo encabezado y pie que ya trae su video, para que el corte no se note."""
    from PIL import Image, ImageDraw
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.text((W / 2, 26), "HUNAB KU FOTOGRAFÍA", font=fu(23, 800), fill="white", anchor="mm")
    d.text((W / 2, 52), "XV AÑOS", font=fu(20, 700), fill="white", anchor="mm")
    d.text((W / 2, H - 58), "WHATSAPP +1 520 313 6941", font=fu(22, 800), fill="white", anchor="mm")
    d.text((W / 2, H - 150), "Un recuerdo que dura", font=fu(40, 900), fill="white", anchor="mm",
           stroke_width=5, stroke_fill=(30, 20, 40))
    im.save(ruta)


def main():
    tmp = AQUI / "tmp_v21"; tmp.mkdir(exist_ok=True)
    c = tmp / "capa.png"; capa(c)
    gancho = tmp / "gancho.mp4"
    n = int(DUR * FPS)
    ff(["-loop", "1", "-i", str(FOTO), "-i", str(c), "-filter_complex",
        f"[0:v]scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2},"
        f"zoompan=z='min(zoom+0.0012,1.10)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps={FPS},"
        f"setsar=1[a];[a][1:v]overlay=0:0,format=yuv420p",
        "-frames:v", str(n), "-c:v", "libx264", "-crf", "18", str(gancho)])

    salida = AQUI / "final/XV_reel_v21_manuel.mp4"
    ff(["-i", str(ORIG), "-i", str(gancho), "-filter_complex",
        f"[1:v]setpts=PTS-STARTPTS[g];[0:v][g]overlay=0:0:enable='lt(t,{DUR})'[v]",
        "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-profile:v", "main", "-crf", "20",
        "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart", str(salida)])
    print("listo", salida)


if __name__ == "__main__":
    main()
