"""Voz de Pancho para el guion A «Antes de pagar» (sin lo del papá), con su voz clonada en Fish.

El crédito de API de Fish está en 0 y el modelo gratis (s2.1-pro-free) no acepta clonación al vuelo, así que
la voz se guardó como modelo privado «Pancho Mecánico» (VOZ, 18 sep) desde aud1.mp3 (17.5 s, tono 135 Hz, el
más cercano a sus 129 Hz según Nexus) con su transcripción.

Cada escena se genera aparte y se une con un respiro corto; la salida es un solo audio de ~27 s. v2 (18 sep): abre con la pieza en la mano,
como Maya abre con el momento fuerte (ver APRENDIZAJES_MAYA.md).
Uso: python3 voz_pancho_A.py"""
import json, os, subprocess, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = "/workspaces/visionagenciaIAV2.0/visionagenciaIAv2.0-cripto-sim-y-corte-catania/VisionagenciaIAv2.0-main"
MUESTRA = os.path.join(AQUI, "..", "aud1.mp3")
MUESTRA_TEXTO = ("Aprendí a reparar en el taller de mi papá con prueba y error. Un carro no se arregla con piezas "
                 "caras, se arregla con quien entiende. Por eso no cambio partes al azar. Te digo qué tiene y te "
                 "lo dejo andando. Manda foto por WhatsApp y te paso el precio hoy.")
VOZ = "4368caa16bba4bc294a627c559fcf3be"
MODELO, SR, RESPIRO = "s2.1-pro-free", 44100, 0.30

ESCENAS = [
    ("PIEZA", "Esta pieza te la iban a cobrar… y no era la falla."),
    ("HOOK",  "¿Te quieren cambiar medio carro? Antes de pagar, escúchame."),
    ("DEMO",  "Hay talleres que cambian piezas hasta atinarle… y tú pagas cada intento. Yo primero encuentro la falla."),
    ("TRUST", "Aquí un carro se arregla entendiéndolo, no cambiándole todo."),
    ("CTA",   "Mándame por WhatsApp una foto o un audio del ruido, y hoy te digo qué tiene y cuánto cuesta."),
]


def env(n):
    for l in open(os.path.join(RAIZ, ".env"), encoding="utf8", errors="replace"):
        if l.startswith(n + "="):
            return l.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def dura(r):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", r]).decode())


def habla(texto, salida, llave, ref):
    cuerpo = {"text": texto, "format": "mp3", "sample_rate": SR, "prosody": {"speed": 1.0, "volume": 0},
              "reference_id": ref}
    req = urllib.request.Request("https://api.fish.audio/v1/tts", data=json.dumps(cuerpo).encode(),
                                 headers={"Authorization": "Bearer " + llave, "Content-Type": "application/json",
                                          "model": MODELO})
    with urllib.request.urlopen(req, timeout=300) as r:
        datos = r.read()
    if len(datos) < 2000:
        raise SystemExit("Fish devolvió muy poco: " + datos[:300].decode("utf8", "replace"))
    open(salida, "wb").write(datos)


if __name__ == "__main__":
    llave = env("FISH_API_KEY")
    ref = VOZ
    tmp = os.path.join(AQUI, "_frases"); os.makedirs(tmp, exist_ok=True)
    entradas, filtros, t, tiempos = [], [], 0.0, []
    for i, (nombre, texto) in enumerate(ESCENAS):
        mp3 = os.path.join(tmp, "%d_%s.mp3" % (i, nombre))
        if not os.path.exists(mp3):
            habla(texto, mp3, llave, ref)
        d = dura(mp3)
        tiempos.append({"escena": nombre, "inicio_s": round(t, 2), "dura_s": round(d, 2), "texto": texto})
        print("%-5s %5.2f s  dura %.2f" % (nombre, t, d), flush=True)
        entradas += ["-i", mp3]
        filtros.append("[%d:a]aresample=%d,aformat=channel_layouts=mono,silenceremove=start_periods=1:"
                       "start_threshold=-45dB,apad=pad_dur=%.2f[f%d]" % (i, SR, RESPIRO, i))
        t += d + RESPIRO
    mezcla = ";".join(filtros) + ";" + "".join("[f%d]" % i for i in range(len(ESCENAS))) + \
        "concat=n=%d:v=0:a=1,acompressor=threshold=-18dB:ratio=3:attack=15:release=250,highpass=f=80," \
        "loudnorm=I=-16:TP=-1.5:LRA=7[voz]" % len(ESCENAS)
    wav = os.path.join(AQUI, "PANCHO_VOZ_A_antes_de_pagar_v2.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *entradas, "-filter_complex", mezcla, "-map", "[voz]",
                    "-ar", str(SR), "-ac", "1", wav], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wav, "-b:a", "192k", wav[:-4] + ".mp3"], check=True)
    json.dump(tiempos, open(os.path.join(AQUI, "tiempos.json"), "w"), ensure_ascii=False, indent=1)
    print("listo", wav[:-4] + ".mp3", "%.2f s" % dura(wav))
