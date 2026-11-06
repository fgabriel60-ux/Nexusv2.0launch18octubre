"""Stride de Pancho Mecanico: su cara (hoja de cara 1536x1024 del chat de Papa) con ropa de
mecanico, caminando HACIA la camara dentro de su taller. Receta Nexus: vertical 9:16, ~82% del
alto, pies completos con ~12% de piso abajo."""
import base64, json, os, time, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
ROOT = "/workspaces/visionagenciaIAV2.0/visionagenciaIAv2.0-cripto-sim-y-corte-catania/VisionagenciaIAv2.0-main"
WAVESPEED = "https://api.wavespeed.ai/api/v3"
MODELO = "openai/gpt-image-2/edit"

CARA = os.path.join(AQUI, "PANCHO_FACE_SHEET_1536x1024.jpg")
TALLER = os.path.join(AQUI, "REF_TALLER_mini.jpg")
IMAGENES = [CARA, TALLER]
DESTINO = os.path.join(AQUI, "PANCHO_STRIDE_TALLER_v1.png")

PROMPT = (
    "IMAGE 1 is the face sheet of the man: six views of the SAME real man. Keep his face EXACTLY: "
    "same face shape, same eyes, same nose, the same thick black goatee with the thin line down the "
    "chin and the mustache, the same short black hair with the faded sides. He is a Mexican man in "
    "his forties, sturdy build. Do not beautify, do not make him younger.\n\n"

    "IMAGE 2 shows his auto repair workshop and is the reference for the setting: an open garage "
    "with corrugated metal walls, a pickup truck up on the ramps, the tall metal shelf full of oil "
    "bottles and parts, red tool chests, a worn concrete floor with oil stains, a bright open door "
    "in the back. Use that setting; ignore the person in image 2.\n\n"

    "Dress him as a REAL working mechanic: a grey short-sleeve work shirt with a small embroidered "
    "patch on the chest, buttoned, sleeves showing his forearms, navy blue work trousers, a black "
    "belt, a red shop rag hanging from his back pocket, brown leather work boots. Honest light "
    "grease smudges on his hands and a little on the shirt. No cap, so his hair and face read "
    "clearly.\n\n"

    "Compose a TALL VERTICAL 9:16 PORTRAIT frame, much taller than wide, of that man CAUGHT "
    "MID-STRIDE WALKING TOWARD THE CAMERA through the middle of his workshop: one leg clearly "
    "forward with a visible gap between the boots, the rear heel lifted off the floor, arms "
    "swinging opposite to the legs. He is facing the camera with a calm confident look. Not "
    "standing, not posing.\n\n"

    "FRAMING, this is the important part: his WHOLE BODY is inside the frame and HIS FEET ARE NEVER "
    "CUT OFF OR HIDDEN. He fills about 82% of the frame height - the top of his head just below the "
    "top edge, BOTH BOOTS fully visible just above the bottom edge, and about 12% of concrete floor "
    "visible below his boots. Nothing covers his legs or his boots. The workshop fills the frame "
    "behind him.\n\n"

    "Shot on a smartphone, candid documentary photograph, NOT a studio portrait and NOT a 3D "
    "render: 26mm lens, wide depth of field, daylight coming in from the open garage door mixed "
    "with the fluorescent tubes, visible skin texture and pores, slightly desaturated like an "
    "unedited phone photo. No text, no watermark, no other people."
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
