"""Fernando / Anegocios: 1 cuadro Qwen (libreta en mostrador) + 1 clip MiniMax H3 de 5 s sin voz.
Uso: modal run anegocios_modal.py::main --paso cuadros | --paso clips
"""
import io, json, math, pathlib
import modal

ANCHO, ALTO = 576, 1024
CARPETA = "anegocios_v3"
imagen = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("git", "ffmpeg")
    .run_commands("git clone --depth 1 https://github.com/comfyanonymous/ComfyUI /opt/ComfyUI")
    .pip_install("torch", "torchvision", "torchaudio")
    .run_commands("pip install -r /opt/ComfyUI/requirements.txt")
    .pip_install("git+https://github.com/huggingface/diffusers", "transformers", "accelerate", "pillow", "requests")
)
app = modal.App("anegocios-v3", image=imagen)
datos = modal.Volume.from_name("h3-comprimido-gastro")
qwen = modal.Volume.from_name("qwen-image-edit-2511")


NEG = "texto legible, letras, logotipo, deforme, borroso, manos deformes, dedos extra, cara deformada, caricatura"
CUADROS = {
    "M1": ("laptop", "Fotografía vertical realista, plano medio, dueño de una miscelánea mexicana de unos 45 años, bigote, playera polo azul, detrás de su mostrador de madera, "
           "con expresión cansada y preocupada mirando una libreta de rayas abierta llena de cuentas tachadas y una calculadora, la laptop plateada de la imagen 1 cerrada a un lado. "
           "Estantes con productos borrosos al fondo, luz cálida natural de tienda, cámara a la altura del pecho, sin texto legible, sin logotipos."),
    "M2": ("kit", "Fotografía vertical realista, plano medio, el mismo tipo de dueño de miscelánea mexicano (45 años, bigote, polo azul) sonriendo satisfecho en su mostrador, "
           "pasa un producto de abarrotes por el lector de códigos negro con base de la imagen 1, junto a él la impresora térmica negra de tickets de la imagen 1 con un ticket saliendo "
           "y una laptop plateada encendida con pantalla de punto de venta. Luz cálida de tienda, estantes borrosos, sin texto legible, sin logotipos."),
    "M3": ("laptop", "Fotografía vertical realista, plano medio, vendedor de ruta mexicano de 35 años con gorra y chaleco ligero, de pie junto a la camioneta de reparto abierta con cajas de productos, "
           "registrando una venta en un celular Android con ambas manos, sonriendo, en la calle de un barrio de Cuernavaca de día, luz natural suave, sin texto legible, sin logotipos."),
}
CLIPS = {
    "M1": "Vertical social media reel, real footage. A tired Mexican shopkeeper in a blue polo looks down at a paper notebook full of crossed-out numbers on his wooden counter, "
          "sighs, rubs his forehead and pushes the notebook slightly away with frustration. Natural human motion, correct hand anatomy with five fingers, static tripod camera, very slow push-in, no text.",
    "M2": "Vertical social media reel, real footage. A smiling Mexican shopkeeper in a blue polo scans a grocery product with a black barcode scanner on a stand, the thermal printer beside him prints a receipt, "
          "he tears the ticket and hands it toward the camera with a confident smile. Natural human motion, correct hand anatomy with five fingers, static tripod camera, no text.",
    "M3": "Vertical social media reel, real footage. A smiling Mexican route salesman in a cap taps on his Android phone to register a sale beside his delivery van full of boxes, then looks up at the camera and nods. "
          "Natural human motion, correct hand anatomy with five fingers, gentle handheld feel, no text.",
}


def _a_vertical(img):
    from PIL import Image
    img = img.convert("RGB")
    e = max(ANCHO / img.width, ALTO / img.height)
    img = img.resize((round(img.width * e), round(img.height * e)), Image.LANCZOS)
    x, y = (img.width - ANCHO) // 2, (img.height - ALTO) // 2
    return img.crop((x, y, x + ANCHO, y + ALTO))


@app.function(gpu="A100-80GB", volumes={"/datos": datos, "/qwen": qwen}, timeout=3600)
def cuadros(refs: dict, semilla: int = 5):
    import os, torch
    from PIL import Image
    from diffusers import QwenImageEditPlusPipeline
    pipe = QwenImageEditPlusPipeline.from_pretrained("/qwen/Qwen-Image-Edit-2511", torch_dtype=torch.bfloat16).to("cuda")
    carpeta = f"/datos/siena/{CARPETA}"; os.makedirs(carpeta, exist_ok=True)
    salida = {}
    for n, (ref, prompt) in CUADROS.items():
        img = pipe(image=[Image.open(io.BytesIO(refs[ref])).convert("RGB")], prompt=prompt, negative_prompt=NEG,
                   true_cfg_scale=4.0, guidance_scale=1.0, num_inference_steps=40, height=1024, width=576,
                   generator=torch.Generator("cuda").manual_seed(semilla)).images[0]
        img = _a_vertical(img); img.save(f"{carpeta}/{n}.png")
        b = io.BytesIO(); img.save(b, "PNG"); salida[n] = b.getvalue(); print("cuadro", n, flush=True)
    datos.commit()
    return salida


def _flujo(n, prompt, semilla, largo):
    return {
        "6": {"class_type": "UNETLoader", "inputs": {"unet_name": "minimax_h3_fl2va_pruned_fp8_scaled.safetensors", "weight_dtype": "default"}},
        "121": {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["6", 0], "lora_name": "minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors", "strength_model": 1.0}},
        "13": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors", "type": "minimax", "device": "default"}},
        "11": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_video_vae_fp16.safetensors"}},
        "24": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_audio_vae_fp32.safetensors"}},
        "30": {"class_type": "LoadImage", "inputs": {"image": f"{CARPETA}/{n}.png"}},
        "104": {"class_type": "MiniMaxH3ImageToVideo", "inputs": {"clip": ["13", 0], "vae": ["11", 0], "prompt": prompt, "width": ANCHO, "height": ALTO, "length": largo, "first_frame": ["30", 0]}},
        "15": {"class_type": "RandomNoise", "inputs": {"noise_seed": semilla}},
        "17": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "res_multistep"}},
        "9": {"class_type": "BasicScheduler", "inputs": {"model": ["121", 0], "scheduler": "simple", "steps": 8, "denoise": 1.0}},
        "16": {"class_type": "BasicGuider", "inputs": {"model": ["121", 0], "conditioning": ["104", 0]}},
        "14": {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["15", 0], "guider": ["16", 0], "sampler": ["17", 0], "sigmas": ["9", 0], "latent_image": ["104", 1]}},
        "10": {"class_type": "VAEDecode", "inputs": {"samples": ["14", 0], "vae": ["11", 0]}},
        "23": {"class_type": "VAEDecodeAudio", "inputs": {"samples": ["14", 0], "vae": ["24", 0]}},
        "91": {"class_type": "CreateVideo", "inputs": {"images": ["10", 0], "audio": ["23", 0], "fps": 24}},
        "92": {"class_type": "SaveVideo", "inputs": {"video": ["91", 0], "filename_prefix": f"{CARPETA}/{n}", "format": "auto", "codec": "auto"}},
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
    salida = {}
    for n, prompt in CLIPS.items():
        r = requests.post("http://127.0.0.1:8188/prompt", json={"prompt": _flujo(n, prompt, semilla, 121)}).json()
        if "prompt_id" not in r: raise RuntimeError(json.dumps(r)[:3000])
        pid = r["prompt_id"]
        while True:
            h = requests.get(f"http://127.0.0.1:8188/history/{pid}").json()
            if pid in h:
                st = h[pid].get("status", {})
                if st.get("status_str") == "error": raise RuntimeError(json.dumps(st)[:3000])
                break
            time.sleep(5)
        f = sorted(glob.glob(f"/datos/siena/out/{CARPETA}/{n}_*.mp4"), key=os.path.getmtime)[-1]
        salida[n] = open(f, "rb").read(); print("clip", n, flush=True)
    datos.commit()
    return salida


@app.local_entrypoint()
def main(paso: str = "cuadros", semilla: int = 5):
    aqui = pathlib.Path(__file__).resolve().parent
    if paso == "cuadros":
        refs = {"laptop": (aqui / "refs" / "laptop.png").read_bytes(), "kit": (aqui / "refs" / "fernando_image.jpg").read_bytes()}
        res = cuadros.remote(refs, semilla); d, ext = aqui / "cuadros_v3", "png"
    else:
        res = clips.remote(semilla); d, ext = aqui / "clips_v3", "mp4"
    d.mkdir(exist_ok=True)
    for k, v in res.items():
        (d / f"{k}.{ext}").write_bytes(v); print("guardado", d / f"{k}.{ext}")
