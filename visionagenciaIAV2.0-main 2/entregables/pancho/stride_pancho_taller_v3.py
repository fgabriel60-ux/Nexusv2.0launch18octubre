"""Stride de Pancho Mecanico: su cara de la foto nueva que mando Papa el 18 sep (video de 7 s, cuadro 3.5 s) y la hoja de cara con ropa de
mecanico, caminando HACIA la camara dentro de su taller. Receta Nexus: vertical 9:16, ~82% del
alto, pies completos con ~12% de piso abajo."""
import base64, json, os, time, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
ROOT = "/workspaces/visionagenciaIAV2.0/visionagenciaIAv2.0-cripto-sim-y-corte-catania/VisionagenciaIAv2.0-main"
WAVESPEED = "https://api.wavespeed.ai/api/v3"
MODELO = "openai/gpt-image-2/edit"

CARA = os.path.join(AQUI, "foto_nueva_papa", "PANCHO_CARA_NUEVA.jpg")
HOJA = os.path.join(AQUI, "PANCHO_FACE_SHEET_1536x1024.jpg")
BASE = os.path.join(AQUI, "PANCHO_STRIDE_TALLER_v2.png")
IMAGENES = [BASE, CARA, HOJA]
DESTINO = os.path.join(AQUI, "PANCHO_STRIDE_TALLER_v3.png")

PROMPT = (
    "IMAGE 1 is the photo to edit. Keep the same workshop, the pickup on the ramps, the oil shelf, the "
    "red tool chests, the light and the camera angle. Keep him caught MID-STRIDE walking TOWARD the "
    "camera, facing it, one leg forward with a visible gap between the boots, rear heel lifted, arms "
    "swinging; vertical 9:16, he fills about 82% of the frame height, head just below the top edge, "
    "BOTH BOOTS fully visible just above the bottom edge with some floor below them.\n\n"

    "IMAGE 2 is a NEW real photo of this man (Pancho) and is the main reference for who he is. Make him "
    "look exactly like IMAGE 2: his rounder, fuller face and cheeks, his warm open smile showing a bit of "
    "his teeth, his eyes crinkled from smiling, his beard (thin mustache joined to a goatee with the thin "
    "line down the chin, and short stubble along the jaw), his short black hair with faded sides, his "
    "skin tone and his stockier, broad build with a bit of a belly. IMAGE 3 is his face sheet from other "
    "angles; use it only to keep the identity consistent.\n\n"

    "Keep the clean grey short-sleeve mechanic work shirt, navy work trousers, black belt, brown leather "
    "boots and the red rag in the pocket, fitted to his real, stockier body. He looks happy, friendly and "
    "proud of his shop. Real skin texture, same age as IMAGE 2, do not beautify him into someone else.\n\n"

    "Candid smartphone photo look, realistic, no text, no watermark."
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
