"""Adrián v11 (5 nov 2026): mismo video que la v10 (9/10) pero con EL SONIDO DE GUILLERMO.
Carlos pidió que el efecto sonara igual que el de su video de techos: se toma la pista de audio de esa
pieza (música nuestra, sintetizada por nosotros en armar_far12_v4_click.py) y se pone de cama en toda la
parte final —ráfaga, pregunta de filtro y cierre—, con los clics de cámara encima en cada corte.
La voz del cuerpo no se toca.
Salida: clientes/Tatuador9983316522/v3_subs/Adrian_v11_sonido_guillermo.mp4
"""
import math, pathlib, struct, subprocess, wave

AQUI = pathlib.Path(__file__).resolve().parent
TMP10 = AQUI / "tmp_v10"
REF = AQUI.parent / "hardcut_v2/WhatsApp Video 2026-11-04 at 7.07.03 PM.mp4"
SR, DUR_T = 44100, 0.30
VID = ["-c:v", "libx264", "-profile:v", "main", "-crf", "20", "-preset", "medium",
       "-pix_fmt", "yuv420p", "-r", "30", "-video_track_timescale", "15360"]
AUD = ["-c:a", "aac", "-b:a", "128k", "-ar", str(SR), "-ac", "2"]


def ff(a):
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", *a], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr[-1800:])


def clics(n, ruta, extra=4.9):
    """Los mismos clics de cámara, pero ahora cubren también el filtro y el cierre."""
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


def main():
    tmp = AQUI / "tmp_v11"; tmp.mkdir(exist_ok=True)
    # 1) la cama de música: la del video de Guillermo, desde el segundo 4 (donde ya entró el beat)
    cama = tmp / "cama.wav"
    ff(["-ss", "4.0", "-i", str(REF), "-vn", "-t", "8.2", "-ar", str(SR), "-ac", "2",
        "-af", "volume=0.55,afade=t=in:st=0:d=0.25,afade=t=out:st=7.6:d=0.6", str(cama)])

    # 2) video mudo de toda la parte final (ráfaga + filtro + cierre), reusando lo que ya está armado
    partes = [TMP10 / "rafaga.mp4", TMP10 / "filtro.mp4", TMP10 / "cierre.mp4"]
    (tmp / "lista.txt").write_text("".join(f"file '{p}'\n" for p in partes))
    final_mudo = tmp / "final_mudo.mp4"
    ff(["-f", "concat", "-safe", "0", "-i", str(tmp / "lista.txt"), "-an", "-c:v", "copy", str(final_mudo)])

    # 3) clics + cama = audio del final
    cl = tmp / "clics.wav"; clics(10, cl)
    final = tmp / "final.mp4"
    ff(["-i", str(final_mudo), "-i", str(cama), "-i", str(cl), "-filter_complex",
        "[1:a][2:a]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]",
        "-map", "0:v", "-map", "[a]", *VID, *AUD, "-shortest", str(final)])

    # 4) cuerpo (voz, sin tocar) + final
    (tmp / "todo.txt").write_text(f"file '{TMP10 / 'cuerpo.mp4'}'\nfile '{final}'\n")
    salida = AQUI / "Adrian_v11_sonido_guillermo.mp4"
    ff(["-f", "concat", "-safe", "0", "-i", str(tmp / "todo.txt"), "-c", "copy",
        "-movflags", "+faststart", str(salida)])
    print("listo", salida)


if __name__ == "__main__":
    main()
