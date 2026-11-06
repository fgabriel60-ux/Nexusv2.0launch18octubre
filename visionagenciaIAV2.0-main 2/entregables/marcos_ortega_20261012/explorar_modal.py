"""Explora en Modal qué nodos MiniMax H3 trae ComfyUI y qué plantillas de flujo existen (sin GPU)."""
import modal

imagen = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("git")
    .run_commands("git clone --depth 1 https://github.com/comfyanonymous/ComfyUI /opt/ComfyUI")
    .pip_install("torch", "torchvision", "torchaudio")
    .run_commands("pip install -r /opt/ComfyUI/requirements.txt")
)
app = modal.App("explorar-comfy", image=imagen)
datos = modal.Volume.from_name("h3-comprimido-gastro")
qwen = modal.Volume.from_name("qwen-image-edit-2511")


@app.function(volumes={"/datos": datos, "/qwen": qwen}, timeout=900)
def explorar():
    import glob, json, os, subprocess, sys
    out = {}
    out["git"] = subprocess.run(["git", "-C", "/opt/ComfyUI", "log", "-1", "--format=%h %cd"], capture_output=True, text=True).stdout
    nodos = subprocess.run(["grep", "-rlEi", "minimax", "/opt/ComfyUI/comfy_extras", "/opt/ComfyUI/nodes.py"], capture_output=True, text=True).stdout
    out["archivos_nodos"] = nodos
    clases = subprocess.run(["grep", "-rhoE", "node_id=\"[A-Za-z0-9_]*(MiniMax|H3)[A-Za-z0-9_]*\"|class [A-Za-z0-9_]*MiniMax[A-Za-z0-9_]*", "/opt/ComfyUI/comfy_extras"], capture_output=True, text=True).stdout
    out["clases"] = clases
    import importlib.util
    try:
        import comfyui_workflow_templates as t
        base = os.path.dirname(t.__file__)
    except Exception:
        base = "/usr/local/lib/python3.12/site-packages"
    plantillas = [p for p in glob.glob("/usr/local/lib/python3.12/site-packages/comfyui_workflow_templates*/**/*.json", recursive=True) if "minimax" in p.lower() or "h3" in p.lower()]
    out["plantillas"] = plantillas[:40]
    for p in plantillas:
        if "fl2v" in p.lower() or "first" in p.lower() or "flf" in p.lower():
            out["plantilla_" + os.path.basename(p)] = open(p).read()[:60000]
    out["qwen"] = open("/qwen/Qwen-Image-Edit-2511/model_index.json").read() if os.path.exists("/qwen/Qwen-Image-Edit-2511/model_index.json") else os.listdir("/qwen/Qwen-Image-Edit-2511")
    out["modelos"] = subprocess.run(["find", "/datos/models", "-maxdepth", "2"], capture_output=True, text=True).stdout
    return json.dumps(out)


@app.local_entrypoint()
def main():
    import json
    r = json.loads(explorar.remote())
    open("explorar_resultado.json", "w").write(json.dumps(r, indent=1))
    for k, v in r.items():
        print("==", k, "\n", (v if isinstance(v, str) else json.dumps(v))[:1500])
