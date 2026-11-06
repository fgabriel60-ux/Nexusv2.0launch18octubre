"""Video de Omar (Red Natura) en Modal: Omar hablando a cámara como el reel de ejemplo.

1. `cuadros`: Qwen-Image-Edit-2511 pone a Omar (omar_foto.jpg) en una oficina como la del ejemplo (ejemplo/oficina_ref.png).
2. `clips`: MiniMax H3 anima cada cuadro ~10 s con Omar diciendo su parte del guion (voz nativa del modelo).

Uso:  modal run omar_modal.py::main --paso cuadros   |   modal run omar_modal.py::main --paso clips
"""
import io
import json
import pathlib
import modal

ANCHO, ALTO = 576, 1024
CARPETA = "omar"
LARGO = 243  # 17k+5 cuadros a 24 fps ≈ 10 s

imagen = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("git", "ffmpeg")
    .run_commands("git clone --depth 1 https://github.com/comfyanonymous/ComfyUI /opt/ComfyUI")
    .pip_install("torch", "torchvision", "torchaudio")
    .run_commands("pip install -r /opt/ComfyUI/requirements.txt")
    .pip_install("git+https://github.com/huggingface/diffusers", "transformers", "accelerate", "pillow", "requests")
)
app = modal.App("omar-video", image=imagen)
datos = modal.Volume.from_name("h3-comprimido-gastro")
qwen = modal.Volume.from_name("qwen-image-edit-2511")

PERSONA = ("el hombre de la imagen 1, exactamente la misma cara, mismos lentes de armazón delgado, mismo peinado, "
           "mismo traje gris, camisa blanca y corbata azul")
OFICINA = ("en una oficina corporativa moderna y luminosa como la de la imagen 2: pared azul marino de fondo, plantas, "
           "piso claro brillante, escritorios blancos al fondo desenfocados")
CUADROS = {
    "O1": f"Foto vertical realista, plano medio: {PERSONA}, de pie {OFICINA}, mirando a la cámara y hablando con una "
          "sonrisa amable, manos al frente en gesto de explicar. Luz suave de estudio, estilo reel profesional, sin texto.",
    "O2": f"Foto vertical realista, plano americano un poco más abierto: {PERSONA}, caminando hacia la cámara {OFICINA}, "
          "con una mano extendida invitando, sonrisa segura. Luz suave, estilo reel profesional, sin texto.",
}
GUION = {
    "O1": "¿Conoces el multinivel? Con Red Natura, tu libertad financiera puede empezar hoy. Estamos en cuatro países "
          "y tenemos más de cincuenta productos para toda la familia.",
    "O2": "Control de peso, detox y nutrición. Y tienes seis formas de generar ingresos. Escríbeme por WhatsApp y te explico cómo empezar.",
}


def _a_vertical(img):
    from PIL import Image
    img = img.convert("RGB")
    escala = max(ANCHO / img.width, ALTO / img.height)
    img = img.resize((round(img.width * escala), round(img.height * escala)), Image.LANCZOS)
    x, y = (img.width - ANCHO) // 2, (img.height - ALTO) // 2
    return img.crop((x, y, x + ANCHO, y + ALTO))


@app.function(gpu="A100-80GB", volumes={"/datos": datos, "/qwen": qwen}, timeout=3600)
def cuadros(foto: bytes, oficina: bytes, semilla: int = 11):
    import os, torch
    from PIL import Image
    from diffusers import QwenImageEditPlusPipeline

    pipe = QwenImageEditPlusPipeline.from_pretrained("/qwen/Qwen-Image-Edit-2511", torch_dtype=torch.bfloat16).to("cuda")
    refs = [Image.open(io.BytesIO(foto)).convert("RGB"), Image.open(io.BytesIO(oficina)).convert("RGB")]
    carpeta = f"/datos/siena/{CARPETA}"
    os.makedirs(carpeta, exist_ok=True)
    salida = {}
    for nombre, prompt in CUADROS.items():
        img = pipe(image=refs, prompt=prompt, negative_prompt="texto, letras, deforme, borroso, otra persona, cara distinta",
                   true_cfg_scale=4.0, guidance_scale=1.0, num_inference_steps=40, height=1024, width=576,
                   generator=torch.Generator("cuda").manual_seed(semilla)).images[0]
        img = _a_vertical(img)
        img.save(f"{carpeta}/{nombre}.png")
        b = io.BytesIO(); img.save(b, "PNG"); salida[nombre] = b.getvalue()
        print("cuadro", nombre, flush=True)
    datos.commit()
    return salida


def _flujo(cuadro, prompt, prefijo, semilla):
    return {
        "6": {"class_type": "UNETLoader", "inputs": {"unet_name": "minimax_h3_fl2va_pruned_fp8_scaled.safetensors", "weight_dtype": "default"}},
        "121": {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["6", 0], "lora_name": "minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors", "strength_model": 1.0}},
        "13": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors", "type": "minimax", "device": "default"}},
        "11": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_video_vae_fp16.safetensors"}},
        "24": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_audio_vae_fp32.safetensors"}},
        "30": {"class_type": "LoadImage", "inputs": {"image": f"{CARPETA}/{cuadro}.png"}},
        "104": {"class_type": "MiniMaxH3ImageToVideo", "inputs": {"clip": ["13", 0], "vae": ["11", 0], "prompt": prompt, "width": ANCHO, "height": ALTO, "length": LARGO, "first_frame": ["30", 0]}},
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


def _prompt_habla(texto, accion):
    return (f"Vertical social media reel. The Mexican man in the grey suit and glasses {accion}, looking straight into the "
            f"camera, natural confident gestures, perfect lip sync. He speaks clearly in warm, energetic Mexican Spanish "
            f"(male voice, mid 30s), saying exactly: \"{texto}\" "
            "Clean voice recording with light office room tone, no music, no other voices.")


@app.function(gpu="A100-80GB", volumes={"/datos": datos}, timeout=3600)
def clips(semilla: int = 3):
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
    acciones = {"O1": "stands in a modern office and talks to the camera with a friendly smile",
                "O2": "walks slowly toward the camera in the office and gestures invitingly with one hand"}
    salida = {}
    for nombre, texto in GUION.items():
        prefijo = f"habla_{nombre}"
        r = requests.post("http://127.0.0.1:8188/prompt", json={"prompt": _flujo(nombre, _prompt_habla(texto, acciones[nombre]), prefijo, semilla)}).json()
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
        salida[nombre] = open(archivo, "rb").read()
        print("clip", nombre, archivo, flush=True)
    log.close()
    datos.commit()
    return salida


@app.local_entrypoint()
def main(paso: str = "cuadros", semilla: int = 11):
    aqui = pathlib.Path(__file__).resolve().parent
    destino = aqui / ("cuadros" if paso == "cuadros" else "clips")
    destino.mkdir(exist_ok=True)
    if paso == "cuadros":
        res = cuadros.remote((aqui / "omar_foto.jpg").read_bytes(), (aqui / "ejemplo" / "oficina_ref.png").read_bytes(), semilla)
    else:
        res = clips.remote(semilla)
    for nombre, contenido in res.items():
        (destino / f"{nombre}.{'png' if paso == 'cuadros' else 'mp4'}").write_bytes(contenido)
        print("guardado", destino / nombre)
