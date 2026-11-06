"""Stride de Pancho Mecanico v6: el v5 con GORRA (Carlos, 19 sep: «ponle la gorra»). No hay foto de
una gorra suya, así que va una de mecánico sencilla, azul marino como el pantalón, sin logo.
v5: el v4 con un ALTERNADOR en la mano, como hook del guion A («Esta pieza te
la iban a cobrar… y no era la falla»). Carlos, 19 sep.
v4: igual que la v3 pero sin la sonrisa forzada (gesto relajado).
Original v3: su cara de la foto nueva que mando Papa el 18 sep (video de 7 s, cuadro 3.5 s) y la hoja de cara con ropa de
mecanico, caminando HACIA la camara dentro de su taller. Receta Nexus: vertical 9:16, ~82% del
alto, pies completos con ~12% de piso abajo."""
import base64, json, os, time, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
ROOT = "/workspaces/visionagenciaIAV2.0/visionagenciaIAv2.0-cripto-sim-y-corte-catania/VisionagenciaIAv2.0-main"
WAVESPEED = "https://api.wavespeed.ai/api/v3"
MODELO = "openai/gpt-image-2/edit"

CARA = os.path.join(AQUI, "foto_nueva_papa", "PANCHO_CARA_NUEVA.jpg")
HOJA = os.path.join(AQUI, "PANCHO_FACE_SHEET_1536x1024.jpg")
BASE = os.path.join(AQUI, "PANCHO_STRIDE_TALLER_v5.png")
IMAGENES = [BASE, CARA, HOJA]
DESTINO = os.path.join(AQUI, "PANCHO_STRIDE_TALLER_v6.png")

PROMPT = (
    "IMAGE 1 is the photo to edit. Keep everything exactly the same: the workshop, the light, the camera "
    "angle, his face, beard and calm natural expression, his clothes, the alternator in his right hand, and "
    "his mid-stride walk toward the camera with both boots fully visible and floor below.\n\n"

    "Change only one thing: he now wears a plain navy blue work baseball cap, worn forward with the visor "
    "facing the camera, slightly curved visor, a little worn and faded like a mechanic's everyday cap, with "
    "no logo and no text. The cap sits naturally on his head, his faded sides still visible below it, and the "
    "visor casts only a soft light shadow so his eyes stay clearly visible.\n\n"

    "Keep him the same person as IMAGE 2 (new real photo of Pancho); IMAGE 3 is his face sheet, only for "
    "identity. Candid smartphone photo look, realistic, no text, no watermark."
)


def env(n):
    for l in open(os.path.join(ROOT, ".env"), encoding="utf8", errors="replace"):
        if l.startswith(n + "="):
            return l.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


CAB = {"Authorization": "Bearer " + env("WAVESPEED_API_KEY"), "Content-Type": "application/json"}


def uri(ruta):
    tipo = "png" if ruta.lower().endswith(".png") else "jpeg"
    return "data:image/%s;base64,%s" % (tipo, base64.b64encode(open(ruta, "rb").read()).decode())


def pide(cuerpo):
    req = urllib.request.Request(WAVESPEED + "/" + MODELO, data=json.dumps(cuerpo).encode(), headers=CAB)
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read())


def espera(id_):
    for _ in range(300):
        time.sleep(3)
        req = urllib.request.Request("%s/predictions/%s/result" % (WAVESPEED, id_), headers=CAB)
        d = (json.loads(urllib.request.urlopen(req, timeout=60).read()) or {}).get("data") or {}
        if d.get("status") == "completed":
            return d["outputs"]
        if d.get("status") == "failed":
            raise RuntimeError("WaveSpeed fallo: %s" % d.get("error"))
    raise RuntimeError("se acabo la espera")


if __name__ == "__main__":
    d = pide({
        "prompt": PROMPT,
        "images": [uri(r) for r in IMAGENES],
        "aspect_ratio": "9:16",
        "output_format": "png",
    })
    urls = espera(d["data"]["id"])
    with urllib.request.urlopen(urls[0], timeout=300) as r:
        open(DESTINO, "wb").write(r.read())
    print("listo", DESTINO, flush=True)
