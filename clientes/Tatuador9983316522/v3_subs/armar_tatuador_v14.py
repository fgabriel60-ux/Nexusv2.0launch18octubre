"""Adrián v12 (5 nov 2026): mismo video de la v10 (9/10) pero con la música RECREADA por nosotros,
no copiada del video de Guillermo.
Carlos: «no copiar el de Guillermo, replicar el sonido, tú lo pusiste originalmente».
Se usa nuestro sintetizador propio `spiderman_musica.beat` (124 BPM, sin derechos de terceros), con el
DROP justo cuando arranca la ráfaga de trabajos, más el whoosh en la entrada y el boom del cierre
(`clientes/Guillermo/video/sfx/`), y encima los clics de cámara en cada corte.
Salida: clientes/Tatuador9983316522/v3_subs/Adrian_v14_final95.mp4
"""
import math, pathlib, struct, subprocess, sys, wave

sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/Mariano/video")
from spiderman_musica import beat

AQUI = pathlib.Path(__file__).resolve().parent
TMP10 = AQUI / "tmp_v13"
SFX = pathlib.Path("/workspaces/Nexusv2.0launch18octubre/clientes/Guillermo/video/sfx")
SR, DUR_T, N_FOTOS = 44100, 1.10, 6
RAFAGA = N_FOTOS * DUR_T          # 3.0 s
TOTAL = RAFAGA + 1.8 + 3.0        # ráfaga + filtro + cierre
VID = ["-c:v", "libx264", "-profile:v", "main", "-crf", "20", "-preset", "medium",
       "-pix_fmt", "yuv420p", "-r", "30", "-video_track_timescale", "15360"]
AUD = ["-c:a", "aac", "-b:a", "128k", "-ar", str(SR), "-ac", "2"]


def ff(a):
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", *a], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr[-1800:])


def clics(ruta):
    m = [0.0] * int(TOTAL * SR)
    for k in range(N_FOTOS):
        i0 = int(k * DUR_T * SR)
        for j in range(int(0.035 * SR)):
            if i0 + j < len(m):
                m[i0 + j] += 0.5 * math.exp(-j / (0.006 * SR)) * math.sin(2 * math.pi * 2000 * j / SR)
    with wave.open(str(ruta), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, c)) * 32767)) for c in m))


def main():
    tmp = AQUI / "tmp_v14"; tmp.mkdir(exist_ok=True)
    # 1) nuestro beat: el drop cae al empezar la ráfaga (segundo 0 de este tramo)
    cama = tmp / "beat_adrian.wav"
    beat(str(cama), 0.25, TOTAL)
    cl = tmp / "clics.wav"; clics(cl)

    # 2) video mudo del final (ráfaga + filtro + cierre), ya armado en la v10
    partes = [TMP10 / "rafaga.mp4", TMP10 / "filtro.mp4", TMP10 / "cierre.mp4"]
    (tmp / "lista.txt").write_text("".join(f"file '{p}'\n" for p in partes))
    mudo = tmp / "final_mudo.mp4"
    ff(["-f", "concat", "-safe", "0", "-i", str(tmp / "lista.txt"), "-an", "-c:v", "copy", str(mudo)])

    # 3) beat + whoosh de entrada + boom del cierre + clics
    fl = (f"[1:a]aresample={SR},volume=0.8,afade=t=out:st={TOTAL - 1.0:.2f}:d=1.0[m];"
          f"[2:a]aresample={SR},volume=0.55[w];"
          f"[3:a]aresample={SR},volume=0.5,adelay={int((RAFAGA + 1.8) * 1000)}|{int((RAFAGA + 1.8) * 1000)}[b];"
          f"[4:a]aresample={SR},volume=0.9[c];"
          "[m][w][b][c]amix=inputs=4:duration=first:normalize=0,alimiter=limit=0.95,"
          "aformat=channel_layouts=stereo[a]")
    final = tmp / "final.mp4"
    ff(["-i", str(mudo), "-i", str(cama), "-i", str(SFX / "whoosh.wav"), "-i", str(SFX / "boom.wav"),
        "-i", str(cl), "-filter_complex", fl, "-map", "0:v", "-map", "[a]", *VID, *AUD, "-shortest", str(final)])

    # 4) cuerpo con la voz (sin tocar) + final
    (tmp / "todo.txt").write_text(f"file '{TMP10 / 'cuerpo.mp4'}'\nfile '{final}'\n")
    salida = AQUI / "Adrian_v14_final95.mp4"
    ff(["-f", "concat", "-safe", "0", "-i", str(tmp / "todo.txt"), "-c", "copy",
        "-movflags", "+faststart", str(salida)])
    print("listo", salida)


if __name__ == "__main__":
    main()
