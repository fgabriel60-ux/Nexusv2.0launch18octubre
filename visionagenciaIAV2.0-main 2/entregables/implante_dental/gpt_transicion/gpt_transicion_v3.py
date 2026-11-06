"""v3 del cuadro 749. Carlos sobre la v2: «salen dientes de más».
En la v2 la fila de dientes seguía más allá del corte de hueso (dos dientes flotando a la derecha, sin hueso ni
raíz) y un diente quedaba partido y repetido sobre la línea cian. Se fija el conteo exacto y se conserva todo lo
demás de la v2 (implante bien orientado, tapón en la encía, hueco, transición de labios, luz y hueso).
Uso: python3 gpt_transicion_v3.py"""
import json, os, time, urllib.request
import gpt_transicion as v1
import gpt_transicion_v2 as v2

AQUI = v1.AQUI
DESTINO = os.path.join(AQUI, "GPT2_TRANSICION_CUADRO_749_v3.png")
CONTEO = (
    " Image 6 is the latest attempt: keep its composition, lighting, bone, implant orientation and healing cap, lips "
    "and cyan cut line, but it shows TOO MANY TEETH. Fix the tooth count exactly: in the whole image there are only "
    "FOUR upper teeth. On the photographic side, left of the cyan line, exactly TWO upper teeth show between her "
    "lips, and no tooth is split or repeated by the cyan line. Then the empty gap, one tooth wide, directly under "
    "the healing cap. On the anatomical side, right of the gap, exactly TWO upper teeth, each attached to its own "
    "long root clearly visible inside the bone. The bone section, gum and tooth row all END right after that second "
    "tooth: nothing continues beyond it, no extra teeth, no floating teeth over the dark background, no lower teeth."
)

if __name__ == "__main__":
    cuerpo = {"prompt": v1.PROMPT + v2.CORRECCION + CONTEO,
              "images": [v1.uri(r) for r in v1.REFS] + [v1.uri(os.path.join(AQUI, "GPT2_TRANSICION_CUADRO_749.png")),
                                                         v1.uri(os.path.join(AQUI, "GPT2_TRANSICION_CUADRO_749_v2.png"))],
              "aspect_ratio": "9:16", "output_format": "png"}
    req = urllib.request.Request(v1.WAVESPEED + "/" + v1.MODELO, data=json.dumps(cuerpo).encode(), headers=v1.CAB)
    with urllib.request.urlopen(req, timeout=300) as r:
        id_ = json.loads(r.read())["data"]["id"]
    print("job", id_, flush=True)
    json.dump({"id": id_}, open(os.path.join(AQUI, "job_v3.json"), "w"))
    for _ in range(300):
        time.sleep(4)
        q = urllib.request.Request("%s/predictions/%s/result" % (v1.WAVESPEED, id_), headers=v1.CAB)
        d = (json.loads(urllib.request.urlopen(q, timeout=60).read()) or {}).get("data") or {}
        if d.get("status") == "completed":
            with urllib.request.urlopen(d["outputs"][0], timeout=300) as r:
                open(DESTINO, "wb").write(r.read())
            print("listo", DESTINO, flush=True); break
        if d.get("status") == "failed":
            raise RuntimeError("WaveSpeed falló: %s" % d.get("error"))
