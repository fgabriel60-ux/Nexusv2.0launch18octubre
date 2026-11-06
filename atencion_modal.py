"""Atención automática a prospectos que llegan de un anuncio (3 nov 2026).

Para qué: cuando alguien escribe «Hola, quiero más información» desde un anuncio,
contestar en menos de 5 minutos multiplica por 21 la probabilidad de calificarlo
(MIT/InsideSales, lo verificó Glimmer). Nadie puede estar pegado al celular toda
la noche, así que esto contesta solo.

Solo contesta a los clientes que Carlos haya ENCENDIDO. La lista está en el
volumen: `entregables/atencion/encendidos.json`
    {"<chatId>@lid": {"negocio": "Vicens", "ciudad": "Puebla", "activo": true}}
Si un chat no está ahí con `activo: true`, NO se le contesta nada.

  modal deploy atencion_modal.py
  Webhook de Meta:  https://charlyfavela666--atencion-nexus-web.us-east.modal.run/meta
  Probar a mano:    POST /probar  {"chatId": "...", "texto": "..."}

Lo que responde y lo que NO:
- Da la bienvenida y pide los datos que Facebook necesita para calificar al
  prospecto: giro, ciudad, qué busca y presupuesto.
- Nunca promete precios ni resultados: eso lo decide Carlos.
- Todo lo que entra y lo que contesta queda en `entregables/atencion/registro.jsonl`
  y, si es un prospecto nuevo, deja aviso en `buzon/para_nexus/` para que Carlos lo vea.
"""
import pathlib

import modal

RAIZ = "/workspaces/Nexusv2.0launch18octubre"
BASE = f"/vol{RAIZ}/entregables/atencion"

imagen = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("fastapi[standard]", "requests")
    .env({"MODAL_IMAGE_BUILDER_VERSION": "2025.06"})
)
app = modal.App("atencion-nexus", image=imagen)
vol = modal.Volume.from_name("nexus-workspace")
# WAAPI_INSTANCE / WAAPI_TOKEN para contestar, y META_VERIFY_TOKEN para el webhook.
secreto = modal.Secret.from_name("nexus-env")


@app.function(volumes={"/vol": vol}, secrets=[secreto], min_containers=0,
              scaledown_window=300, timeout=600)   # los web endpoints de Modal no admiten retries
@modal.asgi_app()
def web():
    import json
    import os
    import time

    import requests
    from fastapi import FastAPI, Request
    from fastapi.responses import JSONResponse, PlainTextResponse

    api = FastAPI()
    carpeta = pathlib.Path(BASE)

    def _encendidos() -> dict:
        p = carpeta / "encendidos.json"
        if not p.exists():
            return {}
        try:
            crudo = json.loads(p.read_text())
        except Exception:
            return {}
        # El archivo lleva una clave "_LEEME" con la explicación: no es un chat.
        return {k: v for k, v in crudo.items() if isinstance(v, dict)}

    def _apuntar(fila: dict):
        carpeta.mkdir(parents=True, exist_ok=True)
        with open(carpeta / "registro.jsonl", "a") as f:
            f.write(json.dumps(fila, ensure_ascii=False) + "\n")
        vol.commit()

    def _mandar(chat_id: str, texto: str) -> bool:
        inst = os.environ.get("WAAPI_INSTANCE", "")
        tok = os.environ.get("WAAPI_TOKEN", "")
        if not inst or not tok:
            return False
        r = requests.post(
            f"https://waapi.app/api/v1/instances/{inst}/client/action/send-message",
            json={"chatId": chat_id, "message": texto},
            headers={"Authorization": "Bearer " + tok, "Content-Type": "application/json"},
            timeout=60,
        )
        return r.ok

    def _saludo(cfg: dict) -> str:
        negocio = cfg.get("negocio", "nosotros")
        ciudad = cfg.get("ciudad", "")
        donde = f" en {ciudad}" if ciudad else ""
        return (
            f"¡Hola! Gracias por escribir a {negocio}{donde} 👋\n\n"
            "Soy el asistente y le voy a pasar su caso al encargado ahora mismo. "
            "Para que le den el precio correcto a la primera, ¿me ayuda con esto?\n\n"
            "1. ¿Qué es lo que necesita?\n"
            "2. ¿En qué colonia o zona?\n"
            "3. ¿Para cuándo lo ocupa?\n"
            "4. Si tiene una foto o las medidas, mándemelas por aquí.\n\n"
            "Con eso le cotizamos hoy mismo."
        )

    def _atender(chat_id: str, texto: str) -> dict:
        cfg = _encendidos().get(chat_id)
        if not cfg or not cfg.get("activo"):
            _apuntar({"t": time.strftime("%Y-%m-%d %H:%M:%S"), "chat": chat_id,
                      "entro": texto, "accion": "ignorado: no está encendido"})
            return {"ok": False, "motivo": "ese chat no tiene la atención encendida"}

        respuesta = _saludo(cfg)
        mandado = _mandar(chat_id, respuesta)
        _apuntar({"t": time.strftime("%Y-%m-%d %H:%M:%S"), "chat": chat_id,
                  "negocio": cfg.get("negocio", ""), "entro": texto,
                  "contesto": respuesta, "mandado": mandado})

        # Aviso para que Carlos y nexus3 lo retomen con una persona.
        avisos = pathlib.Path(f"/vol{RAIZ}/buzon/para_nexus")
        avisos.mkdir(parents=True, exist_ok=True)
        sello = time.strftime("%Y%m%d_%H%M%S")
        (avisos / f"{sello}_prospecto_{cfg.get('negocio', 'cliente')}.md").write_text(
            f"# Prospecto nuevo atendido solo · {time.strftime('%d %b %Y %H:%M')} UTC\n\n"
            f"- Negocio: {cfg.get('negocio', '?')}\n- Chat: `{chat_id}`\n"
            f"- Escribió: {texto}\n\n"
            "Ya se le mandó la bienvenida y las 4 preguntas de calificación.\n"
            "**Falta que una persona le dé precio.** No se prometió ningún precio.\n"
        )
        vol.commit()
        return {"ok": True, "mandado": mandado}

    @api.get("/meta")
    def verificar(req: Request):
        """Meta pide confirmar el webhook una vez, devolviendo su reto."""
        p = req.query_params
        esperado = os.environ.get("META_VERIFY_TOKEN", "")
        if p.get("hub.mode") == "subscribe" and esperado and p.get("hub.verify_token") == esperado:
            return PlainTextResponse(p.get("hub.challenge", ""))
        return PlainTextResponse("no", status_code=403)

    @api.post("/meta")
    async def entrante(req: Request):
        """Mensaje que llega de un anuncio de Meta."""
        cuerpo = await req.json()
        atendidos = 0
        for entrada in cuerpo.get("entry", []):
            for cambio in entrada.get("changes", []):
                valor = cambio.get("value", {}) or {}
                for m in valor.get("messages", []) or []:
                    de = m.get("from", "")
                    texto = (m.get("text", {}) or {}).get("body", "")
                    if de and _atender(f"{de}@c.us", texto).get("ok"):
                        atendidos += 1
        return JSONResponse({"ok": True, "atendidos": atendidos})

    @api.post("/probar")
    async def probar(req: Request):
        """Para probarlo sin Meta: {"chatId": "...", "texto": "..."}"""
        c = await req.json()
        return JSONResponse(_atender(c.get("chatId", ""), c.get("texto", "")))

    @api.get("/estado")
    def estado():
        enc = _encendidos()
        return JSONResponse({
            "encendidos": [k for k, v in enc.items() if v.get("activo")],
            "apagados": [k for k, v in enc.items() if not v.get("activo")],
        })

    return api
