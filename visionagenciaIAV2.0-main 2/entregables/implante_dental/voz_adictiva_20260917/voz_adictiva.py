"""Voz nueva del video de Alberto: guion reescrito para que enganche + varias voces mexicanas.

Carlos (17 sep): «crea un mejor audio que escucharlo sea adictivo, voz mexicana».

Dos cambios contra voz_fish/voz_implante.py:

1. GUION. El viejo era de libro de texto ("Así se reemplaza con un implante, paso a paso"):
   informa, pero no da razón de quedarse. El nuevo abre con una pregunta que señala al que
   mira, promete algo que todavía no se ve ("por dentro") y lo paga hasta el segundo 12,
   que es justo donde el rostro se despega. En medio mata la objeción real (el dolor) y
   cierra con el beneficio, no con el procedimiento. Todo en segunda persona y tuteo.

2. REJA. El guion viejo caía en los marcadores de Blender (5.09, 6.75, 12.09, 14.09...).
   El nuevo cae en la reja de 5 s de los 7 tramos de Kling, así que voz y video quedan
   clavados: cada frase entra justo cuando empieza su tramo.

Genera un audio completo de 35 s por cada voz candidata, para escoger de oído.
Uso: python3 voz_adictiva.py            (todas las voces)
     python3 voz_adictiva.py narrador   (solo esa)
"""
import json, os, subprocess, sys, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = "/workspaces/visionagenciaIAV2.0/visionagenciaIAv2.0-cripto-sim-y-corte-catania/VisionagenciaIAv2.0-main"
API = "https://api.fish.audio/v1/tts"
MODELO = "s2.1-pro-free"
SR, DURACION = 44100, 35.0
RESPIRO = 0.20
TEMPO_MAX = 1.22   # más arriba de esto ya se oye atropellado

# Voces candidatas de Fish (español, locución; las de más likes del catálogo)
VOCES = {
    "narrador":  ("35199d5438854f5d9157c500479ab684", "Narrador v2 — la más usada del catálogo (4845)"),
    "locutor":   ("3f45a7fd7a614655a61eb7027b955783", "Voz de locutor K (3988)"),
    "documental":("c87656721dda48a7906f990f036ce76f", "Voz Narrador Documental (1006)"),
    "shorts":    ("279bb697a5b94a3a80ad8912136b6a5d", "Locutor para YouTube Shorts — ritmo de reel"),
    "mexicano":  ("3a485d962d2d4fb6838bc7eaf6d685a0", "Mexican Lopez — la mejor calificada con etiqueta mexicana"),
    "actual":    ("5e8ee00af4dd4f438d66fea8efa4baf4", "Doctor Carlos — la que trae hoy, para comparar"),
}

# (segundo en que entra, nombre, frase, velocidad Fish)
# Los segundos son los de la reja de 5 s: cada frase abre su tramo de Kling.
GUION = [
    (0.10,  "HOOK",        "¿Te falta un diente? Esto es lo que pasa por dentro.", 1.0),
    (5.10,  "ANESTESIA",   "Empieza con anestesia. No duele: ni lo vas a sentir.", 0.97),
    (10.10, "ADENTRO",     "Y aquí está lo que nadie te enseña.", 1.0),
    (15.10, "PREPARA",     "El dentista abre un espacio en el hueso, justo donde estaba tu raíz.", 0.95),
    (20.10, "TITANIO",     "Ahí entra un tornillo de titanio. Esa va a ser tu nueva raíz.", 0.96),
    (25.10, "INTEGRA",     "Con los meses tu hueso crece alrededor y lo deja firme.", 0.96),
    (30.10, "CORONA",      "Encima, una corona igual a tus dientes.", 0.98),
    (33.10, "SONRISA",     "Y vuelves a sonreír.", 0.98),
]


def env(n):
    for l in open(os.path.join(RAIZ, ".env"), encoding="utf8", errors="replace"):
        if l.startswith(n + "="):
            return l.split("=", 1)[1].strip().strip('"').strip("'")
    return os.environ.get(n, "")


def dura(r):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", r]).decode())


def habla(texto, salida, llave, voz, velocidad):
    cuerpo = {"text": texto, "format": "mp3", "sample_rate": SR,
              "prosody": {"speed": velocidad, "volume": 0}, "reference_id": voz}
    req = urllib.request.Request(API, data=json.dumps(cuerpo).encode(),
                                 headers={"Authorization": "Bearer " + llave,
                                          "Content-Type": "application/json", "model": MODELO})
    with urllib.request.urlopen(req, timeout=180) as r:
        datos = r.read()
    if len(datos) < 2000:
        raise SystemExit("Fish devolvió muy poco: " + datos[:300].decode("utf8", "replace"))
    open(salida, "wb").write(datos)


def arma(clave, llave):
    ref, desc = VOCES[clave]
    tmp = os.path.join(AQUI, "_frases", clave); os.makedirs(tmp, exist_ok=True)
    tiempos, entradas, filtros = [], [], []
    print("\n=== %s · %s ===" % (clave, desc), flush=True)
    for i, (inicio, nombre, texto, vel) in enumerate(GUION):
        mp3 = os.path.join(tmp, "%02d_%s.mp3" % (i, nombre))
        if not os.path.exists(mp3):
            habla(texto, mp3, llave, ref, vel)
        siguiente = GUION[i + 1][0] if i + 1 < len(GUION) else DURACION
        tramo = siguiente - inicio - RESPIRO
        d = dura(mp3)
        tempo = min(TEMPO_MAX, max(1.0, d / tramo))
        final = d / tempo
        encima = final > tramo + 0.05
        tiempos.append({"inicio_s": inicio, "nombre": nombre, "dura_s": round(final, 2),
                        "tramo_s": round(tramo, 2), "tempo": round(tempo, 3), "encima": encima, "texto": texto})
        entradas += ["-i", mp3]
        filtros.append("[%d:a]aresample=%d,aformat=channel_layouts=mono,atempo=%.4f,adelay=%d:all=1[f%d]"
                       % (i, SR, tempo, int(inicio * 1000), i))
        print("  %-10s %5.2f s  dura %.2f/%.2f  tempo %.2f%s" %
              (nombre, inicio, final, tramo, tempo, "  ⚠ SE ENCIMA" if encima else ""), flush=True)

    mezcla = (";".join(filtros) + ";" + "".join("[f%d]" % i for i in range(len(GUION)))
              + "amix=inputs=%d:duration=longest:normalize=0,apad,atrim=0:%.3f," % (len(GUION), DURACION)
              + "acompressor=threshold=-18dB:ratio=3:attack=15:release=250,highpass=f=80,"
                "loudnorm=I=-16:TP=-1.5:LRA=7[voz]")
    wav = os.path.join(AQUI, "VOZ_%s_35s.wav" % clave.upper())
    subprocess.run(["ffmpeg", "-v", "error", "-y", *entradas, "-filter_complex", mezcla, "-map", "[voz]",
                    "-ar", str(SR), "-ac", "1", wav], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wav, "-b:a", "192k", wav[:-4] + ".mp3"], check=True)
    print("  ->", os.path.basename(wav[:-4] + ".mp3"), "%.2f s" % dura(wav), flush=True)
    return tiempos


if __name__ == "__main__":
    llave = env("FISH_API_KEY")
    if not llave:
        raise SystemExit("falta FISH_API_KEY en VisionagenciaIAv2.0-main/.env")
    pedidas = [a for a in sys.argv[1:] if a in VOCES] or list(VOCES)
    todo = {c: arma(c, llave) for c in pedidas}
    json.dump({"guion": [dict(zip(("inicio_s", "nombre", "texto"), g[:3])) for g in GUION], "voces": todo},
              open(os.path.join(AQUI, "tiempos_adictiva.json"), "w"), ensure_ascii=False, indent=1)
    print("\nlisto:", ", ".join(pedidas))
