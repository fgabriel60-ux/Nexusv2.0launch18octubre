"""Parte la voz elegida (Narrador v2) en los 7 segmentos de 5 s de los tramos de Kling.

Carlos (17 sep): «me gusta la primera, corta el audio en segmentos».

Cada corte cae exactamente en un múltiplo de 5 s. Se comprobó con silencedetect que los
ocho silencios del track cubren TODOS los cortes (2.63-5.16, 8.46-10.03, 11.82-15.16,
18.47-20.16, 23.49-25.15, 28.10-30.16), así que ningún corte parte una palabra.

Salida: SEGMENTOS/T1..T7 en mp3 y wav, más un reporte de qué frase trae cada uno.
Uso: python3 cortar_en_segmentos.py [VOZ_XXX_35s.mp3]
"""
import json, os, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
SEG = os.path.join(AQUI, "SEGMENTOS"); os.makedirs(SEG, exist_ok=True)
FUENTE = os.path.join(AQUI, sys.argv[1] if len(sys.argv) > 1 else "VOZ_NARRADOR_35s.wav")
SR = 44100

# (tramo, de, a, nombre del tramo de video, frases que caen adentro)
TRAMOS = [
    (1,  0,  5, "T1_rostro_a_closeup",      ["¿Te falta un diente? Esto es lo que pasa por dentro."]),
    (2,  5, 10, "T2_anestesia",             ["Empieza con anestesia. No duele: ni lo vas a sentir."]),
    (3, 10, 15, "T3_sticker_y_fresa",       ["Y aquí está lo que nadie te enseña."]),
    (4, 15, 20, "T4_canal_y_tornillo",      ["El dentista abre un espacio en el hueso, justo donde estaba tu raíz."]),
    (5, 20, 25, "T5_tornillo_e_integracion",["Ahí entra un tornillo de titanio. Esa va a ser tu nueva raíz."]),
    (6, 25, 30, "T6_pilar_y_corona",        ["Con los meses tu hueso crece alrededor y lo deja firme."]),
    (7, 30, 35, "T7_morph_sonrisa",         ["Encima, una corona igual a tus dientes.", "Y vuelves a sonreír."]),
]


def dura(r):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", r]).decode())


def pico(r):
    s = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", r, "-af", "volumedetect",
                        "-f", "null", os.devnull], capture_output=True, text=True).stderr
    for l in s.splitlines():
        if "max_volume" in l:
            return l.split("max_volume:")[1].strip()
    return "?"


if __name__ == "__main__":
    assert os.path.exists(FUENTE), "no está la fuente: " + FUENTE
    print("fuente:", os.path.basename(FUENTE), "%.2f s\n" % dura(FUENTE))
    reporte = []
    for n, a, b, nombre, frases in TRAMOS:
        base = os.path.join(SEG, "VOZ_T%d_%s" % (n, nombre.split("_", 1)[1]))
        # -ss/-t sobre el wav para cortar al sample exacto, luego mp3 para mandar
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a), "-t", str(b - a), "-i", FUENTE,
                        "-ar", str(SR), "-ac", "1", base + ".wav"], check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", base + ".wav", "-b:a", "192k", base + ".mp3"],
                       check=True)
        d = dura(base + ".wav")
        print("T%d  %2d-%2d s  %.3f s  pico %-8s  %s" % (n, a, b, d, pico(base + ".wav"), " / ".join(frases)))
        reporte.append({"tramo": n, "de_s": a, "a_s": b, "dura_s": round(d, 3),
                        "video": nombre, "archivo": os.path.basename(base) + ".mp3", "frases": frases})
    json.dump({"fuente": os.path.basename(FUENTE), "segmentos": reporte},
              open(os.path.join(AQUI, "segmentos.json"), "w"), ensure_ascii=False, indent=1)
    print("\n-> SEGMENTOS/ (%d wav + %d mp3)" % (len(TRAMOS), len(TRAMOS)))
