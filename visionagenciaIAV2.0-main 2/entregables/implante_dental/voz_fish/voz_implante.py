"""Voz con Fish Audio para la escena CHICA_IMPLANTE_ESTILO_APROBADO (Carlos: «crea una voz en fish para ponerlo
en blender que explique los pasos acorde a como pasa en el video»).

Cada frase empieza en el cuadro de su marcador de Blender (30 fps, 1050 cuadros = 35 s). Si una frase dura más
que su tramo, se acelera hasta 1.25× para que no se encime con la siguiente. Salida: un solo audio de 35 s
(IMPLANTE_VOZ_35s.wav para Blender y .mp3 para escuchar) y tiempos.json con dónde quedó cada frase.

Mismo modelo y voz que ya funcionaron en veneers (voz_veneers.py): s2.1-pro-free, «Doctor carlos».
Afirmaciones médicas genéricas; confirmar con el dentista antes de publicar (p. ej. «unos meses»).
Uso: python3 voz_implante.py [reference_id]"""
import json, os, subprocess, sys, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = "/workspaces/visionagenciaIAV2.0/visionagenciaIAv2.0-cripto-sim-y-corte-catania/VisionagenciaIAv2.0-main"
API = "https://api.fish.audio/v1/tts"
MODELO = "s2.1-pro-free"
VOZ_DEF = "5e8ee00af4dd4f438d66fea8efa4baf4"   # «Doctor carlos»: masculina, calmada, educativa
FPS, CUADROS, SR = 30, 1050, 44100
DURACION = CUADROS / FPS
MARGEN = 0.12            # la frase arranca un poco después del cambio de plano
RESPIRO = 0.20           # espacio mínimo antes del siguiente marcador
TEMPO_MAX = 1.25

# (cuadro del marcador, nombre, frase, velocidad Fish)
GUION = [
    (1,    "ROSTRO",      "¿Te falta un diente? Así se reemplaza con un implante, paso a paso.", 1.0),
    (150,  "CLOSEUP",     "Este es el espacio.", 1.0),
    (200,  "ANESTESIA",   "Primero, anestesia local en la encía. No sientes dolor.", 0.96),
    (360,  "CORTE",       "Ahora, veamos por dentro.", 1.0),
    (420,  "PREPARACION", "El dentista prepara el hueso con precisión, justo donde estaba la raíz.", 0.95),
    (620,  "IMPLANTE",    "Coloca un tornillo de titanio dentro del hueso.", 0.95),
    (740,  "INTEGRACION", "Con los meses, el hueso crece a su alrededor y lo fija.", 0.95),
    (865,  "CORONA",      "Encima va el pilar, y una corona del color de tus dientes.", 0.96),
    (1000, "SONRISA",     "Y vuelves a sonreír.", 1.0),
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
    cuerpo = {"text": texto, "format": "mp3", "sample_rate": SR, "prosody": {"speed": velocidad, "volume": 0},
              "reference_id": voz}
    req = urllib.request.Request(API, data=json.dumps(cuerpo).encode(),
                                 headers={"Authorization": "Bearer " + llave, "Content-Type": "application/json",
                                          "model": MODELO})
    with urllib.request.urlopen(req, timeout=180) as r:
        datos = r.read()
    if len(datos) < 2000:
        raise SystemExit("Fish devolvió muy poco: " + datos[:300].decode("utf8", "replace"))
    open(salida, "wb").write(datos)


if __name__ == "__main__":
    llave = env("FISH_API_KEY")
    if not llave:
        raise SystemExit("falta FISH_API_KEY en VisionagenciaIAv2.0-main/.env")
    voz = sys.argv[1] if len(sys.argv) > 1 else (env("FISH_VOICE_ID") or VOZ_DEF)
    tmp = os.path.join(AQUI, "_frases"); os.makedirs(tmp, exist_ok=True)

    tiempos, entradas, filtros = [], [], []
    for i, (cuadro, nombre, texto, vel) in enumerate(GUION):
        mp3 = os.path.join(tmp, "%02d_%s.mp3" % (i, nombre))
        if not os.path.exists(mp3):
            habla(texto, mp3, llave, voz, vel)
        inicio = (cuadro - 1) / FPS + MARGEN
        siguiente = (GUION[i + 1][0] - 1) / FPS if i + 1 < len(GUION) else DURACION
        tramo = siguiente - inicio - RESPIRO
        d = dura(mp3)
        tempo = min(TEMPO_MAX, max(1.0, d / tramo))
        final = d / tempo
        tiempos.append({"marcador": nombre, "cuadro": cuadro, "inicio_s": round(inicio, 2), "dura_s": round(final, 2),
                        "tramo_s": round(tramo, 2), "tempo": round(tempo, 3), "encima": final > tramo + 0.05,
                        "texto": texto})
        entradas += ["-i", mp3]
        filtros.append("[%d:a]aresample=%d,aformat=channel_layouts=mono,atempo=%.4f,adelay=%d:all=1[f%d]"
                       % (i, SR, tempo, int(inicio * 1000), i))
        print("%-12s cuadro %4d  %5.2f s  dura %.2f/%.2f  tempo %.2f%s" % (
            nombre, cuadro, inicio, final, tramo, tempo, "  ⚠ se encima" if tiempos[-1]["encima"] else ""), flush=True)

    mezcla = ";".join(filtros) + ";" + "".join("[f%d]" % i for i in range(len(GUION))) + \
        "amix=inputs=%d:duration=longest:normalize=0,apad,atrim=0:%.3f," % (len(GUION), DURACION) + \
        "acompressor=threshold=-18dB:ratio=3:attack=15:release=250,highpass=f=80,loudnorm=I=-16:TP=-1.5:LRA=7[voz]"
    wav = os.path.join(AQUI, "IMPLANTE_VOZ_35s.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *entradas, "-filter_complex", mezcla, "-map", "[voz]",
                    "-ar", str(SR), "-ac", "1", wav], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wav, "-b:a", "192k", wav[:-4] + ".mp3"], check=True)
    json.dump(tiempos, open(os.path.join(AQUI, "tiempos.json"), "w"), ensure_ascii=False, indent=1)
    print("listo", wav, "%.2f s" % dura(wav))
