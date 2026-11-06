"""Volante tamaño carta · Iglesia La Gracia de Dios (Nogales, AZ).
Pedido de papá por WhatsApp, 14 sep 2026 00:12–00:16: "Lo preparamos como el anterior".
El anterior = volante de Ministerios Casa de Oración (iglesia diana.pdf). Mismo estilo, datos nuevos.
"PARA MÁS INFO LLAMAR A" venía tachado en su captura: no va."""
import base64, json, os, sys, time, urllib.request
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
ROOT = "/workspaces/visionagenciaIAV2.0/visionagenciaIAv2.0-cripto-sim-y-corte-catania/VisionagenciaIAv2.0-main"
WAVESPEED = "https://api.wavespeed.ai/api/v3"
MODELO = "openai/gpt-image-2/edit"
VERSION = sys.argv[1] if len(sys.argv) > 1 else "v1"

IMAGENES = [
    os.path.join(AQUI, "ref_anterior_casa_de_oracion.png"),
    os.path.join(AQUI, "ref_logo_gracia_de_dios.jpg"),
    os.path.join(AQUI, "ref_local_y_telefonos.jpg"),
]

PROMPT = """Design a printable LETTER-SIZE PORTRAIT church flyer. All text in Spanish, spelled EXACTLY as written below, with accents. No other text.

IMAGE 1 is the previous flyer we made for another church: copy its STYLE and STRUCTURE (heavenly sky with soft clouds and golden light rays, elegant serif titles, gold script accents, ornamental gold flourishes, cream rounded boxes with thin gold borders, a curved blue band at the bottom). Do NOT copy any of its text, names, address or phone.
IMAGE 2 is the logo of the new church: reproduce it faithfully at the top (navy blue cross merging into a tree with navy and gold leaves, inside an open gold circle, the words "LA GRACIA DE DIOS" in navy and "IGLESIA · FAMILIA · PROPÓSITO" below). Use its navy blue and gold as the color palette of the whole flyer.
IMAGE 3 shows the new address and phones (the crossed-out line must NOT appear).

LAYOUT, top to bottom:

1) The logo from image 2, large and centered.

2) Gold script line: "Un lugar para adorar, crecer y encontrar esperanza en familia"

3) Cream box with a small open Bible and cross icon on the left and, in navy italic serif:
   "“Porque donde están dos o tres reunidos en mi nombre, allí estoy yo en medio de ellos.”"
   and below it: "Mateo 18:20"

4) Small gold script word "Pastores", then a big navy serif title on two lines:
   "JOSE MANUEL Y"
   "TERE COVARRUBIAS"

5) Heading with gold lines on both sides: "NUESTROS SERVICIOS"
   Three cream boxes side by side, each with a navy ribbon title on top and a small gold icon:
   - "DOMINGOS" — "Adoración y Predicación" — big navy "11:00 AM"
   - "MARTES" — "Oración" — big navy "7:00 PM"
   - "JUEVES" — "Adoración y Predicación" — big navy "7:00 PM"

6) A navy rounded pill with a white location pin icon and white serif text:
   "EN EL NUEVO LOCAL"
   "412 N Morley Ave"
   "Nogales, AZ 85621"

7) Two gold phone icons with big navy numbers side by side, separated by a thin gold line:
   "520-455-8753"   "520-619-9333"

8) Big gold script: "¡Acompáñanos!"

9) Curved navy band at the bottom with gold text: "La Gracia de Dios" and below, smaller white spaced capitals: "IGLESIA · FAMILIA · PROPÓSITO"

Every phone digit, time and address character must be reproduced EXACTLY. Large, high-contrast, easy to read from a distance. No watermark, no extra logos, no people. Print-ready and sharp."""


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
    d = pide({"prompt": PROMPT, "images": [uri(r) for r in IMAGENES], "aspect_ratio": "3:4", "output_format": "png"})
    urls = espera(d["data"]["id"])
    crudo = os.path.join(AQUI, "VOLANTE_GRACIA_DE_DIOS_%s.png" % VERSION)
    with urllib.request.urlopen(urls[0], timeout=300) as r:
        open(crudo, "wb").write(r.read())

    # Tamaño carta a 300 dpi: se escala a lo alto y se centra sobre fondo del color del borde
    W, H = 2550, 3300
    im = Image.open(crudo).convert("RGB")
    k = H / im.height
    im = im.resize((round(im.width * k), H), Image.LANCZOS)
    if im.width > W:
        im = im.crop(((im.width - W) // 2, 0, (im.width - W) // 2 + W, H))
    carta = Image.new("RGB", (W, H), im.getpixel((5, H // 2)))
    carta.paste(im, ((W - im.width) // 2, 0))
    carta.save(os.path.join(AQUI, "VOLANTE_GRACIA_DE_DIOS_%s_CARTA.pdf" % VERSION), resolution=300)
    carta.resize((1275, 1650), Image.LANCZOS).save(os.path.join(AQUI, "VOLANTE_GRACIA_DE_DIOS_%s_preview.jpg" % VERSION), quality=90)
    print("listo", crudo, Image.open(crudo).size, flush=True)
