"""Adrián v16 (5 nov 2026). Carlos, en el chat de Adrián: «recrea el final, la ráfaga, SIN la
música, y los sonidos deben ser como el final del video de Guillermo».

Medí el final de Guillermo (Vicens_far12_v9) para no copiarlo de oído: lleva un golpe seco cada
0.48 s, uno por cada cambio de imagen, alternando grave (90-120 Hz) y agudo (560-870 Hz). No hay
melodía debajo: es percusión sola, y por eso pega tan fuerte.

Así que aquí la ráfaga va SIN cama musical y con ese mismo patrón: un golpe en cada cambio de foto,
alternando grave y agudo. Se queda el whoosh de entrada y el boom del cierre.
Salida: clientes/Tatuador9983316522/v3_subs/Adrian_v16_rafaga_sin_musica.mp4
"""
import math, pathlib, struct, subprocess, sys, wave

sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/Mariano/video")
from spiderman_musica import beat

AQUI = pathlib.Path(__file__).resolve().parent
TMP10 = AQUI / "tmp_v15"
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


def golpes(ruta):
    """Un golpe en cada cambio de foto, como el final de Guillermo: grave y agudo alternados.

    Medido del suyo: nivel alto (0.3 a 0.6), ataque instantáneo y caída muy corta. El grave lleva
    un poco de cuerpo (cae en 90 ms) y el agudo es casi un chasquido (25 ms).
    """
    m = [0.0] * int(TOTAL * SR)
    for k in range(N_FOTOS):
        i0 = int(k * DUR_T * SR)
        grave = (k % 2 == 0)
        f0 = 105 if grave else 760          # Hz, los dos tonos que alternan en el de Guillermo
        caida = 0.090 if grave else 0.025   # s
        vol = 0.62 if grave else 0.48
        for j in range(int(min(0.35, caida * 4) * SR)):
            if i0 + j >= len(m):
                break
            env = math.exp(-j / (caida * SR))
            # el armónico le da el golpe seco; sin él suena a pitido
            m[i0 + j] += vol * env * (math.sin(2 * math.pi * f0 * j / SR)
                                      + 0.35 * math.sin(2 * math.pi * f0 * 2.5 * j / SR))
    pico = max(abs(x) for x in m) or 1
    m = [x / pico * 0.9 for x in m]
    with wave.open(str(ruta), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, c)) * 32767)) for c in m))


def main():
    tmp = AQUI / "tmp_v16"; tmp.mkdir(exist_ok=True)
    # 1) nuestro beat: el drop cae al empezar la ráfaga (segundo 0 de este tramo)
    cl = tmp / "golpes.wav"; golpes(cl)

    # 2) video mudo del final (ráfaga + filtro + cierre), ya armado en la v10
    partes = [TMP10 / "rafaga.mp4", TMP10 / "filtro.mp4", TMP10 / "cierre.mp4"]
    (tmp / "lista.txt").write_text("".join(f"file '{p}'\n" for p in partes))
    mudo = tmp / "final_mudo.mp4"
    ff(["-f", "concat", "-safe", "0", "-i", str(tmp / "lista.txt"), "-an", "-c:v", "copy", str(mudo)])

    # 3) beat + whoosh de entrada + boom del cierre + clics
    # sin cama musical: solo whoosh de entrada, los golpes de la ráfaga y el boom del cierre
    fl = (f"[1:a]aresample={SR},volume=0.55[w];"
          f"[2:a]aresample={SR},volume=0.5,adelay={int((RAFAGA + 1.8) * 1000)}|{int((RAFAGA + 1.8) * 1000)}[b];"
          f"[3:a]aresample={SR},volume=1.0[c];"
          "[w][b][c]amix=inputs=3:duration=first:normalize=0,alimiter=limit=0.95,"
          "aformat=channel_layouts=stereo[a]")
    final = tmp / "final.mp4"
    ff(["-i", str(mudo), "-i", str(SFX / "whoosh.wav"), "-i", str(SFX / "boom.wav"),
        "-i", str(cl), "-filter_complex", fl, "-map", "0:v", "-map", "[a]", *VID, *AUD, "-shortest", str(final)])

    # 4) cuerpo con la voz (sin tocar) + final
    (tmp / "todo.txt").write_text(f"file '{TMP10 / 'cuerpo.mp4'}'\nfile '{final}'\n")
    salida = AQUI / "Adrian_v16_rafaga_sin_musica.mp4"
    ff(["-f", "concat", "-safe", "0", "-i", str(tmp / "todo.txt"), "-c", "copy",
        "-movflags", "+faststart", str(salida)])
    print("listo", salida)


if __name__ == "__main__":
    main()
