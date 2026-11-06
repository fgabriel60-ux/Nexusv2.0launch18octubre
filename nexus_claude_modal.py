"""Claude Code vivo en un CPU de Modal (sandbox `nexus-claude`) con el workspace en el volumen `nexus-workspace`.

  modal run nexus_claude_modal.py::encender     # crea el sandbox (24 h máx.)
  modal shell sandbox-id / `modal container exec -it <id> bash`  → claude  (login con /login la 1.ª vez; queda en el volumen)
  claude remote-control --name nexus                             # lo ves y controlas desde claude.ai/code
  modal run nexus_claude_modal.py::apagar       # apaga el sandbox
"""
import modal

RAIZ = "/workspaces/Nexusv2.0launch18octubre"
imagen = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("curl", "git", "ffmpeg", "fonts-dejavu-core", "ca-certificates", "gnupg")
    .run_commands("curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && apt-get install -y nodejs",
                  "npm install -g @anthropic-ai/claude-code")
    .pip_install("modal", "av", "imageio-ffmpeg", "pillow", "numpy", "requests")
    .env({"HOME": "/root", "CLAUDE_CONFIG_DIR": "/vol/claude-config"})
)
app = modal.App.lookup("nexus-claude", create_if_missing=True)
vol = modal.Volume.from_name("nexus-workspace")
SECRETO = modal.Secret.from_name("nexus-env")
NOMBRE = "nexus-claude"


def encender():
    sb = modal.Sandbox.create("sleep", "infinity", app=app, image=imagen, name=NOMBRE, timeout=24 * 3600,
                              cpu=1, memory=2048, secrets=[SECRETO], workdir=RAIZ,
                              volumes={"/vol": vol})
    sb.exec("bash", "-c", f"mkdir -p /vol/claude-config && mkdir -p /workspaces && rm -rf {RAIZ} && ln -s /vol{RAIZ} {RAIZ}").wait()
    print("sandbox:", sb.object_id)


def apagar():
    modal.Sandbox.from_name("nexus-claude", NOMBRE).terminate()
    print("apagado")
