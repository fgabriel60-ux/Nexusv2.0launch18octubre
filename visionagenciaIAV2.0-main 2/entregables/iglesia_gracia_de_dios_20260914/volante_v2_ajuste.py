"""v2: papá, 14 sep 02:01 — "Un poco más chico los nombres de los pastores y un poco más grande la dirección".
Edita la v1 con gpt-image-2 pidiendo solo esos dos cambios."""
import os, urllib.request
from PIL import Image
from volante_gptimage2 import AQUI, espera, pide, uri

PROMPT = """This is an approved church flyer. Reproduce it EXACTLY — same background, logo, colors, fonts, ornaments, boxes, icons, every word and every number — with only TWO changes:

1) Make the pastors' names "JOSE MANUEL Y" / "TERE COVARRUBIAS" about 25% SMALLER (keep the same navy serif style, the gold word "Pastores" above and the gold flourishes on both sides).

2) Make the navy address pill about 30% BIGGER, with larger white text, using the space freed by the smaller names:
   "EN EL NUEVO LOCAL"
   "412 N Morley Ave"
   "Nogales, AZ 85621"

Keep everything else in the same order and at the same size. Do not change, add or remove any text. Every digit must stay exactly the same: 11:00 AM, 7:00 PM, 7:00 PM, 412 N Morley Ave, Nogales, AZ 85621, 520-455-8753, 520-619-9333, Mateo 18:20."""

if __name__ == "__main__":
    d = pide({"prompt": PROMPT, "images": [uri(os.path.join(AQUI, "VOLANTE_GRACIA_DE_DIOS_v1.png"))],
              "aspect_ratio": "3:4", "output_format": "png"})
    urls = espera(d["data"]["id"])
    crudo = os.path.join(AQUI, "VOLANTE_GRACIA_DE_DIOS_v2.png")
    with urllib.request.urlopen(urls[0], timeout=300) as r:
        open(crudo, "wb").write(r.read())

    W, H = 2550, 3300
    im = Image.open(crudo).convert("RGB")
    k = H / im.height
    im = im.resize((round(im.width * k), H), Image.LANCZOS)
    if im.width > W:
        im = im.crop(((im.width - W) // 2, 0, (im.width - W) // 2 + W, H))
    carta = Image.new("RGB", (W, H), im.getpixel((5, H // 2)))
    carta.paste(im, ((W - im.width) // 2, 0))
    carta.save(os.path.join(AQUI, "VOLANTE_GRACIA_DE_DIOS_v2_CARTA.pdf"), resolution=300)
    print("listo", crudo, Image.open(crudo).size, flush=True)
