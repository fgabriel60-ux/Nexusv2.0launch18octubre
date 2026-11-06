"""Lista de prioridades de Carlos por WhatsApp cada 10 minutos (pedido del 4 nov 2026).

Carlos tiene TDAH y el día se le llena de encargos sueltos: esto le manda SIEMPRE la misma
lista corta y ordenada, con lo que está trabado esperándolo a él primero. Corre en Modal, no
en el codespace, para que siga aunque se cierre la sesión de Claude.

    MODAL_PROFILE=charlyfavela666 MODAL_IMAGE_BUILDER_VERSION=2025.06 modal deploy prioridades_modal.py

La lista vive en el volumen, en `entregables/prioridades/carlos.json`, y Claude la actualiza
conforme avanza el día. Para apagarlo: poner "pausado": true en ese archivo, o
`modal app stop prioridades-carlos`.
"""
import json
import os
import pathlib
import urllib.request

import modal

RAIZ = "/workspaces/Nexusv2.0launch18octubre"
CHAT_CARLOS = "44522318905388@lid"
TABLERO = "https://charlyfavela666--tablero-nexus-web.us-east.modal.run/?k=i7_8usCbRdED_8lp"

imagen = (modal.Image.debian_slim(python_version="3.12")
          .env({"MODAL_IMAGE_BUILDER_VERSION": "2025.06"}))
app = modal.App("prioridades-carlos", image=imagen)
vol = modal.Volume.from_name("nexus-workspace")
secreto = modal.Secret.from_name("nexus-env")


def _mandar(texto: str):
    base = os.environ.get("WAAPI_BASE", "https://waapi.app/api/v1").rstrip("/") + "/instances/" + os.environ["WAAPI_INSTANCE"]
    r = urllib.request.Request(base + "/client/action/send-message", method="POST",
                               data=json.dumps({"chatId": CHAT_CARLOS, "message": texto}).encode(),
                               headers={"Authorization": "Bearer " + os.environ["WAAPI_TOKEN"],
                                        "Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=90) as x:
        return x.status


@app.function(volumes={"/vol": vol}, secrets=[secreto],
              schedule=modal.Period(minutes=10), timeout=300, retries=1)
def recordar():
    vol.reload()
    p = pathlib.Path(f"/vol{RAIZ}/entregables/prioridades/carlos.json")
    if not p.exists():
        return "sin lista"
    d = json.loads(p.read_text())
    if d.get("pausado"):
        return "pausado"
    pend = [t for t in d.get("tareas", []) if not t.get("hecho")]
    if not pend:
        _mandar("✅ Ya no tienes pendientes en la lista. Apago los recordatorios hasta que haya algo nuevo.")
        d["pausado"] = True
        p.write_text(json.dumps(d, ensure_ascii=False, indent=1))
        vol.commit()
        return "lista vacía"

    lineas = ["📌 *TUS PRIORIDADES AHORITA* (van por orden; haz la 1 y ya)", ""]
    for i, t in enumerate(pend[:6], 1):
        lineas.append(f"*{i}. {t['que']}*")
        if t.get("paso"):
            lineas.append(f"   → {t['paso']}")
        if t.get("porque"):
            lineas.append(f"   _{t['porque']}_")
        lineas.append("")
    hechas = len(d.get("tareas", [])) - len(pend)
    lineas += [f"Llevas {hechas} de {len(d.get('tareas', []))} 💪",
               TABLERO,
               "",
               "Dime «ya hice la 1» y la tacho, o «para los recordatorios» y los apago."]
    _mandar("\n".join(lineas))
    return f"{len(pend)} pendientes"


@app.local_entrypoint()
def probar():
    print(recordar.remote())
