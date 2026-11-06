"""v4 — solo dientes y encías (Carlos: «quiero una imagen donde no se vea la cara, la línea se desplazará y
desaparecerá, la explicación será sobre solo los dientes y encías»).
Sin cara, sin labios, sin piel y sin línea cian: el corte del maxilar superior llena el cuadro, fase de
oseointegración, estilo de la hoja de Alberto. Conteo fijo de dientes (en la v2/v3 salían de más).

Referencias:
  1) v3 (hueso poroso, luz, implante bien orientado y tapón: lo que ya se aprobó visualmente)
  2) panel PASO 5 de la hoja (f6_corona): corte sin cara, encía con borde luminoso, estilo
  3) render del modelo 3D Hunyuan: anatomía del corte
Uso: python3 gpt_solo_dientes_v4.py"""
import json, os, time, urllib.request
import gpt_transicion as v1

AQUI = v1.AQUI
DESTINO = os.path.join(AQUI, "GPT2_SOLO_DIENTES_ENCIAS_v4.png")
REFS = [
    os.path.join(AQUI, "GPT2_TRANSICION_CUADRO_749_v3.png"),
    os.path.join(v1.DENTAL, "hoja_proceso_implante", "f6_corona.png"),
    "/workspaces/visionagenciaIAV2.0/entregables/implante_dental/modelo_3d_hoja/HOJA_PASO5_hunyuan_frente.png",
]
PROMPT = (
    "Create one finished photoreal cinematic macro frame for a dental implant explainer that focuses ONLY on the teeth, "
    "gums and jawbone. Stage: osseointegration. ABSOLUTELY NO face, no lips, no skin, no nose, no person, and NO cyan "
    "cut line or divider of any kind. "
    "Image 1 shows the approved anatomy and lighting: keep its porous ivory bone texture with warm inner glow, pink "
    "glossy gum, natural ivory teeth and the titanium implant exactly as oriented there, but remove the face side "
    "completely. Image 2 is the approved style sheet panel (anatomy on a dark background, glowing gum edge). Image 3 "
    "is the 3D anatomy model. "
    "Composition, vertical 9:16: a clean cross-section of the UPPER jaw fills the centre of the frame, bone on top and "
    "the row of upper teeth hanging below the gum line. Exact tooth count, left to right: TWO natural upper teeth, "
    "each with its long root visible inside the bone; then ONE empty gap exactly one tooth wide showing healed pink "
    "gum; above that gap, inside the bone, the titanium implant with its threaded tip pointing UP and a small round "
    "healing cap sitting on the gum; then TWO natural upper teeth, each with its root visible inside the bone. "
    "Only these four teeth in the whole image, tight together with natural contacts, no lower teeth, no extra or "
    "floating teeth. The bone and gum section ends cleanly on both sides just past the outer teeth with a soft warm "
    "glowing edge. Dark deep teal background with warm amber rim light, soft shallow depth of field, anatomically "
    "clean, not gore. No text, no labels, no arrows, no watermark."
)

if __name__ == "__main__":
    cuerpo = {"prompt": PROMPT, "images": [v1.uri(r) for r in REFS], "aspect_ratio": "9:16", "output_format": "png"}
    req = urllib.request.Request(v1.WAVESPEED + "/" + v1.MODELO, data=json.dumps(cuerpo).encode(), headers=v1.CAB)
    with urllib.request.urlopen(req, timeout=300) as r:
        id_ = json.loads(r.read())["data"]["id"]
    print("job", id_, flush=True)
    json.dump({"id": id_}, open(os.path.join(AQUI, "job_v4.json"), "w"))
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
