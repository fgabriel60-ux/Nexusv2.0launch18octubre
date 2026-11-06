"""Regla de Carlos (4 nov 2026): si el cliente no contesta su sección en 10 minutos, los
cambios se hacen solos.

Cada sección de cliente (`entregables/tablero/clientes/<slug>.json`) lleva la calificación de
Glimmer y la lista de arreglos para llegar a 8. Cuando se le publica una propuesta nueva se
guarda `propuesto_en`. Este cron revisa cada 5 minutos:

  · si el cliente ya respondió (hay un pedido suyo después de la propuesta) → no toca nada,
    manda lo que él pidió;
  · si pasaron 10 minutos sin respuesta → deja el encargo en `buzon/para_nexus2/` con TODOS
    los arreglos, para que Claude los aplique, vuelva a calificar y actualice la sección,
    y le avisa a Carlos por WhatsApp.

Nunca escribe al cliente: eso lo decide Carlos (regla 1 del AGENTS.md).

    MODAL_PROFILE=charlyfavela666 MODAL_IMAGE_BUILDER_VERSION=2025.06 modal deploy auto_aplicar_modal.py
"""
import json
import os
import pathlib
import time
import urllib.request

import modal

RAIZ = "/workspaces/Nexusv2.0launch18octubre"
CHAT_CARLOS = "44522318905388@lid"
ESPERA = 10 * 60          # los 10 minutos que pidió Carlos

imagen = modal.Image.debian_slim(python_version="3.12").env({"MODAL_IMAGE_BUILDER_VERSION": "2025.06"})
app = modal.App("auto-aplicar-cambios", image=imagen)
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
              schedule=modal.Period(minutes=5), timeout=600, retries=1)
def revisar():
    vol.reload()
    carpeta = pathlib.Path(f"/vol{RAIZ}/entregables/tablero/clientes")
    buzon = pathlib.Path(f"/vol{RAIZ}/buzon/para_nexus2")
    buzon.mkdir(parents=True, exist_ok=True)
    if not carpeta.exists():
        return "sin secciones"
    ahora = time.time()
    disparados = []
    for p in sorted(carpeta.glob("*.json")):
        d = json.loads(p.read_text())
        prop = d.get("propuesto_en")
        if not prop or d.get("auto_hecho") or not d.get("arreglos"):
            continue
        if ahora - float(prop) < ESPERA:
            continue
        # ¿contestó el cliente después de la propuesta?
        if any(float(x.get("en", 0)) > float(prop) for x in d.get("pedidos", [])):
            d["auto_hecho"] = "contestó el cliente"
            p.write_text(json.dumps(d, ensure_ascii=False))
            continue
        slug = p.stem
        sello = time.strftime("%Y%m%d_%H%M%S")
        lineas = [
            f"# AUTOMÁTICO · {d.get('cliente', slug)} no contestó en 10 min · {time.strftime('%d %b %Y %H:%M')} UTC",
            "",
            "Regla de Carlos del 4 nov 2026: si el cliente no aprueba los cambios de su sección en",
            "10 minutos, se hacen solos, se vuelve a calificar y se reporta la calificación nueva.",
            "",
            f"Video: `{d.get('video_ruta', '?')}` · Glimmer {d.get('calificacion', '?')}/10 "
            f"→ proyectada {d.get('proyectada', '?')}/10.",
            "",
            "## Arreglos a aplicar (todos, en este orden)",
            "",
        ]
        lineas += [f"{i}. {a['texto']}" + (f"  ({a['sube']})" if a.get("sube") else "")
                   for i, a in enumerate(d["arreglos"], 1)]
        lineas += [
            "",
            "## Reglas",
            "- Versiona el video, no sobreescribas el anterior.",
            "- No inventes precios, ofertas ni prueba social: si un arreglo lo pide y no hay dato real, sáltalo y dilo.",
            "- Al terminar: vuelve a calificar con Glimmer, actualiza "
            f"`entregables/tablero/clientes/{slug}.json` (calificación, arreglos nuevos y `propuesto_en`),",
            "  y avísale a Carlos con la calificación nueva. Si NO llegó a 8, dile qué falta.",
            "- No le escribas al cliente: eso lo decide Carlos.",
        ]
        (buzon / f"{sello}_auto_{slug}.md").write_text("\n".join(lineas))
        d["auto_hecho"] = time.strftime("%d/%m %H:%M")
        p.write_text(json.dumps(d, ensure_ascii=False))
        disparados.append(d.get("cliente", slug))
    if disparados:
        vol.commit()
        _mandar("🤖 *Cambios automáticos* (regla de los 10 minutos)\n\n"
                + "\n".join(f"• {c}: no contestó su sección, le aplico los arreglos y lo recalifico."
                            for c in disparados)
                + "\n\nTe paso la calificación nueva en cuanto termine. Si no llega a 8, te digo qué falta.")
    return f"{len(disparados)} disparados"


@app.local_entrypoint()
def probar():
    print(revisar.remote())
