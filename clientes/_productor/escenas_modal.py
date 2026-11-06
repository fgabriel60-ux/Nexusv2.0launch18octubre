"""Escenas con IA para el productor, en UNA sola GPU: Qwen-Image-Edit-2511 hace el primer cuadro a partir de las fotos reales del cliente
y MiniMax H3 lo anima (sin voz; la voz Fish va en el armado). Lo llama producir.py; no se usa solo."""
import io, sys
import modal

sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/XV")
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/Mariano/flyers_animados")
from flyers_modal import imagen, datos, qwen
import xv_modal

app = modal.App("productor-escenas", image=imagen.add_local_python_source("flyers_modal", "xv_modal"))
NEGATIVO = "texto, letras, subtítulos, logotipos inventados, cara distinta, deforme, borroso, manos extra, dedos extra"


@app.function(gpu="A100-80GB", volumes={"/datos": datos, "/qwen": qwen}, timeout=7200)
def escenas(carpeta: str, refs: dict, cuadros: dict, tomas: list, semilla: int = 3, listos: dict = None, voces: dict = None, tam: tuple = None) -> dict:
    """refs {nombre: jpg}; cuadros {nombre: ([refs], prompt)}; listos {nombre: png ya hecho, sin Qwen};
    tomas [(nombre, cuadro, prompt, segundos)] o con último cuadro y voz que guía los labios [(nombre, cuadro, prompt, segundos, cuadro_final, voz)];
    voces {nombre: wav}; tam (ancho, alto) de H3 para más calidad (por omisión 576×1024) → {archivo: bytes}."""
    import gc, glob, json, os, subprocess, time, requests, torch
    from PIL import Image
    from diffusers import QwenImageEditPlusPipeline
    xv_modal.CARPETA = carpeta   # _flujo arma las rutas y el tamaño con estos globales
    if tam: xv_modal.ANCHO, xv_modal.ALTO = tam
    base = f"/datos/siena/{carpeta}"
    os.makedirs(base, exist_ok=True)
    for n, v in (voces or {}).items():
        open(f"{base}/{n}.wav", "wb").write(v)
    imgs = {k: Image.open(io.BytesIO(v)).convert("RGB") for k, v in refs.items()}
    for n, b in (listos or {}).items():
        Image.open(io.BytesIO(b)).convert("RGB").resize((xv_modal.ANCHO, xv_modal.ALTO), Image.LANCZOS).save(f"{base}/{n}.png")
    salida = {}
    pipe = QwenImageEditPlusPipeline.from_pretrained("/qwen/Qwen-Image-Edit-2511", torch_dtype=torch.bfloat16).to("cuda") if cuadros else None
    for n, (usar, p) in cuadros.items():
        im = pipe(image=[imgs[u] for u in usar], prompt=p, negative_prompt=NEGATIVO, true_cfg_scale=4.0, guidance_scale=1.0,
                  num_inference_steps=40, height=1280, width=720, generator=torch.Generator("cuda").manual_seed(semilla)).images[0]
        im.resize((xv_modal.ANCHO, xv_modal.ALTO), Image.LANCZOS).save(f"{base}/{n}.png")
        b = io.BytesIO(); im.save(b, "PNG"); salida[f"{n}.png"] = b.getvalue(); print("cuadro", n, flush=True)
    del pipe; gc.collect(); torch.cuda.empty_cache()
    open("/opt/ComfyUI/extra_model_paths.yaml", "w").write(
        "datos:\n  base_path: /datos/models\n  diffusion_models: diffusion_models\n  loras: loras\n  text_encoders: text_encoders\n  vae: vae\n")
    os.makedirs("/datos/siena/logs", exist_ok=True)
    log = open(f"/datos/siena/logs/comfy_{int(time.time())}.log", "w")
    subprocess.Popen(["python", "main.py", "--listen", "127.0.0.1", "--port", "8188", "--input-directory", "/datos/siena", "--output-directory", "/datos/siena/out"],
                     cwd="/opt/ComfyUI", stdout=log, stderr=subprocess.STDOUT)
    for _ in range(300):
        try:
            requests.get("http://127.0.0.1:8188/system_stats", timeout=2); break
        except Exception:
            time.sleep(2)
    for n, cuadro, prompt, seg, *extra in tomas:
        fin, voz = (list(extra) + [None, None])[:2]
        r = requests.post("http://127.0.0.1:8188/prompt", json={"prompt": xv_modal._flujo(cuadro, fin, voz, prompt, n, semilla, xv_modal._largo(seg))}).json()
        if "prompt_id" not in r:
            raise RuntimeError(json.dumps(r)[:3000])
        pid = r["prompt_id"]
        while True:
            h = requests.get(f"http://127.0.0.1:8188/history/{pid}").json()
            if pid in h:
                if h[pid].get("status", {}).get("status_str") == "error":
                    raise RuntimeError(json.dumps(h[pid]["status"])[:3000])
                break
            time.sleep(5)
        archivo = sorted(glob.glob(f"/datos/siena/out/{carpeta}/{n}_*.mp4"), key=os.path.getmtime)[-1]
        salida[f"{n}.mp4"] = open(archivo, "rb").read(); print("toma", n, flush=True)
    datos.commit()
    return salida
