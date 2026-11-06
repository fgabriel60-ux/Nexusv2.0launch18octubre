"""Pájaro mecánico de nitinol · video realista (Qwen-Image-Edit-2511 + MiniMax H3 fl2va fp8 + LoRA turbo 8 pasos).

Todo se define en un JSON de trabajos (carpeta trabajos/):
  cuadros: {"paso": "cuadros", "trabajos": [{"nombre", "refs": [png en refs/ o cuadros/], "prompt", "semilla"}]}
  clips:   {"paso": "clips", "trabajos": [{"nombre", "inicio", "fin" (opcional), "prompt", "semilla", "largo"}]}
Una sola GPU (A100-80GB), sin starmap.
Uso: MODAL_PROFILE=fabelagabriel645 modal run pajaro_modal.py --trabajos trabajos/r1_cuadros.json
"""
import io, json, pathlib
import modal

ANCHO, ALTO = 576, 1024          # H3: múltiplos de 32
CARPETA = "pajaro_nitinol"

imagen = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("git", "ffmpeg")
    .run_commands("git clone --depth 1 https://github.com/comfyanonymous/ComfyUI /opt/ComfyUI")
    .pip_install("torch", "torchvision", "torchaudio")
    .run_commands("pip install -r /opt/ComfyUI/requirements.txt")
    .pip_install("git+https://github.com/huggingface/diffusers", "transformers", "accelerate", "pillow", "requests")
)
app = modal.App("pajaro-nitinol-realista", image=imagen)
datos = modal.Volume.from_name("h3-comprimido-gastro")
qwen = modal.Volume.from_name("qwen-image-edit-2511")

NEG = ("feathers, real bird, animal head, beak, eyes, fur, plush, cartoon, illustration, drawing, diagram, text, letters, labels, numbers, watermark, "
       "deformed hands, extra fingers, six fingers, fused fingers, blurry, low quality, burnt textures")


@app.function(gpu="A100-80GB", volumes={"/qwen": qwen}, timeout=3600)
def cuadros(refs: dict, trabajos: list) -> dict:
    import torch
    from PIL import Image
    from diffusers import QwenImageEditPlusPipeline
    pipe = QwenImageEditPlusPipeline.from_pretrained("/qwen/Qwen-Image-Edit-2511", torch_dtype=torch.bfloat16).to("cuda")
    imgs = {k: Image.open(io.BytesIO(v)).convert("RGB") for k, v in refs.items()}
    salida = {}
    for t in trabajos:
        img = pipe(image=[imgs[r] for r in t["refs"]], prompt=t["prompt"], negative_prompt=t.get("neg", NEG),
                   true_cfg_scale=4.0, guidance_scale=1.0, num_inference_steps=40, height=1280, width=720,
                   generator=torch.Generator("cuda").manual_seed(t.get("semilla", 5))).images[0]
        b = io.BytesIO(); img.save(b, "PNG"); salida[t["nombre"]] = b.getvalue()
        print("cuadro", t["nombre"], flush=True)
    return salida


def _flujo(t):
    f = {
        "6": {"class_type": "UNETLoader", "inputs": {"unet_name": "minimax_h3_fl2va_pruned_fp8_scaled.safetensors", "weight_dtype": "default"}},
        "121": {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["6", 0], "lora_name": "minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors", "strength_model": 1.0}},
        "13": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors", "type": "minimax", "device": "default"}},
        "11": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_video_vae_fp16.safetensors"}},
        "24": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_audio_vae_fp32.safetensors"}},
        "30": {"class_type": "LoadImage", "inputs": {"image": f"{CARPETA}/{t['inicio']}.png"}},
        "104": {"class_type": "MiniMaxH3ImageToVideo", "inputs": {"clip": ["13", 0], "vae": ["11", 0], "prompt": t["prompt"], "width": ANCHO, "height": ALTO,
                                                                  "length": t.get("largo", 121), "first_frame": ["30", 0]}},
        "15": {"class_type": "RandomNoise", "inputs": {"noise_seed": t.get("semilla", 2)}},
        "17": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "res_multistep"}},
        "9": {"class_type": "BasicScheduler", "inputs": {"model": ["121", 0], "scheduler": "simple", "steps": 8, "denoise": 1.0}},
        "16": {"class_type": "BasicGuider", "inputs": {"model": ["121", 0], "conditioning": ["104", 0]}},
        "14": {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["15", 0], "guider": ["16", 0], "sampler": ["17", 0], "sigmas": ["9", 0], "latent_image": ["104", 1]}},
        "10": {"class_type": "VAEDecode", "inputs": {"samples": ["14", 0], "vae": ["11", 0]}},
        "23": {"class_type": "VAEDecodeAudio", "inputs": {"samples": ["14", 0], "vae": ["24", 0]}},
        "91": {"class_type": "CreateVideo", "inputs": {"images": ["10", 0], "audio": ["23", 0], "fps": 24}},
        "92": {"class_type": "SaveVideo", "inputs": {"video": ["91", 0], "filename_prefix": f"{CARPETA}/{t['nombre']}", "format": "auto", "codec": "auto"}},
    }
    if t.get("fin"):
        f["31"] = {"class_type": "LoadImage", "inputs": {"image": f"{CARPETA}/{t['fin']}.png"}}
        f["104"]["inputs"]["last_frame"] = ["31", 0]
    return f


@app.function(gpu="A100-80GB", volumes={"/datos": datos}, timeout=5400)
def clips(cuadros_png: dict, trabajos: list) -> dict:
    import glob, os, subprocess, time, requests
    from PIL import Image
    carpeta = f"/datos/siena/{CARPETA}"
    os.makedirs(carpeta, exist_ok=True)
    for nombre, contenido in cuadros_png.items():
        img = Image.open(io.BytesIO(contenido)).convert("RGB")
        if img.size != (ANCHO, ALTO):
            img = img.resize((ANCHO, ALTO), Image.LANCZOS)
        img.save(f"{carpeta}/{nombre}.png")
    open("/opt/ComfyUI/extra_model_paths.yaml", "w").write(
        "datos:\n  base_path: /datos/models\n  diffusion_models: diffusion_models\n  loras: loras\n  text_encoders: text_encoders\n  vae: vae\n")
    os.makedirs("/datos/siena/logs", exist_ok=True)
    log = open(f"/datos/siena/logs/comfy_pajaro_{int(time.time())}.log", "w")
    subprocess.Popen(["python", "main.py", "--listen", "127.0.0.1", "--port", "8188", "--input-directory", "/datos/siena", "--output-directory", "/datos/siena/out"],
                     cwd="/opt/ComfyUI", stdout=log, stderr=subprocess.STDOUT)
    for _ in range(300):
        try:
            requests.get("http://127.0.0.1:8188/system_stats", timeout=2); break
        except Exception:
            time.sleep(2)
    salida = {}
    for t in trabajos:
        t0 = time.time()
        r = requests.post("http://127.0.0.1:8188/prompt", json={"prompt": _flujo(t)}).json()
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
        archivo = sorted(glob.glob(f"/datos/siena/out/{CARPETA}/{t['nombre']}_*.mp4"), key=os.path.getmtime)[-1]
        salida[t["nombre"]] = open(archivo, "rb").read()
        print("clip", t["nombre"], f"{time.time()-t0:.0f}s", flush=True)
    log.close()
    return salida


@app.local_entrypoint()
def main(trabajos: str):
    aqui = pathlib.Path(__file__).resolve().parent
    spec = json.loads((aqui / trabajos).read_text())
    def png(n):
        for d in ("cuadros", "refs"):
            p = aqui / d / f"{n}.png"
            if p.exists():
                return p.read_bytes()
        raise FileNotFoundError(n)
    if spec["paso"] == "cuadros":
        nombres = {r for t in spec["trabajos"] for r in t["refs"]}
        res = cuadros.remote({n: png(n) for n in nombres}, spec["trabajos"])
        for n, v in res.items():
            (aqui / "cuadros" / f"{n}.png").write_bytes(v); print("guardado cuadros/", n)
    else:
        nombres = {t["inicio"] for t in spec["trabajos"]} | {t["fin"] for t in spec["trabajos"] if t.get("fin")}
        res = clips.remote({n: png(n) for n in nombres}, spec["trabajos"])
        for n, v in res.items():
            (aqui / "clips" / f"{n}.mp4").write_bytes(v); print("guardado clips/", n)
