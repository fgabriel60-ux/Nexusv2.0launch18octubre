"""Stride de Pancho Mecanico: su cara (hoja de cara 1536x1024 del chat de Papa) con ropa de
mecanico, caminando HACIA la camara dentro de su taller. Receta Nexus: vertical 9:16, ~82% del
alto, pies completos con ~12% de piso abajo."""
import base64, json, os, time, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
ROOT = "/workspaces/visionagenciaIAV2.0/visionagenciaIAv2.0-cripto-sim-y-corte-catania/VisionagenciaIAv2.0-main"
WAVESPEED = "https://api.wavespeed.ai/api/v3"
MODELO = "openai/gpt-image-2/edit"

CARA = os.path.join(AQUI, "PANCHO_FACE_SHEET_1536x1024.jpg")
BASE = os.path.join(AQUI, "PANCHO_STRIDE_TALLER_v1.png")
IMAGENES = [BASE, CARA]
DESTINO = os.path.join(AQUI, "PANCHO_STRIDE_TALLER_v2.png")

PROMPT = (
    "IMAGE 1 is the photo to edit. Keep EVERYTHING the same: the workshop, the pickup on the ramps, "
    "the oil shelf, the red tool chests, the light, the camera angle, his pose mid-stride walking "
    "toward the camera, his framing with BOTH BOOTS fully visible above the bottom edge. Same man, "
    "same identity - use IMAGE 2 (his face sheet) to keep his face exactly: same goatee with the "
    "thin line down the chin, same mustache, same short black hair with faded sides.\n\n"

    "Change only two things:\n"
    "1) CLOTHES CLEAN AND NEAT: the grey short-sleeve work shirt is clean, freshly washed and "
    "pressed, crisp collar, fits well, with the small embroidered patch on the chest; NO grease "
    "stains, no smudges, no dirt on the shirt. The navy work trousers are clean and well fitted, "
    "the black belt neat, the boots clean brown leather. His hands and forearms clean. Keep the "
    "red shop rag folded neatly in the back pocket. He looks like a proud, professional mechanic "
    "who owns his shop.\n"
    "2) A RESTED, RELAXED FACE: well rested, fresh skin, no tired eyes, no dark circles or bags, "
    "relaxed eyebrows (not frowning), soft friendly eyes and a slight warm natural smile with "
    "closed lips, approachable and confident. Still the same man, same age, real skin texture - "
    "do not beautify into another person.\n\n"

    "Vertical 9:16, candid smartphone photo look, realistic, no text, no watermark."
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
