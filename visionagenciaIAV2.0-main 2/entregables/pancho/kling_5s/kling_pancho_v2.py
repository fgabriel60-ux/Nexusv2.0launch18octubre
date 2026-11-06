"""Kling 5 s de Pancho: camina HACIA la cámara en su taller mientras habla (primeros 5 s del guion A v2:
«Esta pieza te la iban a cobrar… y no era la falla.»). Parte del stride v5 (con el alternador en la mano como hook).
v2 (19 sep): la cámara retrocede más rápido, porque en la v1 se cortaban las botas desde el segundo 3.
Después se le cuadra la boca con lipsync_pancho.py. Receta: kling_caminata_hablando.py de la Catania."""
import base64, json, os, time, urllib.error, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
ROOT = "/workspaces/visionagenciaIAV2.0/visionagenciaIAv2.0-cripto-sim-y-corte-catania/VisionagenciaIAv2.0-main"
WAVESPEED = "https://api.wavespeed.ai/api/v3"
MODELO = "kwaivgi/kling-v2.1-i2v-pro"

FRAME = os.path.join(AQUI, "..", "PANCHO_STRIDE_TALLER_v5.png")
ESTADO = os.path.join(AQUI, "kling_pancho_v2_job.json")
SALIDA = os.path.join(AQUI, "pancho_caminata_v2_sin_audio.mp4")

PROMPT = (
    "The mechanic in the grey work shirt walks steadily TOWARD the camera through his workshop while "
    "TALKING to the camera: his lips move continuously in natural speech, his jaw and mouth open and close "
    "clearly, his eyebrows and cheeks move with what he says, calm and confident, looking straight into "
    "the lens. In his right hand he holds up the used car alternator toward the camera, showing it to the viewer "
    "as proof, keeping it steady at chest height without covering his face. Natural relaxed walking stride, his boots "
    "landing one after the other on the concrete floor, his free left arm swinging slightly. The camera "
    "DOLLIES BACKWARD at the SAME SPEED he walks, so the distance between him and the camera never changes "
    "and he stays EXACTLY the same size in frame from the first to the last second: his whole body stays inside the shot and his BOOTS "
    "REMAIN FULLY VISIBLE the whole time, with floor visible below them. The pickup on the ramps, the oil "
    "shelf and the red tool chests stay still behind him. Real phone-camera look, one continuous shot, no cuts."
)
NEGATIVO = (
    "closed mouth, still lips, silent face, big forced smile, feet cut off, cropped legs, boots out of frame, "
    "zoom in, camera pushing in, man getting closer or bigger, dropping the part, part changing shape, the man turning around or walking away, distorted face, changing face, "
    "extra fingers, extra limbs, warped background, text, watermark, subtitles, blur, low quality"
)


def env(n):
    for l in open(os.path.join(ROOT, ".env"), encoding="utf8", errors="replace"):
        if l.startswith(n + "="):
            return l.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


CAB = {"Authorization": "Bearer " + env("WAVESPEED_API_KEY"), "Content-Type": "application/json"}


def uri(ruta):
    return "data:image/png;base64," + base64.b64encode(open(ruta, "rb").read()).decode()


def pide(cuerpo):
    req = urllib.request.Request(WAVESPEED + "/" + MODELO, data=json.dumps(cuerpo).encode(), headers=CAB)
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(e.read().decode()[:1500])


def espera(id_):
    for i in range(400):
        time.sleep(5)
        req = urllib.request.Request("%s/predictions/%s/result" % (WAVESPEED, id_), headers=CAB)
        d = (json.loads(urllib.request.urlopen(req, timeout=60).read()) or {}).get("data") or {}
        if d.get("status") == "completed":
            return d["outputs"]
        if d.get("status") == "failed":
            raise RuntimeError("Kling fallo: %s" % d.get("error"))
        if i % 6 == 0:
            print("  estado:", d.get("status"), flush=True)
    raise RuntimeError("se acabo la espera")


if __name__ == "__main__":
    if os.path.exists(ESTADO):
        job = json.load(open(ESTADO))["id"]
        print("reanudando job", job, flush=True)
    else:
        r = pide({
            "image": uri(FRAME),
            "prompt": PROMPT,
            "negative_prompt": NEGATIVO,
            "duration": 5,
        })
        job = r["data"]["id"]
        json.dump({"id": job, "model": MODELO}, open(ESTADO, "w"), indent=2)
        print("JOB", job, flush=True)

    urls = espera(job)
    with urllib.request.urlopen(urls[0], timeout=600) as r:
        open(SALIDA, "wb").write(r.read())
    print("listo", SALIDA, flush=True)
