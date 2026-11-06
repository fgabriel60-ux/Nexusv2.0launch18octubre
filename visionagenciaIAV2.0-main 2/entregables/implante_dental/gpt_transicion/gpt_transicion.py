"""GPT Image 2 (openai/gpt-image-2/edit): el cuadro que Carlos tiene en Blender (749, fase INTEGRACION) al
estilo de la hoja de Alberto, resolviendo de forma cinematográfica la transición entre la chica y el modelo 3D.

Referencias, en este orden:
  1) captura del viewport de Blender → encuadre, cámara y posición del corte diagonal
  2) foto original de la chica        → misma persona (piel, labios, nariz)
  3) panel PASO 4 de la hoja (f5)     → estilo y cómo la cara se abre en sección
  4) render del modelo 3D Hunyuan     → anatomía: hueso marfil, encía con borde luminoso, implante
Uso: python3 gpt_transicion.py"""
import base64, json, os, sys, time, urllib.request
from io import BytesIO
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
ROOT = "/workspaces/visionagenciaIAV2.0/visionagenciaIAv2.0-cripto-sim-y-corte-catania/VisionagenciaIAv2.0-main"
DENTAL = os.path.join(ROOT, "clientes", "Vision Agencia", "veneers_dental")
WAVESPEED = "https://api.wavespeed.ai/api/v3"
MODELO = "openai/gpt-image-2/edit"
REFS = [
    os.path.join(AQUI, "BLENDER_CUADRO_ACTUAL.png"),
    os.path.join(DENTAL, "last_frame_diente_faltante.png"),
    os.path.join(DENTAL, "hoja_proceso_implante", "f5_cicatrizacion.png"),
    "/workspaces/visionagenciaIAV2.0/entregables/implante_dental/modelo_3d_hoja/HOJA_PASO5_hunyuan_frente.png",
]
DESTINO = os.path.join(AQUI, "GPT2_TRANSICION_CUADRO_749.png")

PROMPT = (
    "Create one finished photoreal cinematic macro frame for a dental implant explainer, stage: osseointegration "
    "(the titanium implant is already healed inside the bone, with its small healing cap at the gum line, no crown yet). "
    "Image 1 is a grey 3D Blender viewport of the shot: keep its exact camera framing, scale and composition. It is "
    "a close macro: only a narrow strip of her skin and upper lip remains on the far left, bounded by the steep "
    "diagonal cut line running from the top centre-left down to the bottom left; the anatomical section fills most "
    "of the frame, with the implant slightly left of centre above the gap, two natural roots to its right inside the "
    "bone, the gum line across the middle and the row of upper teeth across the lower third. Keep that exact angle "
    "and position of the cut line and those positions. "
    "Image 2 is the real woman: keep exactly her skin tone, lips and nose so she is clearly the same person. "
    "Image 3 is the approved style sheet panel: match its look and above all its transition. "
    "Image 4 is the anatomy model to depict inside the section: ivory porous bone, pink gum with a warm glowing edge, "
    "natural ivory teeth close together, and a satin titanium threaded implant. "
    "Solve the transition between the woman and the anatomy in a brilliant, seamless way: her real face on the left "
    "flows into a clean diagonal cross-section on the right, separated by one thin luminous cyan edge that follows "
    "the curvature of her cheek and lips as if the skin were precisely sliced away, with depth and soft shadow at the "
    "edge, so the upper lip, gum and teeth continue naturally from the photographic half into the anatomical half "
    "at the same height and scale. The implant sits in the upper jaw exactly at the gap of the missing upper front "
    "tooth, pointing up into the bone, neighbouring teeth tight together with no gaps. "
    "Dark background with deep teal and warm amber rim light, soft shallow depth of field, glossy skin texture with "
    "pores, subtle internal glow on the bone section like the style sheet. Anatomically clean, not gore. "
    "No text, no labels, no captions, no watermark. Vertical 9:16."
)


def env(n):
    for l in open(os.path.join(ROOT, ".env"), encoding="utf8", errors="replace"):
        if l.startswith(n + "="):
            return l.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


CAB = {"Authorization": "Bearer " + env("WAVESPEED_API_KEY"), "Content-Type": "application/json"}


def uri(ruta, lado=1600):
    im = Image.open(ruta).convert("RGB"); im.thumbnail((lado, lado))
    b = BytesIO(); im.save(b, "PNG")
    return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()


if __name__ == "__main__":
    cuerpo = {"prompt": PROMPT, "images": [uri(r) for r in REFS], "aspect_ratio": "9:16", "output_format": "png"}
    req = urllib.request.Request(WAVESPEED + "/" + MODELO, data=json.dumps(cuerpo).encode(), headers=CAB)
    with urllib.request.urlopen(req, timeout=300) as r:
        id_ = json.loads(r.read())["data"]["id"]
    print("job", id_, flush=True)
    json.dump({"id": id_}, open(os.path.join(AQUI, "job.json"), "w"))
    for _ in range(300):
        time.sleep(4)
        q = urllib.request.Request("%s/predictions/%s/result" % (WAVESPEED, id_), headers=CAB)
        d = (json.loads(urllib.request.urlopen(q, timeout=60).read()) or {}).get("data") or {}
        if d.get("status") == "completed":
            with urllib.request.urlopen(d["outputs"][0], timeout=300) as r:
                open(DESTINO, "wb").write(r.read())
            print("listo", DESTINO, flush=True); break
        if d.get("status") == "failed":
            raise RuntimeError("WaveSpeed falló: %s" % d.get("error"))
