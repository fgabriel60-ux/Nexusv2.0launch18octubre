"""Hoja tamaño carta 360 Salud: pareja con rayos X + Facebook en la esquina + pague después."""
import base64, json, os, time, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
ROOT = "/workspaces/visionagenciaIAV2.0/visionagenciaIAv2.0-cripto-sim-y-corte-catania/VisionagenciaIAv2.0-main"
CLI = os.path.join(ROOT, "clientes/360* salud optima")
WAVESPEED = "https://api.wavespeed.ai/api/v3"
MODELO = "openai/gpt-image-2/edit"

IMAGENES = [
    os.path.join(AQUI, "ref_jesus_pareja_rayosx.jpg"),
    os.path.join(CLI, "360_PAREJA_CAMINANDO_v1.png"),
    os.path.join(AQUI, "ref_facebook.jpg"),
]

PROMPT = """Design a printable LETTER-SIZE PORTRAIT flyer (8.5 x 11 in) for elderly readers in Mexico. All text in Spanish, spelled EXACTLY as written below, with accents. Very large, high-contrast, bold, easy-to-read sans-serif type.

IMAGE 1 is the client's approved artwork and is the LAW for the photo: the smiling elderly couple walking hand in hand in a sunny park, with the glowing translucent blue X-RAY effect showing the leg bones and knees on both of them. Keep the couple, poses, clothes and X-ray legs. IMAGE 2 is the same couple in high resolution: use it for sharp faces, skin and fabric detail. Remove the small white subtitle word that floats over their chests in image 1.

LAYOUT, top to bottom:

1) TOP (upper ~60% of the sheet): the photo of the couple, full width. Headline over the top of the photo, huge: first line white "MÚSCULOS", second line warm orange/gold "Y ESPALDA" (same style as image 1, but crisp and correctly accented).

   BOTTOM-RIGHT CORNER OF THE PHOTO: a rounded white card with a soft shadow, clearly readable, overlapping the photo (it may cover the feet, that is fine). Inside the card: the blue Facebook "f" logo, then in bold dark text "Mereces Amarte MXN", below it a green WhatsApp icon and "627 517 7203". Take the page name from IMAGE 3.

2) BOTTOM (lower ~40%): a clean cream/white panel with a thin forest-green border, containing:

   Big bold forest-green headline: "PRUÉBELO PRIMERO. PAGUE DESPUÉS."

   Dark text: "Si Rar~Amore le gustó, deposite $ ________ en:"

   Two side-by-side boxes of equal size:
   Left box, navy blue title "BBVA", then large digits "4152 3146 1931 1049", then "Jesús Armando Gutiérrez Corral".
   Right box, title "BANCOPPEL", then large digits "4169 1606 2188 4262", then "Rosalba Reyes Zapien".

   Small line under the boxes: "En ventanilla, cajero u OXXO"

   A green band at the very bottom with white text: "Mande foto de su comprobante por WhatsApp: 627 517 7203"
   and under it, smaller: "Confiamos en usted. ¡Gracias por su honestidad!"

The account digits must be reproduced EXACTLY, digit by digit, grouped in fours. No other text, no extra logos, no watermark. Warm, trustworthy, natural-health look (forest green, cream, gold accents), print-ready and sharp."""


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
        "aspect_ratio": "3:4",
        "output_format": "png",
    })
    urls = espera(d["data"]["id"])
    destino = os.path.join(AQUI, "HOJA_PAGUE_DESPUES_v1.png")
    with urllib.request.urlopen(urls[0], timeout=300) as r:
        open(destino, "wb").write(r.read())
    print("listo", destino, flush=True)
