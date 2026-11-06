"""Manda a Carlos (su propio WhatsApp) el anuncio v2 con el 818 466 8456, para que él se lo reenvíe a Jesús."""
import base64, json, os, urllib.request
from datetime import datetime

AQUI = os.path.dirname(os.path.abspath(__file__))
ENV = "/workspaces/visionagenciaIAV2.0/visionagenciaIAv2.0-cripto-sim-y-corte-catania/VisionagenciaIAv2.0-main/.env"
env = {}
for l in open(ENV, encoding="utf8", errors="replace"):
    if "=" in l and not l.lstrip().startswith("#"):
        k, v = l.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
CHAT = "5216312470486@c.us"
URL = "https://waapi.app/api/v1/instances/" + env["WAAPI_INSTANCE"] + "/client/action/send-media"
CAB = {"Authorization": "Bearer " + env["WAAPI_TOKEN"], "Content-Type": "application/json"}

PIEZAS = [
    ("ANUNCIO_PRUEBELO_v2.jpg", "🤖 Claude: ANUNCIO v2 con el número que pidió Jesús: PÍDALO HOY 818 466 8456 (antes 627 517 7203).", False),
    ("ANUNCIO_PRUEBELO_v2_CARTA.pdf", "🤖 Claude: versión carta para imprimir, con 818 466 8456.", True),
]

recibo = []
for nombre, texto, doc in PIEZAS:
    cuerpo = {"chatId": CHAT, "mediaBase64": base64.b64encode(open(os.path.join(AQUI, nombre), "rb").read()).decode(),
              "mediaName": nombre, "mediaCaption": texto, "asDocument": doc}
    req = urllib.request.Request(URL, data=json.dumps(cuerpo).encode(), headers=CAB)
    with urllib.request.urlopen(req, timeout=280) as r:
        res = json.loads(r.read())
    estado = (res.get("data") or {}).get("status", res.get("status"))
    recibo.append({"pieza": nombre, "status": estado})
    print(nombre, estado, flush=True)

json.dump({"enviado_a": "Carlos (" + CHAT + ")", "fecha": datetime.now().isoformat(timespec="seconds"), "piezas": recibo},
          open(os.path.join(AQUI, "recibo_envio_v2_carlos.json"), "w"), ensure_ascii=False)
