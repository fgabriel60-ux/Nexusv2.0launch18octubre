"""Prueba de 1 h: contenedor CPU mínimo con Claude Code + tmux, sesión guardada en un volumen."""
import modal

app = modal.App("remoto-claude-prueba")
vol = modal.Volume.from_name("remoto-claude-home", create_if_missing=True)
img = (modal.Image.debian_slim(python_version="3.12")
       .apt_install("curl", "git", "tmux", "ca-certificates")
       .run_commands("curl -fsSL https://deb.nodesource.com/setup_22.x | bash -", "apt-get install -y nodejs",
                     "npm install -g @anthropic-ai/claude-code"))


@app.function(image=img, cpu=0.125, memory=512, timeout=3600, min_containers=1,
              volumes={"/root/.claude": vol})
def guardian():
    import subprocess, time
    subprocess.run(["tmux", "new-session", "-d", "-s", "cc", "-x", "200", "-y", "50"])
    t0 = time.time()
    while time.time() - t0 < 3500:
        time.sleep(30)
    vol.commit()
