"""Claude Code permanente en Modal: `claude remote-control` vive en un Sandbox CPU mínimo (centavos al día) con el workspace en un volumen,
así la sesión no se cae al cerrar el Codespace. Lo caro (GPU: Qwen, H3, Glimmer) sigue lanzándose bajo demanda y sólo cobra mientras corre.
Un vigilante (cron cada 30 min) crea el Sandbox si no existe o murió (los Sandbox duran máx. 24 h) y lo reanuda con `--continue`.
Uso:  modal deploy nexus_claude.py        (una vez; deja el vigilante corriendo)
      modal run nexus_claude.py::login     (una vez: `claude setup-token` o login interactivo; credenciales quedan en el volumen)
      modal run nexus_claude.py::estado    (¿está vivo? muestra la cola de logs)"""
import modal

app = modal.App("nexus-claude")
home = modal.Volume.from_name("claude-home", create_if_missing=True)          # credenciales + historial de sesiones de Claude Code
work = modal.Volume.from_name("nexus-workspace", create_if_missing=True)      # el repo/workspace (ya existe)
img = (modal.Image.debian_slim(python_version="3.12")
       .apt_install("curl", "git", "tmux", "ca-certificates", "ffmpeg")
       .run_commands("curl -fsSL https://deb.nodesource.com/setup_22.x | bash -", "apt-get install -y nodejs",
                     "npm install -g @anthropic-ai/claude-code")
       .pip_install("modal", "pillow", "numpy", "imageio-ffmpeg", "yt-dlp"))
VOLS = {"/home/cc": home, "/workspace": work}
ENV = {"HOME": "/home/cc", "CLAUDE_REMOTE_CONTROL_SESSION_NAME_PREFIX": "nexus-modal"}
NOMBRE = "nexus-claude"
# Secretos (se crean una sola vez desde el Codespace, nunca van en el código):
#   modal secret create nexus-env --from-dotenv /workspaces/Nexusv2.0launch18octubre/.env
#   modal secret create modal-token MODAL_TOKEN_ID=... MODAL_TOKEN_SECRET=...   (para que el Claude de allá lance trabajos de GPU)
SECRETOS = [modal.Secret.from_name("nexus-env"), modal.Secret.from_name("modal-token")]

ARRANQUE = ("cd /workspace && while true; do claude remote-control --name nexus --permission-mode acceptEdits --continue "
            "|| claude remote-control --name nexus --permission-mode acceptEdits; sleep 5; done")


@app.function(image=img, schedule=modal.Cron("*/30 * * * *"), timeout=300)
def vigilante():
    """Si el Sandbox no existe o ya murió, lo crea de nuevo; si está vivo no hace nada."""
    try:
        sb = modal.Sandbox.from_name("nexus-claude", NOMBRE)
        if sb.poll() is None:
            print("vivo"); return
    except modal.exception.NotFoundError:
        pass
    sb = modal.Sandbox.create("bash", "-lc", ARRANQUE, app=app, image=img, name=NOMBRE, volumes=VOLS, secrets=SECRETOS,
                              env=ENV, cpu=0.25, memory=1024, timeout=24 * 3600, workdir="/workspace")
    print("creado", sb.object_id)


@app.local_entrypoint()
def login():
    """Abre una shell dentro de la imagen con los volúmenes para autenticar Claude Code una sola vez (`claude setup-token` o `claude`)."""
    import subprocess
    subprocess.run(["modal", "shell", "--image", "debian_slim", "--volume", "claude-home", "--cmd", "bash"], check=False)
    print("Si prefieres: modal shell nexus_claude.py::vigilante  y dentro ejecuta `HOME=/home/cc claude`")


@app.local_entrypoint()
def estado():
    try:
        sb = modal.Sandbox.from_name("nexus-claude", NOMBRE)
    except modal.exception.NotFoundError:
        print("no hay Sandbox (espera al vigilante o ejecuta: modal run nexus_claude.py::vigilante)"); return
    print("vivo" if sb.poll() is None else f"terminó con {sb.poll()}")
