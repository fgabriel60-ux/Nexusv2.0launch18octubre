"""Adrián v6 (5 nov 2026): la ráfaga ahora es con SUS trabajos reales (los 13 que mandó por WhatsApp
el 5 nov), con clic de cámara en cada corte como el video de Guillermo, y antes del cierre se mete la
PREGUNTA DE FILTRO que pidió Glimmer («¿tatuaje pequeño o proyecto grande?»), que sube los mensajes
calificados.
Salida: clientes/Tatuador9983316522/v3_subs/Adrian_v6_trabajos.mp4
"""
import math, pathlib, struct, subprocess, wave

AQUI = pathlib.Path(__file__).resolve().parent
CUERPO = AQUI / "tmp_v5/cuerpo_ok.mp4"       # cuerpo de la v5 (con la tapa sobre el texto viejo)
TRABAJOS = AQUI.parent / "trabajos_1105"
FUENTES = pathlib.Path("/workspaces/Nexusv2.0launch18octubre/visionagenciaIAV2.0-main 2/entregables/modelos_modal/fuentes")
W, H, FPS, SR = 720, 1280, 30, 44100
DUR = 0.44
VERDE, ORO = (18, 46, 36), (236, 200, 90)


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


def tarjeta_rafaga(ruta):
    from PIL import Image, ImageDraw
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    t = "TRABAJOS DE ADRIÁN"
    f = fu(40, 800); an = d.textlength(t, font=f) + 76
    d.rounded_rectangle(((W - an) / 2, 120, (W + an) / 2, 192), 34, fill=VERDE + (235,), outline=ORO + (255,), width=3)
    d.text((W / 2, 156), t, font=f, fill="white", anchor="mm")
    im.save(ruta)


def tarjeta_filtro(ruta):
    """Pregunta de filtro: separa al que quiere algo chico del proyecto grande."""
    from PIL import Image, ImageDraw
    im = Image.new("RGB", (W, H), (12, 16, 14)); d = ImageDraw.Draw(im)
    d.text((W / 2, 470), "¿TATUAJE PEQUEÑO", font=fu(56, 900), fill="white", anchor="mm")
    d.text((W / 2, 540), "O PROYECTO GRANDE?", font=fu(56, 900), fill="white", anchor="mm")
    d.text((W / 2, 640), "Dime cuál y te paso precio y fecha", font=fu(32, 600), fill=ORO, anchor="mm")
    im.save(ruta)


def cierre(ruta):
    from PIL import Image, ImageDraw
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
    im.save(ruta)


def clics(n, ruta, extra=0.3):
    total = n * DUR + extra
    m = [0.0] * int(total * SR)
    for k in range(n):
        i0 = int(k * DUR * SR)
        for j in range(int(0.035 * SR)):
            if i0 + j < len(m):
                m[i0 + j] += 0.5 * math.exp(-j / (0.006 * SR)) * math.sin(2 * math.pi * 2000 * j / SR)
    with wave.open(str(ruta), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, c)) * 32767)) for c in m))


def main():
    tmp = AQUI / "tmp_v6"; tmp.mkdir(exist_ok=True)
    fotos = sorted(TRABAJOS.glob("*.jpg"))[:10]
    partes = []
    n = int(DUR * FPS) + 1
    for i, f in enumerate(fotos):
        p = tmp / f"r{i}.mp4"
        z = "min(zoom+0.0016,1.12)" if i % 2 == 0 else "if(eq(on,1),1.12,max(zoom-0.0016,1))"
        ff(["-loop", "1", "-i", str(f), "-vf",
            f"scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2},"
            f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps={FPS},setsar=1",
            "-frames:v", str(n), "-an", "-c:v", "libx264", "-crf", "19", "-pix_fmt", "yuv420p", str(p)])
        partes.append(p)
    (tmp / "lista.txt").write_text("".join(f"file '{p}'\n" for p in partes))
    muda = tmp / "muda.mp4"
    ff(["-f", "concat", "-safe", "0", "-i", str(tmp / "lista.txt"), "-c", "copy", str(muda)])

    tr = tmp / "tarjeta.png"; tarjeta_rafaga(tr)
    cl = tmp / "clics.wav"; clics(len(fotos), cl)
    rafaga = tmp / "rafaga.mp4"
    ff(["-i", str(muda), "-i", str(tr), "-i", str(cl), "-filter_complex",
        "[0:v][1:v]overlay=0:0,format=yuv420p[v]", "-map", "[v]", "-map", "2:a",
        "-c:v", "libx264", "-crf", "19", "-c:a", "aac", "-b:a", "128k", "-shortest", str(rafaga)])

    fi = tmp / "filtro.png"; tarjeta_filtro(fi)
    filtro = tmp / "filtro.mp4"
    ff(["-loop", "1", "-i", str(fi), "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
        "-t", "1.8", "-vf", f"fps={FPS},setsar=1", "-c:v", "libx264", "-crf", "19",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-shortest", str(filtro)])

    ci = tmp / "cierre.png"; cierre(ci)
    cierre_mp4 = tmp / "cierre.mp4"
    ff(["-loop", "1", "-i", str(ci), "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
        "-t", "3", "-vf", f"fps={FPS},setsar=1", "-c:v", "libx264", "-crf", "19",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-shortest", str(cierre_mp4)])

    (tmp / "final.txt").write_text(
        f"file '{CUERPO}'\nfile '{rafaga}'\nfile '{filtro}'\nfile '{cierre_mp4}'\n")
    salida = AQUI / "Adrian_v6_trabajos.mp4"
    ff(["-f", "concat", "-safe", "0", "-i", str(tmp / "final.txt"),
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
        "-c:v", "libx264", "-profile:v", "main", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(salida)])
    print("listo", salida, len(fotos), "trabajos")


if __name__ == "__main__":
    main()
