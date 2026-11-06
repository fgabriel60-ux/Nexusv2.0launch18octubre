"""Manda el stride v4 de Pancho (sin sonrisa forzada) al WhatsApp de Carlos por WAAPI."""
import base64, json, os, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = "/workspaces/visionagenciaIAV2.0/visionagenciaIAv2.0-cripto-sim-y-corte-catania/VisionagenciaIAv2.0-main"


def env(n, x=""):
    for l in open(os.path.join(RAIZ, ".env"), encoding="utf8", errors="replace"):
        if l.startswith(n + "="):
            return l.split("=", 1)[1].strip().strip('"').strip("'")
    return x


TOKEN, INST = env("WAAPI_TOKEN"), env("WAAPI_INSTANCE")
CHAT = "".join(c for c in env("CARLOS_TEL", "5216312470486") if c.isdigit()) + "@c.us"
API = f"https://waapi.app/api/v1/instances/{INST}/client/action/send-media"

cuerpo = {
    "chatId": CHAT,
    "mediaBase64": base64.b64encode(open(os.path.join(AQUI, "PANCHO_STRIDE_TALLER_v4.jpg"), "rb").read()).decode(),
    "mediaName": "PANCHO_STRIDE_TALLER_v4.jpg",
    "mediaCaption": "\U0001F4E6 Pancho · stride taller v4: gesto relajado, sin la sonrisa forzada",
}
req = urllib.request.Request(API, data=json.dumps(cuerpo).encode(),
                             headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})
r = json.loads(urllib.request.urlopen(req, timeout=240).read())
print((r.get("data") or {}).get("status") or r.get("status") or r)
