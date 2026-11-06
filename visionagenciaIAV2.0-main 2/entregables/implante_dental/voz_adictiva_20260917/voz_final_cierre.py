"""Audio definitivo del video de Alberto: voz Narrador v2 + cierre con llamada a la acción.

Carlos (17 sep): «me gusta la primera» (Narrador v2) y «haz el cierre con llamada a la
acción con esa voz y que diga Veneers Dental».

Las seis primeras frases no se tocan: son las que ya aprobó. Sólo cambia la cola (30-35 s),
que antes era "Encima, una corona igual a tus dientes." + "Y vuelves a sonreír." y ahora
mete la marca y un verbo de acción.

Se arman tres versiones de la cola porque no puedo juzgar de oído cuál suena mejor ni cómo
lee el TTS la palabra "Veneers":
  pregunta      corona corta + "Vuelve a sonreír. Pregunta en Veneers Dental."
  pregunta_fon  igual, pero la marca escrita "Viníers" para que la lea a la española
  agenda        corona larga + "Agenda tu valoración en Veneers Dental."

Salida por versión: el track de 35 s y los 7 segmentos de 5 s de los tramos de Kling.
Uso: python3 voz_final_cierre.py [pregunta|pregunta_fon|agenda]
"""
import json, os, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from voz_adictiva import habla, env, dura, VOCES, SR, DURACION, RESPIRO, TEMPO_MAX

REF, _ = VOCES["narrador"]

# Las seis primeras frases, ya aprobadas, intactas
BASE = [
    (0.10,  "HOOK",      "¿Te falta un diente? Esto es lo que pasa por dentro.", 1.0),
    (5.10,  "ANESTESIA", "Empieza con anestesia. No duele: ni lo vas a sentir.", 0.97),
    (10.10, "ADENTRO",   "Y aquí está lo que nadie te enseña.", 1.0),
    (15.10, "PREPARA",   "El dentista abre un espacio en el hueso, justo donde estaba tu raíz.", 0.95),
    (20.10, "TITANIO",   "Ahí entra un tornillo de titanio. Esa va a ser tu nueva raíz.", 0.96),
    (25.10, "INTEGRA",   "Con los meses tu hueso crece alrededor y lo deja firme.", 0.96),
]

# Colas candidatas. Los segundos salen de medir cada frase con esta misma voz (probar_cierres.py).
COLAS = {
    "pregunta": [
        (30.10, "CORONA", "Encima va tu corona nueva.", 0.98),
        (32.00, "CIERRE", "Vuelve a sonreír. Pregunta en Veneers Dental.", 0.98),
    ],
    "pregunta_fon": [
        (30.10, "CORONA", "Encima va tu corona nueva.", 0.98),
        (32.00, "CIERRE", "Vuelve a sonreír. Pregunta en Viníers Dental.", 0.98),
    ],
    "agenda": [
        (30.10, "CORONA", "Encima, una corona igual a tus dientes.", 0.98),
        (32.65, "CIERRE", "Agenda tu valoración en Veneers Dental.", 0.98),
    ],
}

TRAMOS = [(1, 0, 5, "rostro_a_closeup"), (2, 5, 10, "anestesia"), (3, 10, 15, "sticker_y_fresa"),
          (4, 15, 20, "canal_y_tornillo"), (5, 20, 25, "tornillo_e_integracion"),
          (6, 25, 30, "pilar_y_corona"), (7, 30, 35, "morph_sonrisa")]


def arma(version, llave):
    guion = BASE + COLAS[version]
    tmp = os.path.join(AQUI, "_frases", "final_" + version); os.makedirs(tmp, exist_ok=True)
    entradas, filtros, tiempos = [], [], []
    print("\n=== %s ===" % version, flush=True)
    for i, (inicio, nombre, texto, vel) in enumerate(guion):
        mp3 = os.path.join(tmp, "%02d_%s.mp3" % (i, nombre))
        if not os.path.exists(mp3):
            habla(texto, mp3, llave, REF, vel)
        siguiente = guion[i + 1][0] if i + 1 < len(guion) else DURACION
        tramo = siguiente - inicio - (RESPIRO if i + 1 < len(guion) else 0.05)
        d = dura(mp3)
        tempo = min(TEMPO_MAX, max(1.0, d / tramo))
        final = d / tempo
        encima = final > tramo + 0.05
        entradas += ["-i", mp3]
        filtros.append("[%d:a]aresample=%d,aformat=channel_layouts=mono,atempo=%.4f,adelay=%d:all=1[f%d]"
                       % (i, SR, tempo, int(inicio * 1000), i))
        tiempos.append({"inicio_s": inicio, "nombre": nombre, "dura_s": round(final, 2),
                        "tramo_s": round(tramo, 2), "tempo": round(tempo, 3), "encima": encima, "texto": texto})
        print("  %-10s %5.2f s  dura %.2f/%.2f  tempo %.2f%s" %
              (nombre, inicio, final, tramo, tempo, "  ⚠ SE ENCIMA" if encima else ""), flush=True)

    mezcla = (";".join(filtros) + ";" + "".join("[f%d]" % i for i in range(len(guion)))
              + "amix=inputs=%d:duration=longest:normalize=0,apad,atrim=0:%.3f," % (len(guion), DURACION)
              + "acompressor=threshold=-18dB:ratio=3:attack=15:release=250,highpass=f=80,"
                "loudnorm=I=-16:TP=-1.5:LRA=7,apad=whole_dur=%.3f[voz]" % DURACION)
    wav = os.path.join(AQUI, "FINAL_%s_35s.wav" % version.upper())
    subprocess.run(["ffmpeg", "-v", "error", "-y", *entradas, "-filter_complex", mezcla, "-map", "[voz]",
                    "-ar", str(SR), "-ac", "1", "-t", "%.3f" % DURACION, wav], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wav, "-b:a", "192k", wav[:-4] + ".mp3"], check=True)
    print("  track:", os.path.basename(wav[:-4] + ".mp3"), "%.3f s" % dura(wav), flush=True)

    seg = os.path.join(AQUI, "SEGMENTOS_" + version.upper()); os.makedirs(seg, exist_ok=True)
    for n, a, b, nombre in TRAMOS:
        base = os.path.join(seg, "VOZ_T%d_%s" % (n, nombre))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a), "-t", str(b - a), "-i", wav,
                        "-af", "apad=whole_dur=%d" % (b - a), "-ar", str(SR), "-ac", "1",
                        "-t", str(b - a), base + ".wav"], check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", base + ".wav", "-b:a", "192k", base + ".mp3"],
                       check=True)
        print("    T%d %2d-%2d s  %.3f s" % (n, a, b, dura(base + ".wav")), flush=True)
    return tiempos


if __name__ == "__main__":
    llave = env("FISH_API_KEY")
    pedidas = [a for a in sys.argv[1:] if a in COLAS] or list(COLAS)
    todo = {v: arma(v, llave) for v in pedidas}
    json.dump(todo, open(os.path.join(AQUI, "tiempos_final.json"), "w"), ensure_ascii=False, indent=1)
    print("\nlisto:", ", ".join(pedidas))
