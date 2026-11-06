"""Stride de Pancho Mecanico v4: igual que la v3 pero sin la sonrisa forzada (gesto relajado).
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
BASE = os.path.join(AQUI, "PANCHO_STRIDE_TALLER_v3.png")
IMAGENES = [BASE, CARA, HOJA]
DESTINO = os.path.join(AQUI, "PANCHO_STRIDE_TALLER_v4.png")

PROMPT = (
    "IMAGE 1 is the photo to edit. Change ONLY his facial expression. Keep everything else exactly the "
    "same: the workshop, the pickup on the ramps, the oil shelf, the red tool chests, the light, the "
    "camera angle, his clothes, his pose mid-stride walking toward the camera, and both boots fully "
    "visible with floor below them.\n\n"

    "Right now his smile looks forced and posed. Replace it with a calm, natural, relaxed expression, "
    "like a man casually walking through his own shop: mouth closed or only barely parted, at most a "
    "very slight, subtle smile at the corners of the mouth, no teeth showing, relaxed cheeks, relaxed "
    "eyes looking toward the camera with a friendly, confident, serene look. Not serious or angry, just "
    "natural and unposed.\n\n"

    "Keep him the same person as IMAGE 2 (new real photo of Pancho): same fuller face, same goatee and "
    "stubble, same short black hair with faded sides, same skin tone and age. IMAGE 3 is his face sheet, "
    "only to keep identity consistent.\n\n"

    "Candid smartphone photo look, realistic skin texture, no text, no watermark."
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
