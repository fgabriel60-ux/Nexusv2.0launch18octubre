"""Fernando / Anegocios: 1 cuadro Qwen (libreta en mostrador) + 1 clip MiniMax H3 de 5 s sin voz.
Uso: modal run anegocios_modal.py::main --paso cuadros | --paso clips
"""
import io, json, math, pathlib
import modal

ANCHO, ALTO = 576, 1024
CARPETA = "anegocios"
imagen = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("git", "ffmpeg")
    .run_commands("git clone --depth 1 https://github.com/comfyanonymous/ComfyUI /opt/ComfyUI")
    .pip_install("torch", "torchvision", "torchaudio")
    .run_commands("pip install -r /opt/ComfyUI/requirements.txt")
    .pip_install("git+https://github.com/huggingface/diffusers", "transformers", "accelerate", "pillow", "requests")
)
app = modal.App("anegocios-v1", image=imagen)
datos = modal.Volume.from_name("h3-comprimido-gastro")
qwen = modal.Volume.from_name("qwen-image-edit-2511")

PROMPT_CUADRO = ("Fotografía vertical realista de un mostrador de miscelánea mexicana, vista cenital inclinada: sobre el mostrador de madera "
                 "una libreta de rayas abierta con cuentas escritas a mano, un lápiz y una calculadora, y al lado la laptop plateada de la imagen 1. "
                 "Al fondo estantes con productos borrosos. Una mano de hombre sostiene el lápiz sobre la libreta. Luz cálida de tienda, "
                 "sin texto legible, sin logotipos.")
PROMPT_CLIP = ("Vertical social media reel, real footage. Close-up of a shopkeeper's hand writing numbers in a paper notebook on a wooden counter "
               "of a small Mexican corner store, a calculator and a silver laptop beside it. The hand writes slowly, then pauses and slides "
               "the notebook aside. Static tripod camera, very subtle slow push-in, natural hand anatomy with five fingers, no text.")


def _a_vertical(img):
    from PIL import Image
    img = img.convert("RGB")
    e = max(ANCHO / img.width, ALTO / img.height)
    img = img.resize((round(img.width * e), round(img.height * e)), Image.LANCZOS)
    x, y = (img.width - ANCHO) // 2, (img.height - ALTO) // 2
    return img.crop((x, y, x + ANCHO, y + ALTO))


@app.function(gpu="A100-80GB", volumes={"/datos": datos, "/qwen": qwen}, timeout=3600)
def cuadros(ref: bytes, semilla: int = 5):
    import os, torch
    from PIL import Image
    from diffusers import QwenImageEditPlusPipeline
    pipe = QwenImageEditPlusPipeline.from_pretrained("/qwen/Qwen-Image-Edit-2511", torch_dtype=torch.bfloat16).to("cuda")
    img = pipe(image=[Image.open(io.BytesIO(ref)).convert("RGB")], prompt=PROMPT_CUADRO,
               negative_prompt="texto legible, letras, logotipo, deforme, borroso, manos deformes",
               true_cfg_scale=4.0, guidance_scale=1.0, num_inference_steps=40, height=1024, width=576,
               generator=torch.Generator("cuda").manual_seed(semilla)).images[0]
    img = _a_vertical(img)
    carpeta = f"/datos/siena/{CARPETA}"; os.makedirs(carpeta, exist_ok=True)
    img.save(f"{carpeta}/L1.png"); datos.commit()
    b = io.BytesIO(); img.save(b, "PNG"); return {"L1": b.getvalue()}


def _flujo(semilla, largo):
    return {
        "6": {"class_type": "UNETLoader", "inputs": {"unet_name": "minimax_h3_fl2va_pruned_fp8_scaled.safetensors", "weight_dtype": "default"}},
        "121": {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["6", 0], "lora_name": "minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors", "strength_model": 1.0}},
        "13": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors", "type": "minimax", "device": "default"}},
        "11": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_video_vae_fp16.safetensors"}},
        "24": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_audio_vae_fp32.safetensors"}},
        "30": {"class_type": "LoadImage", "inputs": {"image": f"{CARPETA}/L1.png"}},
        "104": {"class_type": "MiniMaxH3ImageToVideo", "inputs": {"clip": ["13", 0], "vae": ["11", 0], "prompt": PROMPT_CLIP, "width": ANCHO, "height": ALTO, "length": largo, "first_frame": ["30", 0]}},
        "15": {"class_type": "RandomNoise", "inputs": {"noise_seed": semilla}},
        "17": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "res_multistep"}},
        "9": {"class_type": "BasicScheduler", "inputs": {"model": ["121", 0], "scheduler": "simple", "steps": 8, "denoise": 1.0}},
        "16": {"class_type": "BasicGuider", "inputs": {"model": ["121", 0], "conditioning": ["104", 0]}},
        "14": {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["15", 0], "guider": ["16", 0], "sampler": ["17", 0], "sigmas": ["9", 0], "latent_image": ["104", 1]}},
        "10": {"class_type": "VAEDecode", "inputs": {"samples": ["14", 0], "vae": ["11", 0]}},
        "23": {"class_type": "VAEDecodeAudio", "inputs": {"samples": ["14", 0], "vae": ["24", 0]}},
        "91": {"class_type": "CreateVideo", "inputs": {"images": ["10", 0], "audio": ["23", 0], "fps": 24}},
        "92": {"class_type": "SaveVideo", "inputs": {"video": ["91", 0], "filename_prefix": f"{CARPETA}/L1", "format": "auto", "codec": "auto"}},
    }


@app.function(gpu="A100-80GB", volumes={"/datos": datos}, timeout=5400)
def clips(semilla: int = 2):
    import glob, os, subprocess, time, requests
    os.makedirs("/datos/siena/logs", exist_ok=True)
    open("/opt/ComfyUI/extra_model_paths.yaml", "w").write(
        "datos:\n  base_path: /datos/models\n  diffusion_models: diffusion_models\n  loras: loras\n  text_encoders: text_encoders\n  vae: vae\n")
    log = open(f"/datos/siena/logs/comfy_{int(time.time())}.log", "w")
    subprocess.Popen(["python", "main.py", "--listen", "127.0.0.1", "--port", "8188", "--input-directory", "/datos/siena",
                      "--output-directory", "/datos/siena/out"], cwd="/opt/ComfyUI", stdout=log, stderr=subprocess.STDOUT)
    for _ in range(300):
        try: requests.get("http://127.0.0.1:8188/system_stats", timeout=2); break
        except Exception: time.sleep(2)
    r = requests.post("http://127.0.0.1:8188/prompt", json={"prompt": _flujo(semilla, 121)}).json()
    if "prompt_id" not in r: raise RuntimeError(json.dumps(r)[:3000])
    pid = r["prompt_id"]
    while True:
        h = requests.get(f"http://127.0.0.1:8188/history/{pid}").json()
        if pid in h:
            st = h[pid].get("status", {})
            if st.get("status_str") == "error": raise RuntimeError(json.dumps(st)[:3000])
            break
        time.sleep(5)
    f = sorted(glob.glob(f"/datos/siena/out/{CARPETA}/L1_*.mp4"), key=os.path.getmtime)[-1]
    datos.commit()
    return {"L1": open(f, "rb").read()}


@app.local_entrypoint()
def main(paso: str = "cuadros", semilla: int = 5):
    aqui = pathlib.Path(__file__).resolve().parent
    if paso == "cuadros":
        res = cuadros.remote((aqui / "refs" / "laptop.png").read_bytes(), semilla); d, ext = aqui / "cuadros", "png"
    else:
        res = clips.remote(semilla); d, ext = aqui / "clips", "mp4"
    for k, v in res.items():
        (d / f"{k}.{ext}").write_bytes(v); print("guardado", d / f"{k}.{ext}")
