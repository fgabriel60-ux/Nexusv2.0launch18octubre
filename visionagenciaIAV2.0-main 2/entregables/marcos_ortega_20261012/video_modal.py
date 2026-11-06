"""Video de Soluciones Previsionales Ortega en Modal.

1. `cuadros`: Qwen-Image-Edit-2511 (volumen qwen-image-edit-2511) crea K1..K4; cada cuadro parte del
   anterior para que el personaje sea el mismo.
2. `clips`: ComfyUI + MiniMax H3 (volumen h3-comprimido-gastro) hace K1→K2, K2→K3, K3→K4 (5 s c/u, con audio).

Uso:  modal run video_modal.py::main --paso cuadros   |   modal run video_modal.py::main --paso clips
"""
import io
import json
import modal

ANCHO, ALTO = 576, 1024
CARPETA = "marcos"  # dentro de /datos/siena (entrada de ComfyUI) y /datos/siena/out (salida)

imagen = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("git", "ffmpeg")
    .run_commands("git clone --depth 1 https://github.com/comfyanonymous/ComfyUI /opt/ComfyUI")
    .pip_install("torch", "torchvision", "torchaudio")
    .run_commands("pip install -r /opt/ComfyUI/requirements.txt")
    .pip_install("git+https://github.com/huggingface/diffusers", "transformers", "accelerate", "pillow", "requests")
)
app = modal.App("ortega-video", image=imagen)
datos = modal.Volume.from_name("h3-comprimido-gastro")
qwen = modal.Volume.from_name("qwen-image-edit-2511")

ESTILO = ("Fotografía realista vertical 9:16, estilo comercial cinematográfico, luz natural suave, "
          "piel y texturas reales, sin texto, sin letras, sin logotipos.")
CUADROS = {
    "K1": (None, "Crea una foto nueva que ocupe toda la imagen: un hombre mexicano de unos 40 años, moreno, "
                 "bigote corto, camisa casual gris, sentado de noche en la mesa de la cocina de un departamento "
                 "modesto en la Ciudad de México, preocupado, mirando su celular con papeles y recibos sobre la mesa, "
                 "luz cálida de una lámpara. " + ESTILO),
    "K4": (["K1"], "Usa la imagen 1 como lienzo y crea una foto completamente nueva, sin la cocina ni papeles: el hombre de la imagen 2, misma cara, mismo bigote, ahora de día en la sala de su casa, de pie junto a la ventana, "
                 "sonriendo aliviado mientras mira su celular, luz cálida de la mañana. " + ESTILO),
    "K2": (["K4"], "Usa la imagen 1 como lienzo y crea una foto completamente nueva: el hombre de la imagen 2, misma cara, mismo bigote, misma camisa gris, sentado en una silla de visitante del lado izquierdo de un escritorio blanco en una oficina "
                 "moderna y limpia frente a una asesora mexicana de unos 35 años con saco azul marino que le explica "
                 "unos documentos sobre el escritorio; él se ve atento y esperanzado. Luz de día por la ventana. " + ESTILO),
    "K3": (["K2"], "Usa la imagen 1 como lienzo y crea una foto nueva con encuadre más cerrado: el hombre y la asesora de la imagen 2, de pie en la misma oficina, se estrechan la mano sonriendo ampliamente, él ya sin preocupación, "
                 "ella le entrega una carpeta azul. Ambiente de confianza y alivio. " + ESTILO),
}
TOMAS = {
    "toma1": ("K1", "K2", "Slow cinematic push-in. A worried Mexican man at his kitchen table at night looks at his "
                          "phone, then the scene transitions smoothly to the same man sitting in a bright office in front "
                          "of a female advisor in a navy blazer who explains documents. Realistic motion. "
                          "Audio: soft room tone only, no speech, no music."),
    "toma2": ("K2", "K3", "In a bright modern office, the advisor finishes explaining, both stand up slightly and shake "
                          "hands over the desk, she hands him a blue folder, both smile. Natural realistic motion, "
                          "gentle camera drift. Audio: soft office ambience only, no speech, no music."),
    "toma3": ("K3", "K4", "The man leaves the office smiling and the scene transitions to him at home in the morning "
                          "by the window, looking at his phone with relief and a big smile. Slow camera move, realistic. "
                          "Audio: soft morning ambience, birds far away, no speech, no music."),
}


def _a_vertical(img):
    from PIL import Image
    img = img.convert("RGB")
    escala = max(ANCHO / img.width, ALTO / img.height)
    img = img.resize((round(img.width * escala), round(img.height * escala)), Image.LANCZOS)
    x, y = (img.width - ANCHO) // 2, (img.height - ALTO) // 2
    return img.crop((x, y, x + ANCHO, y + ALTO))


@app.function(gpu="A100-80GB", volumes={"/datos": datos, "/qwen": qwen}, timeout=3600)
def cuadros(semilla: int = 7, solo: str = ""):
    import os, torch
    from PIL import Image
    from diffusers import QwenImageEditPlusPipeline

    pipe = QwenImageEditPlusPipeline.from_pretrained("/qwen/Qwen-Image-Edit-2511", torch_dtype=torch.bfloat16).to("cuda")
    carpeta = f"/datos/siena/{CARPETA}"
    os.makedirs(carpeta, exist_ok=True)
    hechos, salida = {}, {}
    lienzo = Image.new("RGB", (ANCHO, ALTO), (128, 128, 128))
    for nombre, (refs, prompt) in CUADROS.items():
        if solo and nombre not in solo.split(","):
            hechos[nombre] = Image.open(f"{carpeta}/{nombre}.png").convert("RGB")
            continue
        entrada = [lienzo] + [hechos[r] for r in (refs or [])]
        img = pipe(image=entrada, prompt=prompt, negative_prompt="texto, letras, marca de agua, deforme, borroso",
                   true_cfg_scale=4.0, guidance_scale=1.0, num_inference_steps=40,
                   generator=torch.Generator("cuda").manual_seed(semilla)).images[0]
        img = _a_vertical(img)
        img.save(f"{carpeta}/{nombre}.png")
        hechos[nombre] = img
        b = io.BytesIO(); img.save(b, "PNG"); salida[nombre] = b.getvalue()
        print("cuadro", nombre, flush=True)
    datos.commit()
    return salida


def _flujo(primero, ultimo, prompt, prefijo, semilla):
    return {
        "6": {"class_type": "UNETLoader", "inputs": {"unet_name": "minimax_h3_fl2va_pruned_fp8_scaled.safetensors", "weight_dtype": "default"}},
        "121": {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["6", 0], "lora_name": "minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors", "strength_model": 1.0}},
        "13": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors", "type": "minimax", "device": "default"}},
        "11": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_video_vae_fp16.safetensors"}},
        "24": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_audio_vae_fp32.safetensors"}},
        "30": {"class_type": "LoadImage", "inputs": {"image": f"{CARPETA}/{primero}.png"}},
        "31": {"class_type": "LoadImage", "inputs": {"image": f"{CARPETA}/{ultimo}.png"}},
        "104": {"class_type": "MiniMaxH3ImageToVideo", "inputs": {"clip": ["13", 0], "vae": ["11", 0], "prompt": prompt, "width": ANCHO, "height": ALTO, "length": 124, "first_frame": ["30", 0], "last_frame": ["31", 0]}},
        "15": {"class_type": "RandomNoise", "inputs": {"noise_seed": semilla}},
        "17": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "res_multistep"}},
        "9": {"class_type": "BasicScheduler", "inputs": {"model": ["121", 0], "scheduler": "simple", "steps": 8, "denoise": 1.0}},
        "16": {"class_type": "BasicGuider", "inputs": {"model": ["121", 0], "conditioning": ["104", 0]}},
        "14": {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["15", 0], "guider": ["16", 0], "sampler": ["17", 0], "sigmas": ["9", 0], "latent_image": ["104", 1]}},
        "10": {"class_type": "VAEDecode", "inputs": {"samples": ["14", 0], "vae": ["11", 0]}},
        "23": {"class_type": "VAEDecodeAudio", "inputs": {"samples": ["14", 0], "vae": ["24", 0]}},
        "91": {"class_type": "CreateVideo", "inputs": {"images": ["10", 0], "audio": ["23", 0], "fps": 24}},
        "92": {"class_type": "SaveVideo", "inputs": {"video": ["91", 0], "filename_prefix": f"{CARPETA}/{prefijo}", "format": "auto", "codec": "auto"}},
    }


@app.function(gpu="A100-80GB", volumes={"/datos": datos}, timeout=3600)
def clips(semilla: int = 1):
    import glob, os, subprocess, time, requests

    open("/opt/ComfyUI/extra_model_paths.yaml", "w").write(
        "datos:\n  base_path: /datos/models\n  diffusion_models: diffusion_models\n  loras: loras\n"
        "  text_encoders: text_encoders\n  vae: vae\n")
    log = open(f"/datos/siena/logs/comfy_{int(time.time())}.log", "w")
    subprocess.Popen(["python", "main.py", "--listen", "127.0.0.1", "--port", "8188",
                      "--input-directory", "/datos/siena", "--output-directory", "/datos/siena/out"],
                     cwd="/opt/ComfyUI", stdout=log, stderr=subprocess.STDOUT)
    for _ in range(300):
        try:
            requests.get("http://127.0.0.1:8188/system_stats", timeout=2); break
        except Exception:
            time.sleep(2)
    salida = {}
    for prefijo, (a, b, prompt) in TOMAS.items():
        r = requests.post("http://127.0.0.1:8188/prompt", json={"prompt": _flujo(a, b, prompt, prefijo, semilla)}).json()
        if "prompt_id" not in r:
            raise RuntimeError(json.dumps(r)[:2000])
        pid = r["prompt_id"]
        while True:
            h = requests.get(f"http://127.0.0.1:8188/history/{pid}").json()
            if pid in h:
                st = h[pid].get("status", {})
                if st.get("status_str") == "error":
                    raise RuntimeError(json.dumps(st)[:3000])
                break
            time.sleep(5)
        archivo = sorted(glob.glob(f"/datos/siena/out/{CARPETA}/{prefijo}_*.mp4"), key=os.path.getmtime)[-1]
        salida[prefijo] = open(archivo, "rb").read()
        print("clip", prefijo, archivo, flush=True)
    log.close()
    datos.commit()
    return salida


@app.local_entrypoint()
def main(paso: str = "cuadros", semilla: int = 7, solo: str = ""):
    import pathlib
    destino = pathlib.Path("cuadros" if paso == "cuadros" else "clips")
    destino.mkdir(exist_ok=True)
    res = cuadros.remote(semilla, solo) if paso == "cuadros" else clips.remote(semilla)
    for nombre, contenido in res.items():
        (destino / f"{nombre}.{'png' if paso == 'cuadros' else 'mp4'}").write_bytes(contenido)
        print("guardado", destino / nombre)
