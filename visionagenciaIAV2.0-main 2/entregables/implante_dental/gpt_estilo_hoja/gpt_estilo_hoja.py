"""GPT Image 2 (WaveSpeed openai/gpt-image-2/edit): cómo se verían los cuadros del Blender de la Mac con el
estilo de la hoja que se le mandó a Alberto (hoja_proceso_implante.png).

Referencias por imagen, en este orden:
  1) captura del viewport de Blender (encuadre y composición que manda)
  2) foto original de la chica (misma persona)
  3) la hoja de Alberto (estilo: fondo oscuro, luz cálida + turquesa, piel fotográfica, dientes naturales)
Uso: python3 gpt_estilo_hoja.py 1   |   python3 gpt_estilo_hoja.py 150"""
import base64, json, os, sys, time, urllib.request
from io import BytesIO
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
ROOT = "/workspaces/visionagenciaIAV2.0/visionagenciaIAv2.0-cripto-sim-y-corte-catania/VisionagenciaIAv2.0-main"
DENTAL = os.path.join(ROOT, "clientes", "Vision Agencia", "veneers_dental")
WAVESPEED = "https://api.wavespeed.ai/api/v3"
MODELO = "openai/gpt-image-2/edit"
FOTO = os.path.join(DENTAL, "last_frame_diente_faltante.png")
HOJA = os.path.join(DENTAL, "hoja_proceso_implante", "hoja_proceso_implante.png")

COMUN = ("The second image is the real woman: keep exactly her face, skin tone, lips, nose and smile so she is "
         "clearly the same person. The third image is the approved style sheet: match its look precisely — "
         "photoreal cinematic macro photography, dark background with deep teal and warm amber rim light, "
         "soft shallow depth of field, natural glossy skin texture with pores, natural ivory teeth with subtle "
         "translucency, healthy pink gums. The upper arch is missing one front tooth. No text, no labels, "
         "no captions, no watermark. Vertical 9:16.")
CUADROS = {
    "1": ("BLENDER_CUADRO_ACTUAL.png", "GPT2_CUADRO_1_ROSTRO.png",
          "Turn the first image, a grey 3D Blender viewport render, into a finished photoreal frame. Keep its "
          "exact camera framing and composition: the woman's face seen from the front, slightly turned, "
          "smiling with her upper teeth showing and a clear gap where one upper front tooth is missing, "
          "same crop and position of the nose and mouth. "),
    "150": ("BLENDER_CUADRO_150.png", "GPT2_CUADRO_150_CLOSEUP.png",
            "Turn the first image, a grey 3D Blender viewport close-up render, into a finished photoreal macro "
            "frame. Keep its exact framing: extreme close-up from the tip of the nose down to the lower lip, "
            "lips parted in a smile, upper front teeth and gum line visible across the frame with the gap of the "
            "missing upper front tooth in the same place, same crop and scale. Like the close-up panels of the "
            "style sheet. "),
}


def env(n):
    for l in open(os.path.join(ROOT, ".env"), encoding="utf8", errors="replace"):
        if l.startswith(n + "="):
            return l.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


CAB = {"Authorization": "Bearer " + env("WAVESPEED_API_KEY"), "Content-Type": "application/json"}


def uri(ruta, lado=1600):
    im = Image.open(ruta).convert("RGB")
    im.thumbnail((lado, lado))
    b = BytesIO(); im.save(b, "PNG")
    return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()


def espera(id_):
    for _ in range(300):
        time.sleep(4)
        req = urllib.request.Request("%s/predictions/%s/result" % (WAVESPEED, id_), headers=CAB)
        d = (json.loads(urllib.request.urlopen(req, timeout=60).read()) or {}).get("data") or {}
        if d.get("status") == "completed":
            return d["outputs"]
        if d.get("status") == "failed":
            raise RuntimeError("WaveSpeed falló: %s" % d.get("error"))
    raise RuntimeError("se acabó la espera")


def procesar_manifest(ruta):
    """Reuse this project's exact GPT Image 2 endpoint for explicit frame manifests.

    Persist job IDs before polling so reruns resume without charging another job.
    """
    from pathlib import Path
    manifest = json.loads(Path(ruta).read_text())
    for item in manifest:
        destination = Path(item['out'])
        destination.parent.mkdir(parents=True, exist_ok=True)
        receipt = destination.with_suffix('.job.json')
        if destination.exists():
            print('Existe:', destination.name, flush=True)
            continue
        if receipt.exists():
            id_ = json.loads(receipt.read_text())['id']
        else:
            body = {'prompt': item['prompt'], 'images': [uri(p) for p in item['images']],
                    'aspect_ratio': '9:16', 'output_format': 'png'}
            req = urllib.request.Request(WAVESPEED + '/' + MODELO,
                                         data=json.dumps(body).encode(), headers=CAB)
            with urllib.request.urlopen(req, timeout=300) as response:
                id_ = json.load(response)['data']['id']
            receipt.write_text(json.dumps({'id': id_, 'model': MODELO, 'frame': item['frame']}, indent=2))
        print('GPT Image 2:', item['frame'], id_, flush=True)
        url = espera(id_)[0]
        with urllib.request.urlopen(url, timeout=300) as response:
            data = response.read()
        temp = destination.with_suffix('.part')
        temp.write_bytes(data)
        with Image.open(temp) as im:
            im.verify()
        temp.replace(destination)
        print('LISTO:', destination.name, flush=True)


if __name__ == "__main__" and sys.argv[1] == '--manifest':
    procesar_manifest(sys.argv[2])
elif __name__ == "__main__":
    captura, destino, encuadre = CUADROS[sys.argv[1]]
    cuerpo = {"prompt": encuadre + COMUN,
              "images": [uri(os.path.join(AQUI, captura)), uri(FOTO), uri(HOJA)],
              "aspect_ratio": "9:16", "output_format": "png"}
    req = urllib.request.Request(WAVESPEED + "/" + MODELO, data=json.dumps(cuerpo).encode(), headers=CAB)
    with urllib.request.urlopen(req, timeout=300) as r:
        id_ = json.loads(r.read())["data"]["id"]
    print("job", id_, flush=True)
    json.dump({"id": id_, "cuadro": sys.argv[1]}, open(os.path.join(AQUI, "job_%s.json" % sys.argv[1]), "w"))
    url = espera(id_)[0]
    with urllib.request.urlopen(url, timeout=300) as r:
        open(os.path.join(AQUI, destino), "wb").write(r.read())
    print("listo", destino, url, flush=True)
