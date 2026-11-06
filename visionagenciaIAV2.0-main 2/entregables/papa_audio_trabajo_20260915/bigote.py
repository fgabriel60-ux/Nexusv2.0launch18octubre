"""Carlos (16 sep): «ponles bigote mexicano a la última, no muy falso».
Edita SOLO el bigote sobre CHARROS_v2_revolucionarios.png (la de revolucionarios). Todo lo demás queda igual.
Uso: python3 bigote.py"""
import json, os, sys, time, urllib.request
sys.path.insert(0, "/workspaces/visionagenciaIAV2.0/entregables/implante_dental/gpt_transicion")
import gpt_transicion as v1

AQUI = os.path.dirname(os.path.abspath(__file__))
ORIGEN = os.path.join(AQUI, "CHARROS_v2_revolucionarios.png")
DESTINO = os.path.join(AQUI, "CHARROS_v2_revolucionarios_BIGOTE.png")
PROMPT = (
    "Precise edit: give BOTH men a natural Mexican moustache, and change nothing else. "
    "The older man on the left: a full, thick greying-black moustache that follows his upper lip and stops at the "
    "corners of the mouth, slightly bushy, trimmed, like a real man in his sixties would wear. "
    "The young man on the right: a dark moustache that blends naturally into the beard he already has, a little "
    "thicker over the upper lip than the rest of his facial hair. "
    "Both moustaches must look completely real: individual hairs with natural direction and density, soft irregular "
    "edges, matching each man's own hair colour and skin, correct shadow and lighting from the scene. "
    "NOT a costume or stick-on moustache, not symmetrical, not painted, not cartoonish, not handlebar, not curled up "
    "at the tips, not oversized. "
    "Keep every other pixel the same: same faces, eyes, nose, mouth shape, expressions, skin texture, beard, hats, "
    "bandoliers, charro jackets, neckerchiefs, poses, framing, background and sepia lighting. "
    "Photorealistic. No text, no watermark."
)

if __name__ == "__main__":
    cuerpo = {"prompt": PROMPT, "images": [v1.uri(ORIGEN)], "aspect_ratio": "1:1", "output_format": "png"}
    req = urllib.request.Request(v1.WAVESPEED + "/" + v1.MODELO, data=json.dumps(cuerpo).encode(), headers=v1.CAB)
    with urllib.request.urlopen(req, timeout=300) as r:
        id_ = json.loads(r.read())["data"]["id"]
    for _ in range(200):
        time.sleep(5)
        q = urllib.request.Request("%s/predictions/%s/result" % (v1.WAVESPEED, id_), headers=v1.CAB)
        d = (json.loads(urllib.request.urlopen(q, timeout=60).read()) or {}).get("data") or {}
        if d.get("status") == "completed":
            with urllib.request.urlopen(d["outputs"][0], timeout=300) as r:
                open(DESTINO, "wb").write(r.read())
            print("listo", DESTINO); break
        if d.get("status") == "failed":
            raise RuntimeError(d.get("error"))
