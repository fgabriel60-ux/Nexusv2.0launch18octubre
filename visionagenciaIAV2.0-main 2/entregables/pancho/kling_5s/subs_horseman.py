"""Subtítulos estilo Horseman (los del gancho de la Catania, 14 sep) sobre los primeros 5 s de Pancho.

Receta de ../../catania_mariano_subs_20260914/subs_difference_sfx.py:
- Playfair Display: conector chico en cursiva / palabra protagonista grande en negrita / remate en cursiva.
- Blanco en modo difference, empujado a CONTRASTE niveles del fondo para que siempre se lea.
- Las letras van DETRÁS de Pancho: se recorta con rembg (u2net_human_seg) cuadro por cuadro y se pone
  encima de las letras. La palabra grande ocupa ~94 % del ancho para asomar por los dos lados.
- Cada palabra entra con su voz (opacidad, escala 94→100 %, subida leve en 5 cuadros), con whoosh y pop.

Entrada: PANCHO_CAMINA_HABLA_5S.mp4 (Kling + lipsync). Tiempos: palabras.json (faster-whisper).
Uso: python3 subs_horseman.py [prueba]"""
import json, math, subprocess, sys, wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = Path(__file__).resolve().parent
CATANIA = AQUI.parent.parent / "catania_mariano_subs_20260914"
BASE = AQUI / "PANCHO_CAMINA_HABLA_5S_v3.mp4"   # v3: alternador + gorra
PALABRAS = AQUI / "palabras.json"
MASCARAS = AQUI / "mascaras_pancho_v3.npy"
SALIDA = AQUI / "PANCHO_5S_SUBS_v3_1080.mp4"
WHATSAPP = AQUI / "PANCHO_5S_SUBS_v3_WHATSAPP.mp4"
SFX_WAV = AQUI / "sfx.wav"

W, H, FPS, SR = 1080, 1920, 24, 48000
COLOR = np.array([255, 255, 255], np.float32)
CONTRASTE = 110
CENTRO_Y = 0.13               # a la altura de la cabeza: el torso de Pancho tapa casi todo el ancho
F_BOLD = str(CATANIA / "fuentes" / "PlayfairDisplay[wght].ttf")
F_ITAL = str(CATANIA / "fuentes" / "PlayfairDisplay-Italic[wght].ttf")
ESTILOS = {"c": (F_ITAL, b"SemiBold Italic", 80), "M": (F_BOLD, b"Black", 180),
           "Mi": (F_ITAL, b"Black Italic", 170), "r": (F_ITAL, b"SemiBold Italic", 112)}

# (texto en pantalla, estilo, palabras de la voz que cubre); suman las 12 de palabras.json
GRUPOS = [
    [("esta", "c", 1), ("pieza", "M", 1)],
    [("te la iban a", "c", 4), ("cobrar…", "Mi", 1)],
    [("y no era", "c", 3), ("la falla.", "M", 2)],
]

voz = json.load(open(PALABRAS))
assert sum(n for g in GRUPOS for _, _, n in g) == len(voz), "no cuadran las palabras"
DUR = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                     "-of", "csv=p=0", str(BASE)]).decode())

fuentes = {}
def fuente(estilo, escala=1.0):
    ruta, var, tam = ESTILOS[estilo]
    clave = (estilo, int(tam * escala))
    if clave not in fuentes:
        f = ImageFont.truetype(ruta, clave[1]); f.set_variation_by_name(var); fuentes[clave] = f
    return fuentes[clave]

grupos, i = [], 0
for g in GRUPOS:
    lineas = []
    for texto, estilo, n in g:
        tramo = voz[i:i + n]; i += n
        palabras = texto.split()
        if estilo in ("M", "Mi"):   # que asome por los dos lados de Pancho
            escala = min(1.9, W * 0.94 / fuente(estilo).getlength(texto))
        else:
            escala = 1.0
            while fuente(estilo, escala).getlength(texto) > W * 0.9:
                escala *= 0.95
        tiempos = [w["start"] for w in tramo] if len(palabras) == n else [tramo[0]["start"]] * len(palabras)
        lineas.append((palabras, fuente(estilo, escala), tiempos, estilo))
    grupos.append(dict(lineas=lineas, inicio=min(t for l in lineas for t in l[2]), fin_voz=voz[i - 1]["end"]))
for k, g in enumerate(grupos):
    sig = grupos[k + 1]["inicio"] if k + 1 < len(grupos) else 99
    g["fin"] = min(g["fin_voz"] + 0.9, sig - 0.02) if k + 1 < len(grupos) else 99

piezas = []
for g in grupos:
    medidas = []
    for palabras, f, _, estilo in g["lineas"]:
        asc, desc = f.getmetrics()
        medidas.append(int((asc + desc) * (0.78 if estilo in ("M", "Mi") else 0.9)))
    y = H * CENTRO_Y - sum(medidas) / 2
    for (palabras, f, tiempos, estilo), alto in zip(g["lineas"], medidas):
        espacio = f.getlength(" ")
        ancho = sum(f.getlength(p) for p in palabras) + espacio * (len(palabras) - 1)
        x = 70 if estilo == "c" else (W - ancho) / 2
        for p, t in zip(palabras, tiempos):
            l, top, r, b = f.getbbox(p)
            img = Image.new("L", (int(r - l) + 8, int(b - top) + 8), 0)
            ImageDraw.Draw(img).text((4 - l, 4 - top), p, font=f, fill=255)
            asc, _ = f.getmetrics()
            piezas.append(dict(img=img, x=x + l - 4,
                               y=y + (top - asc * 0.18) - 4 - (alto * 0.08 if estilo in ("M", "Mi") else 0),
                               t=t, fin=g["fin"], protagonista=estilo in ("M", "Mi")))
            x += f.getlength(p) + espacio
        y += alto


def suave(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def capa_texto(t):
    alfa = np.zeros((H, W), np.float32)
    for p in piezas:
        if t < p["t"] - 0.001 or t > p["fin"] + 0.17:
            continue
        entra = suave((t - p["t"]) / (5 / FPS))
        op = entra * (1 - suave((t - p["fin"]) / (4 / FPS)))
        if op <= 0:
            continue
        esc = 0.94 + 0.06 * entra
        img = p["img"]
        if esc < 0.999:
            img = img.resize((max(1, int(img.width * esc)), max(1, int(img.height * esc))), Image.Resampling.BILINEAR)
        cx = p["x"] + p["img"].width / 2; cy = p["y"] + p["img"].height / 2 + 18 * (1 - entra)
        x0, y0 = int(round(cx - img.width / 2)), int(round(cy - img.height / 2))
        a = np.asarray(img, np.float32) / 255.0 * op
        xa, ya, xb, yb = max(0, x0), max(0, y0), min(W, x0 + img.width), min(H, y0 + img.height)
        if xa < xb and ya < yb:
            zona = alfa[ya:yb, xa:xb]
            np.maximum(zona, a[ya - y0:yb - y0, xa - x0:xb - x0], out=zona)
    return alfa


def cuadros():
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(BASE), "-vf",
                                   f"scale={W}:{H},fps={FPS}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)


def mascaras(todos):
    if MASCARAS.exists():
        return np.load(MASCARAS)
    from rembg import new_session, remove
    sesion = new_session("u2net_human_seg")
    out = np.zeros((len(todos), H // 2, W // 2), np.uint8)
    for n, c in enumerate(todos):
        chico = Image.fromarray(c).resize((W // 2, H // 2), Image.Resampling.BILINEAR)
        out[n] = np.array(remove(chico, session=sesion, only_mask=True, post_process_mask=True))
        if n % 24 == 0:
            print("  máscara", n, "de", len(todos), flush=True)
    np.save(MASCARAS, out)
    return out


def componer(fondo, t, m):
    alfa = capa_texto(t)
    if not alfa.any():
        return fondo
    f32 = fondo.astype(np.float32)
    dif = np.abs(f32 - COLOR)
    coef = np.array([0.299, 0.587, 0.114], np.float32)
    l_fondo, l_dif = f32 @ coef, dif @ coef
    meta = np.where(l_fondo >= 128, np.minimum(l_dif, l_fondo - CONTRASTE), np.maximum(l_dif, l_fondo + CONTRASTE))
    letras = dif + (np.clip(meta, 0, 255) - l_dif)[:, :, None]
    salida = f32 + (letras - f32) * alfa[:, :, None]
    mm = Image.fromarray(m).resize((W, H), Image.Resampling.BILINEAR).filter(ImageFilter.GaussianBlur(1.5))
    mm = np.asarray(mm, np.float32)[:, :, None] / 255.0
    salida = salida * (1 - mm) + f32 * mm       # Pancho encima de las letras
    return np.clip(salida + 0.5, 0, 255).astype(np.uint8)


# ---------- efectos de sonido (mismos que la Catania) ----------
rng = np.random.default_rng(7)
def svf(ruido, cortes, q=0.7):
    lp = bp = 0.0; out = np.empty_like(ruido)
    for n, (x, fc) in enumerate(zip(ruido, cortes)):
        f = 2 * math.sin(math.pi * min(fc, SR / 6) / SR)
        hp = x - lp - q * bp; bp += f * hp; lp += f * bp
        out[n] = bp
    return out

def whoosh(dur, f0=300, f1=4000, pico=0.45):
    n = int(dur * SR); t = np.linspace(0, 1, n)
    s = svf(rng.standard_normal(n), f0 * (f1 / f0) ** np.sin(np.pi * np.minimum(t / pico, 1) / 2), q=0.5)
    env = np.where(t < pico, (t / pico) ** 2, np.exp(-5 * (t - pico) / (1 - pico)))
    return s * env / (np.abs(s).max() + 1e-9)

def pop(freq=900, dur=0.07):
    t = np.arange(int(dur * SR)) / SR
    return np.sin(2 * np.pi * freq * t * (1 - 1.8 * t)) * np.exp(-t * 60)

def sfx():
    pista = np.zeros((int(DUR * SR) + SR, 2), np.float32)
    def pon(s, t, vol, pan=0.0):
        a = max(0, int(t * SR)); s = s[: max(0, len(pista) - a)] * vol
        pista[a:a + len(s), 0] += s * math.sqrt((1 - pan) / 2) * 1.414
        pista[a:a + len(s), 1] += s * math.sqrt((1 + pan) / 2) * 1.414
    for k, g in enumerate(grupos):
        pon(whoosh(0.38, 500, 5000, 0.55), g["inicio"] - 0.2, 0.16, (-0.35, 0.35)[k % 2])
    for p in piezas:
        if p["protagonista"]:
            pon(pop(760 + rng.integers(0, 260)), p["t"], 0.10, p["x"] / W - 0.5)
    pista = np.tanh(pista * 1.2) / 1.2
    with wave.open(str(SFX_WAV), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(pista, -1, 1) * 32767).astype("<i2").tobytes())


if __name__ == "__main__":
    todos = cuadros()
    masc = mascaras(todos)
    if len(sys.argv) > 1 and sys.argv[1] == "prueba":
        tiras = [componer(todos[int(t * FPS)], t, masc[int(t * FPS)]) for t in [0.3, 0.8, 1.6, 2.3, 3.0, 3.6, 4.5]]
        Image.fromarray(np.hstack(tiras)).resize((7 * 270, 480)).save(AQUI / "PRUEBA_SUBS.jpg", quality=88)
        raise SystemExit("-> PRUEBA_SUBS.jpg")
    sfx()
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-i", str(BASE), "-i", str(SFX_WAV), "-filter_complex",
                            "[1:a]aresample=48000,aformat=channel_layouts=stereo[v];"
                            "[v][2:a]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]",
                            "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-preset", "slow", "-crf", "18",
                            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                            str(SALIDA)], stdin=subprocess.PIPE)
    for n, c in enumerate(todos):
        enc.stdin.write(componer(c, n / FPS, masc[min(n, len(masc) - 1)]).tobytes())
    enc.stdin.close(); enc.wait()
    assert enc.returncode == 0
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(SALIDA), "-vf", "scale=720:1280", "-c:v", "libx264",
                    "-crf", "24", "-preset", "medium", "-profile:v", "baseline", "-level", "3.1", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(WHATSAPP)], check=True)
    print("listo", SALIDA)
