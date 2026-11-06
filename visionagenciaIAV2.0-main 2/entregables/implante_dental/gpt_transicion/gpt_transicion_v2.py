"""v2 del cuadro 749 (fase INTEGRACION): misma composición, estilo y transición que la v1, que se vio muy bien,
corrigiendo sus dos errores anatómicos:
  1) el implante salió al revés (cabeza arriba en el hueso, rosca hacia el diente);
  2) ya había un diente bajo el implante (en oseointegración todavía no hay corona).
Se reutilizan referencias y prompt de gpt_transicion.py y se añade la v1 como 5.ª referencia de estilo.
Uso: python3 gpt_transicion_v2.py"""
import json, os, time, urllib.request
import gpt_transicion as v1

AQUI = v1.AQUI
DESTINO = os.path.join(AQUI, "GPT2_TRANSICION_CUADRO_749_v2.png")
CORRECCION = (
    " Image 5 is a previous attempt: keep its excellent look, lighting, bone texture and the way the lips flow into "
    "the section, but fix these two anatomical errors. FIRST: this is the UPPER jaw, so the implant must be oriented "
    "with its narrow threaded tip pointing UP, deep inside the porous bone, and its flat head at the BOTTOM, at the "
    "gum line, covered by a small round titanium healing cap that sits on the pink gum. SECOND: there is NO tooth "
    "under the implant yet — directly below the healing cap there is a clear empty gap in the row of upper teeth, "
    "exactly one tooth wide, showing only healed pink gum; the neighbouring teeth on both sides stay tight and "
    "natural. Two natural roots of the neighbouring teeth remain visible inside the bone to the right."
)

if __name__ == "__main__":
    cuerpo = {"prompt": v1.PROMPT + CORRECCION,
              "images": [v1.uri(r) for r in v1.REFS] + [v1.uri(os.path.join(AQUI, "GPT2_TRANSICION_CUADRO_749.png"))],
              "aspect_ratio": "9:16", "output_format": "png"}
    req = urllib.request.Request(v1.WAVESPEED + "/" + v1.MODELO, data=json.dumps(cuerpo).encode(), headers=v1.CAB)
    with urllib.request.urlopen(req, timeout=300) as r:
        id_ = json.loads(r.read())["data"]["id"]
    print("job", id_, flush=True)
    json.dump({"id": id_}, open(os.path.join(AQUI, "job_v2.json"), "w"))
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
