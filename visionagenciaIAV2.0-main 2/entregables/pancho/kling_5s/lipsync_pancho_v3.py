"""Lip sync de la caminata de Pancho con su voz (primeros 5 s del guion A v2), con
wavespeed-ai/infinitetalk/video-to-video. Receta: lipsync_caminata.py de la Catania."""
import base64, json, os, time, urllib.error, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
ROOT = "/workspaces/visionagenciaIAV2.0/visionagenciaIAv2.0-cripto-sim-y-corte-catania/VisionagenciaIAv2.0-main"
WAVESPEED = "https://api.wavespeed.ai/api/v3"
MODELO = "wavespeed-ai/infinitetalk/video-to-video"

JOB_KLING = os.path.join(AQUI, "kling_pancho_v3_job.json")
AUDIO = os.path.join(AQUI, "audio_5s.mp3")
ESTADO = os.path.join(AQUI, "lipsync_pancho_v3_job.json")
SALIDA = os.path.join(AQUI, "PANCHO_CAMINA_HABLA_5S_v3.mp4")

PROMPT = (
    "A mechanic in a grey work shirt and navy cap walks toward the camera inside his workshop holding up a car alternator, speaking to the "
    "camera. Keep his face, his walk and the background exactly as they are; only his mouth and "
    "jaw move in sync with the speech."
)


def env(n):
    for l in open(os.path.join(ROOT, ".env"), encoding="utf8", errors="replace"):
        if l.startswith(n + "="):
            return l.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


CAB = {"Authorization": "Bearer " + env("WAVESPEED_API_KEY"), "Content-Type": "application/json"}


def resultado(id_):
    req = urllib.request.Request("%s/predictions/%s/result" % (WAVESPEED, id_), headers=CAB)
    return (json.loads(urllib.request.urlopen(req, timeout=60).read()) or {}).get("data") or {}


def espera(id_, etiqueta):
    for i in range(400):
        d = resultado(id_)
        if d.get("status") == "completed":
            return d["outputs"]
        if d.get("status") == "failed":
            raise RuntimeError("%s fallo: %s" % (etiqueta, d.get("error")))
        if i % 6 == 0:
            print("  %s: %s" % (etiqueta, d.get("status")), flush=True)
        time.sleep(5)
    raise RuntimeError("se acabo la espera de " + etiqueta)


def pide(cuerpo):
    req = urllib.request.Request(WAVESPEED + "/" + MODELO, data=json.dumps(cuerpo).encode(), headers=CAB)
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(e.read().decode()[:1500])


if __name__ == "__main__":
    url_video = espera(json.load(open(JOB_KLING))["id"], "kling")[0]
    print("video de entrada:", url_video[:90], flush=True)
    audio_uri = "data:audio/mpeg;base64," + base64.b64encode(open(AUDIO, "rb").read()).decode()

    if os.path.exists(ESTADO):
        job = json.load(open(ESTADO))["id"]
        print("reanudando job", job, flush=True)
    else:
        r = pide({"video": url_video, "audio": audio_uri, "prompt": PROMPT, "resolution": "720p", "seed": -1})
        job = r["data"]["id"]
        json.dump({"id": job, "model": MODELO}, open(ESTADO, "w"), indent=2)
        print("JOB", job, flush=True)

    urls = espera(job, "lipsync")
    with urllib.request.urlopen(urls[0], timeout=600) as r:
        open(SALIDA, "wb").write(r.read())
    print("listo", SALIDA, flush=True)
