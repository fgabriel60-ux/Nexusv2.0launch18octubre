"""Fondo para la escena final del video del implante de Alberto (Veneers Dental), con GPT Image 2.
Carlos (19 sep): «crea una imagen en gpt image del fondo de la animación del video de Alberto para al final
agregar una escena, con el logo, dirección y WhatsApp en postproducción». Referencia: el cuadro 660 del video
final (el fondo teal oscuro con luces naranjas desenfocadas). El logo y los textos NO van aquí: se ponen en
post (final_alberto.py)."""
import base64, json, os, time, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
ROOT = "/workspaces/visionagenciaIAV2.0/visionagenciaIAv2.0-cripto-sim-y-corte-catania/VisionagenciaIAv2.0-main"
WAVESPEED = "https://api.wavespeed.ai/api/v3"
MODELO = "openai/gpt-image-2/edit"

REF = os.path.join(AQUI, "ref_fondo_animacion.png")
IMAGENES = [REF]
DESTINO = os.path.join(AQUI, "FONDO_CIERRE_GPT.png")

PROMPT = (
    "IMAGE 1 is a frame from a dental implant animation. Create a NEW clean vertical 9:16 background plate in "
    "EXACTLY the same visual style and color palette as the background of IMAGE 1: very dark deep teal, soft "
    "out-of-focus bokeh lights in warm orange and a few cyan ones, faint blurred technical lines, cinematic and "
    "premium. Remove the bone and teeth model completely. In the lower third place a single small, elegant, "
    "photorealistic dental implant (titanium screw with a white ceramic crown) standing upright, softly lit with "
    "a warm orange rim light, slightly out of focus, as a subtle hero detail. Keep the upper two thirds and the "
    "center mostly EMPTY and calm, slightly darker, so a logo and text can be placed there later. "
    "No text, no letters, no logo, no watermark, no people."
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
