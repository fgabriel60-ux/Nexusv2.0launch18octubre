"""Vigía de clientes en WhatsApp (pedido de Carlos, 4 nov 2026).

Carlos no alcanza a leer todos los chats. Esto corre solo en Modal cada 10 minutos, hace el
barrido de TODOS los clientes (Amy incluida), y cuando alguien escribe algo que parece un
pedido o una pregunta:

  1. deja el encargo en `buzon/para_nexus2/` para que Claude lo atienda, con la instrucción
     de mandarle al cliente el acuse con tiempo de espera;
  2. le pasa a Carlos el resumen de quién pidió qué.

El vigía NO le escribe solo a los clientes: solo avisa y deja el encargo. Quien contesta es
Claude al tomar el encargo, que es donde se decide qué decirle a cada quien.

    MODAL_PROFILE=charlyfavela666 MODAL_IMAGE_BUILDER_VERSION=2025.06 modal deploy vigia_clientes_modal.py
"""
import json
import os
import pathlib
import re
import time
import urllib.request

import modal

RAIZ = "/workspaces/Nexusv2.0launch18octubre"
CHAT_CARLOS = "44522318905388@lid"
ESTADO = f"/vol{RAIZ}/entregables/vigia_clientes.json"
ACUSE_CADA = 6 * 3600

# chats que vigila; Amy no está en chat_ids.json porque no es cliente de videos
EXTRA = {"Amy · VIP Taxi": "281299671593046"}

PIDE = re.compile(
    r"\b(puedes?|podr[íi]as?|me (puedes?|podr[íi]as?)|quiero|quisiera|necesito|ocupo|me urge|urge|"
    r"c[áa]mbia|cambiar|cambio|ag[ée]ndame|m[áa]ndame|mandame|p[áa]same|pasame|h[áa]zme|hazme|"
    r"arregla|corrige|revisa|ch[ée]came|checame|no (funciona|sirve|me deja|puedo|entra)|"
    r"falla|error|no jala|cu[áa]ndo|cuando est[áa]|ya qued[óo]|qu[ée] pas[óo])\b", re.I)

imagen = modal.Image.debian_slim(python_version="3.12").env({"MODAL_IMAGE_BUILDER_VERSION": "2025.06"})
app = modal.App("vigia-clientes", image=imagen)
vol = modal.Volume.from_name("nexus-workspace")
secreto = modal.Secret.from_name("nexus-env")


def _wa(accion: str, cuerpo: dict):
    base = os.environ.get("WAAPI_BASE", "https://waapi.app/api/v1").rstrip("/") + "/instances/" + os.environ["WAAPI_INSTANCE"]
    r = urllib.request.Request(base + "/client/action/" + accion, method="POST",
                               data=json.dumps(cuerpo).encode(),
                               headers={"Authorization": "Bearer " + os.environ["WAAPI_TOKEN"],
                                        "Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=120) as x:
        return json.load(x)


@app.function(volumes={"/vol": vol}, secrets=[secreto],
              schedule=modal.Period(minutes=10), timeout=900, retries=1)
def vigilar():
    vol.reload()
    base = pathlib.Path(f"/vol{RAIZ}")
    try:
        ids = json.loads((base / "entregables/ronda_8_9_20261031/chat_ids.json").read_text())
    except Exception:
        ids = {}
    ids.update(EXTRA)
    est = {}
    pe = pathlib.Path(ESTADO)
    if pe.exists():
        try:
            est = json.loads(pe.read_text())
        except Exception:
            est = {}
    ahora = time.time()
    nuevos, encargos = [], []
    for nombre, uid in ids.items():
        cid = uid if "@" in uid else uid + "@lid"
        try:
            r = _wa("fetch-messages", {"chatId": cid, "limit": 12})
        except Exception as e:
            print("no pude leer", nombre, e)
            continue
        ms = (r.get("data") or {}).get("data") or []
        st = est.setdefault(nombre, {"visto": 0, "acuse": 0})
        pendientes = []
        for w in ms:
            d = (w.get("message") or {}).get("_data") or {}
            t = d.get("t") or 0
            if t <= st["visto"] or (d.get("id") or {}).get("fromMe"):
                continue
            txt = str(d.get("body") or "")
            tipo = str(d.get("type") or "")
            if tipo in ("ptt", "audio"):
                txt = "(nota de voz, hay que escucharla)"
            elif tipo in ("image", "video", "document"):
                txt = f"({tipo} que mandó)" + (" " + str(d.get("caption") or ""))[:120]
            if not txt.strip():
                continue
            pendientes.append((t, txt[:400], tipo))
        if not pendientes:
            continue
        st["visto"] = max(t for t, _, _ in pendientes)
        pide = [x for x in pendientes if PIDE.search(x[1]) or x[2] in ("ptt", "audio")]
        nuevos.append((nombre, pendientes, bool(pide)))
        if not pide:
            continue
        sello = time.strftime("%Y%m%d_%H%M%S")
        lineas = [f"# {nombre} escribió y parece que pide algo · {time.strftime('%d %b %Y %H:%M')} UTC", "",
                  "Lo detectó el vigía automático.", "",
                  "## Lo que escribió", ""]
        lineas += [f"- {txt}" for _, txt, _ in pendientes]
        lineas += ["", "## Reglas",
                   f"- PRIMERO el acuse: escríbele a `{cid}` que ya lo estás viendo y en cuánto le contestas.",
                   "  Da un tiempo que se pueda cumplir y no prometas resultados.",
                   "- Si pide un cambio en su video: hazlo, vuelve a calificar con Glimmer y publica el",
                   f"  resultado en su sección con POST /c/<slug>/actualizar (clave maestra).",
                   "- Si es una nota de voz, transcríbela antes de decidir.",
                   "- Avísale a Carlos con lo que hiciste y la calificación nueva.",
                   "- No le prometas tiempos al cliente más allá del acuse que ya se mandó."]
        (base / "buzon/para_nexus2" / f"{sello}_vigia_{uid}.md").write_text("\n".join(lineas))
        encargos.append(nombre)
    pe.parent.mkdir(parents=True, exist_ok=True)
    pe.write_text(json.dumps(est, ensure_ascii=False, indent=1))
    vol.commit()
    if nuevos:
        partes = ["👀 *Mensajes nuevos de clientes* (vigía automático)", ""]
        for nombre, pend, pide in nuevos:
            marca = "🔴 pide algo" if pide else "💬"
            partes.append(f"{marca} *{nombre}*")
            for _, txt, _ in pend[-3:]:
                partes.append(f"   «{txt[:120]}»")
            partes.append("")
        if encargos:
            partes.append("Dejé el encargo para atenderlos (con acuse y tiempo de espera): " + ", ".join(encargos))
        _wa("send-message", {"chatId": CHAT_CARLOS, "message": "\n".join(partes)})
    return f"{len(nuevos)} chats con mensajes nuevos, {len(encargos)} encargos"


@app.local_entrypoint()
def probar():
    print(vigilar.remote())
