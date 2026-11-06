"""Anuncio 360 Salud basado en swipes: garantía tipo Domino's como titular, postal de 3 pasos, CTA repetido."""
import base64, json, os, time, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
ROOT = "/workspaces/visionagenciaIAV2.0/visionagenciaIAv2.0-cripto-sim-y-corte-catania/VisionagenciaIAv2.0-main"
CLI = os.path.join(ROOT, "clientes/360* salud optima")
WAVESPEED = "https://api.wavespeed.ai/api/v3"
MODELO = "openai/gpt-image-2/edit"

IMAGENES = [
    os.path.join(CLI, "360_PAREJA_CAMINANDO_v1.png"),
    os.path.join(CLI, "wa_producto_balsamo.jpg"),
    os.path.join(CLI, "etiquetas_ref/08-18_2008_2.jpg"),
    os.path.join(CLI, "WhatsApp Image 2026-08-11 at 12.37.50 PM.jpeg"),
]

PROMPT = """Design a PORTRAIT 3:4 direct-response ad (works printed on letter paper and as a Facebook post) for elderly buyers in Mexico. Spanish text spelled EXACTLY as below, with accents. Huge, bold, high-contrast sans-serif type that a 70-year-old can read from a distance. Warm, trustworthy, natural look: deep forest green, cream, and warm golden-orange accents.

REFERENCES:
- IMAGE 1: the smiling elderly couple walking hand in hand in a sunny park. Keep their faces, clothes and joy exactly. NO X-ray effect, no bones.
- IMAGE 2: the real balm jar shape (clear jar, blue lid, cream-colored balm).
- IMAGE 3: the real green label "Bálsamo Raramore – Fórmula Ancestral Tarahumara". Put THIS label on the jar.
- IMAGE 4: amber capsule bottle with beige capsules spilling out.

LAYOUT, top to bottom:

1) HEADLINE on a forest-green band at the very top, two lines, centered:
   white: "PRUÉBELO EN SU CASA."
   golden-orange, even bigger: "SI NO LE GUSTA, NO PAGA."

2) HERO PHOTO (middle ~45%): the couple from image 1 walking toward camera in the park. In the lower-right foreground, on a rustic wooden surface, the product duo: the balm jar with the green Raramore label next to the amber capsule bottle with a few capsules. On the upper-left of the photo, a round golden seal/badge with dark green text: "HOY PAGA" on top and "$0" very large in the middle.

3) A cream strip with THREE numbered steps side by side, each with a big green circle number, a simple flat icon and short text:
   "1" + WhatsApp icon + "Pídalo por WhatsApp"
   "2" + house icon + "Úselo con calma en su casa"
   "3" + hand-with-coins icon + "¿Le gustó? Paga $1,895"

4) Under the steps, one centered dark-green line: "DÚO Rar~Amore: Bálsamo REFORZADO + Cápsulas REGENERADORAS"
   and below it in italic: "Fórmula ancestral tarahumara. Primero confiamos en usted."

5) BOTTOM CTA bar, golden-orange background, dark-green bold text, very large: "PÍDALO HOY: 627 517 7203" with a WhatsApp icon on the left; under the bar, small: Facebook "f" icon + "Mereces Amarte MXN".

Digits must be exact: "$0", "$1,895", "627 517 7203". No other text, no health promises, no extra logos, no watermark. Photorealistic photo, crisp print-ready graphics."""


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
    destino = os.path.join(AQUI, "ANUNCIO_PRUEBELO_v1.png")
    with urllib.request.urlopen(urls[0], timeout=300) as r:
        open(destino, "wb").write(r.read())
    print("listo", destino, flush=True)
