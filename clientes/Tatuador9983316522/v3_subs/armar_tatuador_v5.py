"""Adrián v5 (5 nov 2026, pedido de Carlos): a la v4 se le mete al final una RÁFAGA con sus trabajos,
con clic de cámara en cada corte (como el video de Guillermo), para subir CONFIANZA — que es el rubro
que Glimmer tiene en 7 y pide prueba de su trabajo.
Estructura: cuerpo de la v4 (voz + subtítulos + tarjetas) · ráfaga de 5 trabajos reales con clics · cierre con el CTA.
Los clips de la ráfaga son suyos, de `hardcut_v2/` (trabajos terminados: pecho, samurái, sirena, anime).
Salida: clientes/Tatuador9983316522/v3_subs/Adrian_v5_rafaga.mp4
"""
import math, pathlib, struct, subprocess, wave

AQUI = pathlib.Path(__file__).resolve().parent
CUERPO = AQUI / "tmp_v4/cuerpo.mp4"          # v4 sin el cierre
CIERRE = AQUI / "tmp_v4/cierre.mp4"
HC = AQUI.parent / "hardcut_v2"
FUENTES = pathlib.Path("/workspaces/Nexusv2.0launch18octubre/visionagenciaIAV2.0-main 2/entregables/modelos_modal/fuentes")
W, H, FPS, SR = 720, 1280, 30, 44100
CLIPS = ["s02", "s03", "s05", "s07", "s09"]   # pecho · samurái · sirena · anime · proceso
DUR = 0.46                                     # cada toma de la ráfaga
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


def tarjeta(ruta):
    from PIL import Image, ImageDraw
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    t = "TRABAJOS DE ADRIÁN"
    f = fu(40, 800)
    an = d.textlength(t, font=f) + 76
    d.rounded_rectangle(((W - an) / 2, 120, (W + an) / 2, 192), 34, fill=VERDE + (235,), outline=ORO + (255,), width=3)
    d.text((W / 2, 156), t, font=f, fill="white", anchor="mm")
    im.save(ruta)


def clics(n, ruta):
    """Clic de cámara en cada corte: seno de 2 kHz con caída rápida, como el video de Guillermo."""
    total = n * DUR + 0.25
    muestras = [0.0] * int(total * SR)
    for k in range(n):
        i0 = int(k * DUR * SR)
        for j in range(int(0.035 * SR)):
            if i0 + j < len(muestras):
                env = math.exp(-j / (0.006 * SR))
                muestras[i0 + j] += 0.5 * env * math.sin(2 * math.pi * 2000 * j / SR)
    with wave.open(str(ruta), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, c)) * 32767)) for c in muestras))


def tapa(ruta):
    """Tapa el texto que él traía pegado al final («AGENDA AL DM»), que choca con nuestro cierre de WhatsApp."""
    from PIL import Image, ImageDraw
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 352), fill=(10, 14, 12, 242))
    t = "ADRIÁN SANTANA · CANCÚN CENTRO"
    f = fu(34, 800)
    an = d.textlength(t, font=f) + 70
    d.rounded_rectangle(((W - an) / 2, 150, (W + an) / 2, 222), 34, fill=VERDE + (242,), outline=ORO + (255,), width=3)
    d.text((W / 2, 186), t, font=f, fill="white", anchor="mm")
    d.text((W / 2, 280), "Escríbeme la palabra CITA por WhatsApp", font=fu(28, 600), fill=ORO, anchor="mm")
    im.save(ruta)


def main():
    tmp = AQUI / "tmp_v5"; tmp.mkdir(exist_ok=True)
    # 1) cuerpo con la tapa sobre su texto viejo de «AGENDA AL DM»
    tp = tmp / "tapa.png"; tapa(tp)
    cuerpo_ok = tmp / "cuerpo_ok.mp4"
    ff(["-i", str(CUERPO), "-i", str(tp), "-filter_complex",
        "[0:v][1:v]overlay=0:0:enable='gte(t,14.6)',format=yuv420p[v]",
        "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-crf", "20",
        "-c:a", "aac", "-b:a", "128k", str(cuerpo_ok)])
    partes = []
    for i, c in enumerate(CLIPS):
        src = HC / f"{c}.mp4"
        p = tmp / f"r{i}.mp4"
        ff(["-ss", "0.15", "-i", str(src), "-t", f"{DUR}",
            "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                   f"eq=contrast=1.08:saturation=1.1,fps={FPS},setsar=1",
            "-an", "-c:v", "libx264", "-crf", "19", "-pix_fmt", "yuv420p", str(p)])
        partes.append(p)
    (tmp / "lista.txt").write_text("".join(f"file '{p}'\n" for p in partes))
    rafaga_muda = tmp / "rafaga_muda.mp4"
    ff(["-f", "concat", "-safe", "0", "-i", str(tmp / "lista.txt"), "-c", "copy", str(rafaga_muda)])

    t = tmp / "tarjeta.png"; tarjeta(t)
    cl = tmp / "clics.wav"; clics(len(CLIPS), cl)
    rafaga = tmp / "rafaga.mp4"
    ff(["-i", str(rafaga_muda), "-i", str(t), "-i", str(cl),
        "-filter_complex", "[0:v][1:v]overlay=0:0,format=yuv420p[v]",
        "-map", "[v]", "-map", "2:a", "-c:v", "libx264", "-crf", "19",
        "-c:a", "aac", "-b:a", "128k", "-shortest", str(rafaga)])

    (tmp / "final.txt").write_text(f"file '{cuerpo_ok}'\nfile '{rafaga}'\nfile '{CIERRE}'\n")
    salida = AQUI / "Adrian_v5_rafaga.mp4"
    ff(["-f", "concat", "-safe", "0", "-i", str(tmp / "final.txt"),
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
        "-c:v", "libx264", "-profile:v", "main", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(salida)])
    print("listo", salida)


if __name__ == "__main__":
    main()
