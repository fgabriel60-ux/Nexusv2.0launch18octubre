"""Carlos: «todavía se ven extrañas las cejas de la chica sonriendo». Edición puntual del cuadro 10: solo cejas y
frente relajadas; el resto de la imagen igual (el encuadre tiene que seguir sirviendo para el morph).
Uso: python3 cejas_10.py"""
import json, os, shutil, sys, time, urllib.request
sys.path.insert(0, "/workspaces/visionagenciaIAV2.0/entregables/implante_dental/gpt_transicion")
import gpt_transicion as v1

AQUI = os.path.dirname(os.path.abspath(__file__))
CUADRO = os.path.join(AQUI, "IMAGENES", "10_sonrisa_feliz.png")
RESPALDO = os.path.join(AQUI, "10_sonrisa_feliz_ANTES_CEJAS.png")
PROMPT = (
    "Precise edit of this portrait. Change ONLY her eyebrows and forehead: make the eyebrows relaxed, soft and natural "
    "for a genuinely happy laughing smile, both brows sitting slightly LOWER and level, in a gentle natural arch, with "
    "NO raised inner corners, NO pinched or worried brows, NO frown lines or tension between the brows, smooth relaxed "
    "forehead. Keep the same eyebrow thickness, shape and colour. Her eyes stay happy with soft smile lines. "
    "Preserve every other pixel exactly: same woman, same framing and crop, head position, big smile, complete teeth, "
    "lips, nose, skin texture, hair, clothing, dark teal background and lighting. Photoreal, no text, no watermark."
)

if __name__ == "__main__":
    if not os.path.exists(RESPALDO):
        shutil.copy(CUADRO, RESPALDO)
    cuerpo = {"prompt": PROMPT, "images": [v1.uri(RESPALDO)], "aspect_ratio": "9:16", "output_format": "png"}
    req = urllib.request.Request(v1.WAVESPEED + "/" + v1.MODELO, data=json.dumps(cuerpo).encode(), headers=v1.CAB)
    with urllib.request.urlopen(req, timeout=300) as r:
        id_ = json.loads(r.read())["data"]["id"]
    for _ in range(200):
        time.sleep(5)
        q = urllib.request.Request("%s/predictions/%s/result" % (v1.WAVESPEED, id_), headers=v1.CAB)
        d = (json.loads(urllib.request.urlopen(q, timeout=60).read()) or {}).get("data") or {}
        if d.get("status") == "completed":
            with urllib.request.urlopen(d["outputs"][0], timeout=300) as r:
                open(os.path.join(AQUI, "10_sonrisa_feliz_CEJAS_NUEVAS.png"), "wb").write(r.read())
            print("listo"); break
        if d.get("status") == "failed":
            raise RuntimeError(d.get("error"))
