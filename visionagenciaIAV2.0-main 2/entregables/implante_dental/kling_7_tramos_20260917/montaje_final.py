"""Arma el video completo de Alberto: los 7 tramos ganadores + la voz.

Cada tramo salió de un modelo distinto porque cada uno falló en cosas distintas. Esta tabla
es el resultado de todo el 17 sep; el porqué de cada elección está en RESULTADO_FINAL.md.

Todo se normaliza a 1080x1920 @ 30 fps y a 5.000 s exactos, porque Seedance y
reference-to-video entregan a 24 fps y 5.04 s. Siete por cinco = 35.000 s clavados,
que es justo lo que dura la voz.
"""
import json, os, subprocess

AQUI = os.path.dirname(os.path.abspath(__file__))
DENTAL = os.path.dirname(AQUI)
VOZ = os.path.join(DENTAL, "voz_adictiva_20260917", "FINAL_AGENDA_35s.mp3")
TMP = os.path.join(AQUI, "_montaje"); os.makedirs(TMP, exist_ok=True)
FINAL = os.path.join(AQUI, "IMPLANTE_ALBERTO_FINAL_35s.mp4")

# (tramo, archivo ganador, modelo, costo, qué pasa)
TRAMOS = [
    (1, "CLIPS/T1_rostro_a_closeup.mp4",                  "Kling 2.6 pro (cuadros llave)", 0.35,
     "rostro con el hueco, la cámara entra al macro"),
    (2, "CLIPS/T2_anestesia.mp4",                         "Kling 2.6 pro (cuadros llave)", 0.35,
     "la jeringa entra, anestesia y se retira"),
    (3, "PRUEBA_SEEDANCE_T3.mp4",                         "Seedance 2.0 fast 1080p",       2.50,
     "el rostro se despega como calcomanía y entra la fresa"),
    (4, "CLIPS/T4_canal_y_tornillo.mp4",                  "Kling 2.6 pro (cuadros llave)", 0.35,
     "la fresa termina el canal y sube el tornillo"),
    (5, "PRUEBA_REF2VIDEO_T5.mp4",                        "Kling o3 pro + video Blender",  0.84,
     "el tornillo se atornilla hasta el fondo e integra"),
    (6, "CLIPS/T6_pilar_y_corona.mp4",                    "Kling 2.6 pro (cuadros llave)", 0.35,
     "el hueso integra y la corona sube y se asienta"),
    (7, "CLIPS_SEEDANCE/T7_morph_sonrisa_480p.mp4",       "Seedance 2.0 fast 480p",        0.50,
     "la piel regresa y la sonrisa se abre"),
]

W, H, FPS, DUR = 1080, 1920, 30, 5.000


def dura(r):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", r]).decode())


if __name__ == "__main__":
    partes = []
    print("normalizando a %dx%d @ %d fps, %.3f s cada uno\n" % (W, H, FPS, DUR))
    for n, rel, modelo, costo, que in TRAMOS:
        src = os.path.join(AQUI, rel)
        assert os.path.exists(src), "falta el tramo %d: %s" % (n, rel)
        dst = os.path.join(TMP, "t%d.mp4" % n)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-t", "%.3f" % DUR,
                        "-vf", "scale=%d:%d:flags=lanczos,fps=%d" % (W, H, FPS),
                        "-c:v", "libx264", "-crf", "17", "-preset", "medium",
                        "-pix_fmt", "yuv420p", "-an", dst], check=True)
        print("  T%d  %-46s %5.3f s  $%.2f  %s" % (n, os.path.basename(rel), dura(dst), costo, que))
        partes.append(dst)

    lista = os.path.join(TMP, "lista.txt")
    open(lista, "w").write("".join("file '%s'\n" % p for p in partes))
    mudo = os.path.join(TMP, "mudo.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lista,
                    "-c", "copy", mudo], check=True)
    assert abs(dura(mudo) - 35.0) < 0.05, "el pegado no dio 35 s: %.3f" % dura(mudo)

    # La voz dura 34.92 y el video 35.000: se rellena el audio con silencio en vez de recortar
    # el video con -shortest, que se comía el último cuadro de la sonrisa.
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mudo, "-i", VOZ, "-map", "0:v", "-map", "1:a",
                    "-af", "apad=whole_dur=35.0", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-t", "35.0", FINAL], check=True)
    assert abs(dura(FINAL) - 35.0) < 0.02, "el final no dio 35 s: %.3f" % dura(FINAL)

    # versión ligera para WhatsApp
    wa = FINAL.replace(".mp4", "_WHATSAPP.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", FINAL, "-vf", "scale=720:1280",
                    "-c:v", "libx264", "-crf", "24", "-preset", "medium", "-profile:v", "baseline",
                    "-level", "3.1", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
                    "-movflags", "+faststart", wa], check=True)

    total = sum(t[3] for t in TRAMOS)
    json.dump({"final": os.path.basename(FINAL), "duracion_s": round(dura(FINAL), 3),
               "voz": os.path.basename(VOZ),
               "tramos": [{"tramo": n, "archivo": r, "modelo": m, "costo": c, "que": q}
                          for n, r, m, c, q in TRAMOS],
               "costo_clips_usados": round(total, 2)},
              open(os.path.join(AQUI, "montaje_final.json"), "w"), ensure_ascii=False, indent=1)
    print("\nFINAL     %s  %.3f s" % (os.path.basename(FINAL), dura(FINAL)))
    print("WHATSAPP  %s  %.1f MB" % (os.path.basename(wa), os.path.getsize(wa) / 1e6))
    print("costo de los clips usados: $%.2f" % total)
