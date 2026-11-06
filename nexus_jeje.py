"""31 oct 2026: mudado a la cuenta carlosfavelajeje (Claude + ChatGPT + filas de GPU). Antes: Claude Code vivo en Modal (cuenta charlyfavela666) que NO se cae: sandbox `nexus-claude` + vigía programado.

  modal deploy nexus_666.py               # publica el vigía (revisa cada 5 min y recrea el sandbox si se cayó o venció)
  modal run nexus_666.py::encender        # crea el sandbox ya mismo
  modal run nexus_666.py::estado          # dice si está vivo
  modal shell <sandbox-id>  →  claude  →  /login (1.ª vez; queda en /vol/claude-config)
  Control desde el celular: escribe «descansa» o «despierta» en tu chat de WhatsApp contigo mismo (lo lee `oido` cada minuto), o abre la página `control`.

Dentro del sandbox, tmux corre `claude remote-control --name nexus` en un bucle: si el proceso se cierra, se relanza a los 5 s.
Sin login todavía, el bucle espera (no gasta) y se activa solo cuando aparece /vol/claude-config/.credentials.json.
Un sandbox dura 24 h como máximo: el vigía lo recrea al vencer (la sesión vuelve a aparecer en claude.ai/code con el mismo nombre).
"""
import modal

RAIZ = "/workspaces/Nexusv2.0launch18octubre"
NOMBRE = "nexus-claude"
imagen = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("curl", "git", "ffmpeg", "fonts-dejavu-core", "ca-certificates", "gnupg", "tmux")
    .run_commands("curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && apt-get install -y nodejs",
                  "npm install -g @anthropic-ai/claude-code @openai/codex@latest")
    .pip_install("modal", "av", "imageio-ffmpeg", "pillow", "numpy", "requests", "faster-whisper")
    .env({"HOME": "/root", "CLAUDE_CONFIG_DIR": "/vol/claude-config", "IS_SANDBOX": "1", "CODEX_HOME": "/vol/claude-config/codex", "GASTO_PERFIL": "carlosfavelajeje", "MODAL_IMAGE_BUILDER_VERSION": "2025.06"})   # IS_SANDBOX: corre como root y Carlos pidió que no pida permisos
)
app = modal.App("nexus-claude")
vol = modal.Volume.from_name("nexus-workspace")
secreto = modal.Secret.from_name("nexus-env")

SUPERVISOR = f"""
mkdir -p /vol/claude-config /workspaces && rm -rf {RAIZ} && ln -s /vol{RAIZ} {RAIZ}
cd {RAIZ}
tmux kill-server 2>/dev/null
tmux new-session -d -s claude 'while true; do
  if [ -f /vol/claude-config/.credentials.json ]; then claude remote-control --name nexus --model claude-haiku-5-5 --permission-mode bypassPermissions; fi
  sleep 5
done'
# Segunda sesión (cuenta carlosfavelajeje@gmail.com, 31 oct 2026): «nexus2», misma memoria; se comunican por {RAIZ}/buzon/
mkdir -p {RAIZ}/buzon
tmux new-session -d -s claude2 'while true; do
  if [ -f /vol/claude-config-2/.credentials.json ]; then CLAUDE_CONFIG_DIR=/vol/claude-config-2 claude remote-control --name nexus2 --permission-mode bypassPermissions; fi
  sleep 5
done'
# ChatGPT por WhatsApp, filas de Glimmer/escenas y vigía de gasto (antes se arrancaban a mano y morían al recrear el sandbox)
mkdir -p /tmp/claude-0/qa && ln -sf {RAIZ}/herramientas/wa.py /tmp/claude-0/wa.py && ln -sf {RAIZ}/herramientas/enviar_seguro.py /tmp/claude-0/enviar_seguro.py
mkdir -p /root && cp /vol/claude-config/modal-carlosfavelajeje.env /tmp/m.env && (grep -q carlosfavelajeje /root/.modal.toml 2>/dev/null || printf '[carlosfavelajeje]\ntoken_id = "%s"\ntoken_secret = "%s"\nactive = true\n' $(grep TOKEN_ID /tmp/m.env|cut -d= -f2) $(grep TOKEN_SECRET /tmp/m.env|cut -d= -f2) >> /root/.modal.toml)
cd {RAIZ} && nohup setsid python3 puente_chatgpt.py >> /vol/claude-config/codex/puente.log 2>&1 < /dev/null &
cd {RAIZ} && nohup setsid bash entregables/fila/fila.sh >> entregables/fila/runner.log 2>&1 < /dev/null &
cd {RAIZ} && nohup setsid bash entregables/fila_escenas/fila.sh >> entregables/fila_escenas/runner.log 2>&1 < /dev/null &
cd {RAIZ} && nohup setsid python3 gasto_modal.py vigilar >> entregables/vigilante_carlosfavelajeje.log 2>&1 < /dev/null &
"""


def _vivo():
    try:
        sb = modal.Sandbox.from_name("nexus-claude", NOMBRE)
        return sb if sb.poll() is None else None
    except Exception:
        return None


def _crear():
    a = modal.App.lookup("nexus-claude", create_if_missing=True)
    sb = modal.Sandbox.create("sleep", "infinity", app=a, image=imagen, name=NOMBRE, timeout=24 * 3600,
                              cpu=1.0, memory=4096, workdir=RAIZ, volumes={"/vol": vol}, secrets=[secreto])
    sb.exec("bash", "-c", SUPERVISOR).wait()
    return sb


estado_d = modal.Dict.from_name("nexus-estado", create_if_missing=True)   # {"dormido": bool, "visto": id del último mensaje atendido}
imagen_fn = modal.Image.debian_slim(python_version="3.12").pip_install("fastapi[standard]").env({"MODAL_IMAGE_BUILDER_VERSION": "2025.06"})   # el cliente dentro de Modal es más viejo que la versión de imagen por defecto de la cuenta
CHAT_CARLOS = "44522318905388@lid"   # chat de Carlos consigo mismo


def _descansar():
    estado_d["dormido"] = True
    sb = _vivo()
    if sb: sb.terminate()


def _despertar():
    estado_d["dormido"] = False
    return _vivo() or _crear()


def _avisar(texto):
    import json, os, urllib.request
    base = os.environ.get("WAAPI_BASE", "https://waapi.app/api/v1").rstrip("/") + "/instances/" + os.environ["WAAPI_INSTANCE"]
    r = urllib.request.Request(base + "/client/action/send-message", method="POST", data=json.dumps({"chatId": CHAT_CARLOS, "message": texto}).encode(),
                               headers={"Authorization": "Bearer " + os.environ["WAAPI_TOKEN"], "Content-Type": "application/json"})
    try: urllib.request.urlopen(r, timeout=30)
    except Exception as e: print("aviso falló:", str(e)[:100])


@app.function(image=imagen_fn, schedule=modal.Period(minutes=5), timeout=300, secrets=[secreto])
def vigia():
    """Despierto: lo mantiene vivo (lo recrea si cayó o venció). Dormido: se asegura de que siga apagado y no gasta."""
    if estado_d.get("dormido", False):
        if _vivo(): _vivo().terminate()
        print("dormido")
    elif _vivo() is None:
        sb = _crear(); print("recreado:", sb.object_id)
    else:
        print("vivo")


@app.function(image=imagen_fn, schedule=modal.Period(minutes=1), timeout=120, secrets=[secreto])
def oido():
    """Lee el chat de Carlos consigo mismo: «descansa» apaga el sandbox, «despierta» lo enciende. Funciona aunque Claude esté apagado."""
    import json, os, time, urllib.request
    base = os.environ.get("WAAPI_BASE", "https://waapi.app/api/v1").rstrip("/") + "/instances/" + os.environ["WAAPI_INSTANCE"]
    r = urllib.request.Request(base + "/client/action/fetch-messages", method="POST", data=json.dumps({"chatId": CHAT_CARLOS, "limit": 8}).encode(),
                               headers={"Authorization": "Bearer " + os.environ["WAAPI_TOKEN"], "Content-Type": "application/json"})
    try:
        m = json.load(urllib.request.urlopen(r, timeout=60))["data"]["data"]
    except Exception as e:
        print("sin lectura:", str(e)[:100]); return
    ms = m if isinstance(m, list) else m.get("messages", [])
    visto = estado_d.get("visto", "")
    for x in ms:
        d = x["message"]["_data"]; mid = d["id"]["id"]
        if d.get("type") != "chat" or time.time() - d["t"] > 600 or mid == visto: continue
        txt = (d.get("body") or "").strip().lower().strip("¡!.,")
        if txt in ("descansa", "despierta"):
            if mid in estado_d.get("hechos", []): continue
            estado_d["hechos"] = (estado_d.get("hechos", []) + [mid])[-30:]
            if txt == "descansa": _descansar(); _avisar("😴 Claude descansa. El sandbox de Modal quedó apagado y no gasta. Dime «despierta» para volver.")
            else: _despertar(); _avisar("✅ Claude despierta. Encendiendo el sandbox; en ~1 min aparece como «nexus» en tu app de Claude.")


@app.function(image=imagen_fn, timeout=120, secrets=[secreto])
@modal.fastapi_endpoint(method="GET")
def control(t: str = "", accion: str = ""):
    """Página con botones Descansa / Despierta para el celular. Requiere ?t=<clave> (secreto nexus-env: CONTROL_CLAVE)."""
    import os
    from fastapi.responses import HTMLResponse
    if not os.environ.get("CONTROL_CLAVE") or t != os.environ["CONTROL_CLAVE"]:
        return HTMLResponse("no autorizado", status_code=401)
    msg = ""
    if accion == "descansa": _descansar(); msg = "😴 Descansando (apagado, sin gasto)"
    elif accion == "despierta": _despertar(); msg = "✅ Despertando (en ~1 min aparece «nexus»)"
    vivo = "encendido" if _vivo() else "apagado"
    return HTMLResponse(f"""<meta name=viewport content="width=device-width,initial-scale=1"><body style="font-family:sans-serif;text-align:center;padding:40px">
<h2>Claude en Modal</h2><p>Ahora: <b>{vivo}</b></p><p>{msg}</p>
<a href="?t={t}&accion=despierta"><button style="font-size:28px;padding:20px 40px;margin:10px">☀️ Despierta</button></a><br>
<a href="?t={t}&accion=descansa"><button style="font-size:28px;padding:20px 40px;margin:10px">😴 Descansa</button></a></body>""")


@app.local_entrypoint()
def encender():
    sb = _vivo() or _crear()
    print("sandbox:", sb.object_id)


@app.local_entrypoint()
def estado():
    sb = _vivo()
    print("vivo:", sb.object_id if sb else "NO")
