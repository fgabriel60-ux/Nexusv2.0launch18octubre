"""Fumicam Iván v4 (método Planet Plus: oferta + confianza + calidad con acercamientos de detalle) — basado en Jeremías (Mueblería Medina, Mérida) · transformación de cuarto vacío a recámara con SU cama de $3,500, como el reel de referencia.

1. `cuadros`: Qwen-Image-Edit-2511 crea J1..J4 con la foto real de la cama (refs/cama.jpg).
2. `clips`: MiniMax H3 anima J1→J2, J2→J3 y J3→J4 (sin voz: la narración va en el armado).

Uso:  MODAL_PROFILE=fgabriel60 modal run jeremias_modal.py::main --paso cuadros   |   --paso clips
"""
import io
import json
import math
import pathlib
import modal

ANCHO, ALTO = 576, 1024
CARPETA = "ivan_v4"

imagen = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("git", "ffmpeg")
    .run_commands("git clone --depth 1 https://github.com/comfyanonymous/ComfyUI /opt/ComfyUI")
    .pip_install("torch", "torchvision", "torchaudio")
    .run_commands("pip install -r /opt/ComfyUI/requirements.txt")
    .pip_install("git+https://github.com/huggingface/diffusers", "transformers", "accelerate", "pillow", "requests")
)
app = modal.App("ivan-v4", image=imagen)
datos = modal.Volume.from_name("h3-comprimido-gastro")
qwen = modal.Volume.from_name("qwen-image-edit-2511")

ESTILO = "Foto vertical 9:16 hiperrealista tipo video de celular profesional, luz natural, sin texto, sin letras, sin logotipos en la ropa ni en los envases."
TECNICO = "el MISMO técnico fumigador de la imagen (playera azul, mascarilla con filtros, guantes)"
CUADROS = {   # acercamientos de DETALLE (método del reel de Planet Plus): dónde anidan las plagas y cómo se aplica, con el técnico real de Fumicam
    "D1": (["zoclo"], f"Acercamiento macro: la mano con guante de {TECNICO} aplica con una jeringa aplicadora un punto de gel insecticida en la grieta entre el zoclo y el piso de una cocina. Se ve la grieta y el punto de gel, fondo desenfocado. " + ESTILO),
    "D2": (["zoclo"], f"Acercamiento: la mano con guante de {TECNICO} aplica gel con jeringa en la entrada del tubo debajo del fregadero, gabinete abierto, linterna iluminando. " + ESTILO),
    "D3": (["recamara"], f"Acercamiento a la boquilla de la bomba aspersora de {TECNICO} rociando una niebla fina a lo largo de la base de la cama y la esquina del cuarto, luz de ventana. " + ESTILO),
    "D4": (["mochila"], f"Toma baja: {TECNICO} con su mochila aspersora verde rocía el perímetro del muro y la tierra del jardín, gotas finas brillando a contraluz. " + ESTILO),
    "D5": (["pasillo"], f"Acercamiento: {TECNICO} perfora con un taladro pequeño un orificio en el marco de madera de una puerta e inyecta el tratamiento contra termitas de madera seca con una boquilla, aserrín fino de termita en el piso. " + ESTILO),
    "D6": (["mochila"], f"Acercamiento: {TECNICO} inyecta tratamiento contra termitas subterráneas en la tierra junto al muro de la casa con una varilla inyectora metálica, tierra húmeda. " + ESTILO),
}
SUAVE = " Handheld smartphone close-up, realistic precise movement, shallow depth of field. Audio: sprayer hiss, no music, no speech."
TOMAS = {
    "V1": ("D1", "Slow macro push-in as the gloved hand places a dot of gel bait into the crack along the baseboard." + SUAVE),
    "V2": ("D2", "The gloved hand applies gel around the pipe under the sink, flashlight beam moves slightly." + SUAVE),
    "V3": ("D3", "The sprayer nozzle releases a fine mist along the bed base and room corner, camera follows the nozzle." + SUAVE),
    "V4": ("D4", "The technician sprays the garden wall perimeter, fine droplets sparkle in the backlight, camera low tracking." + SUAVE),
    "V5": ("D5", "The technician injects the termite treatment into the small hole in the wooden door frame, slow push-in." + SUAVE),
    "V6": ("D6", "The technician pushes the metal injection rod into the soil along the house wall and the treatment flows, close-up." + SUAVE),
}


def _a_vertical(img):
    from PIL import Image
    img = img.convert("RGB")
    escala = max(ANCHO / img.width, ALTO / img.height)
    img = img.resize((round(img.width * escala), round(img.height * escala)), Image.LANCZOS)
    x, y = (img.width - ANCHO) // 2, (img.height - ALTO) // 2
    return img.crop((x, y, x + ANCHO, y + ALTO))


@app.function(gpu="A100-80GB", volumes={"/datos": datos, "/qwen": qwen}, timeout=3600)
def cuadros(refs: dict, semilla: int = 5, solo: str = ""):
    import os, torch
    from PIL import Image
    from diffusers import QwenImageEditPlusPipeline

    pipe = QwenImageEditPlusPipeline.from_pretrained("/qwen/Qwen-Image-Edit-2511", torch_dtype=torch.bfloat16).to("cuda")
    imgs = {k: Image.open(io.BytesIO(v)).convert("RGB") for k, v in refs.items()}
    carpeta = f"/datos/siena/{CARPETA}"
    os.makedirs(carpeta, exist_ok=True)
    salida = {}
    for nombre, (usar, prompt) in CUADROS.items():
        if solo and nombre not in solo.split(","):
            continue
        img = pipe(image=[imgs[u] for u in usar], prompt=prompt,
                   negative_prompt="texto, letras, logotipo, deforme, borroso, letras en la ropa, etiquetas con texto, cara deforme, manos deformes" + "",
                   true_cfg_scale=4.0, guidance_scale=1.0, num_inference_steps=40, height=1280, width=720,
                   generator=torch.Generator("cuda").manual_seed(semilla)).images[0]
        img = _a_vertical(img)
        imgs[nombre] = img
        img.save(f"{carpeta}/{nombre}.png")
        b = io.BytesIO(); img.save(b, "PNG"); salida[nombre] = b.getvalue()
        print("cuadro", nombre, flush=True)
    datos.commit()
    return salida


def _largo(segundos):
    n = max(124, math.ceil(segundos * 24))
    return min(362, n + (5 - n % 17) % 17)


def _flujo(inicio, fin, voz, prompt, prefijo, semilla, largo):
    f = {
        "6": {"class_type": "UNETLoader", "inputs": {"unet_name": "minimax_h3_fl2va_pruned_fp8_scaled.safetensors", "weight_dtype": "default"}},
        "121": {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["6", 0], "lora_name": "minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors", "strength_model": 1.0}},
        "13": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors", "type": "minimax", "device": "default"}},
        "11": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_video_vae_fp16.safetensors"}},
        "24": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_audio_vae_fp32.safetensors"}},
        "30": {"class_type": "LoadImage", "inputs": {"image": f"{CARPETA}/{inicio}.png"}},
        "104": {"class_type": "MiniMaxH3ImageToVideo", "inputs": {"clip": ["13", 0], "vae": ["11", 0], "prompt": prompt, "width": ANCHO, "height": ALTO, "length": largo, "first_frame": ["30", 0]}},
        "15": {"class_type": "RandomNoise", "inputs": {"noise_seed": semilla}},
        "17": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "res_multistep"}},
        "9": {"class_type": "BasicScheduler", "inputs": {"model": ["121", 0], "scheduler": "simple", "steps": 8, "denoise": 1.0}},
        "14": {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["15", 0], "guider": ["16", 0], "sampler": ["17", 0], "sigmas": ["9", 0], "latent_image": ["104", 1]}},
        "10": {"class_type": "VAEDecode", "inputs": {"samples": ["14", 0], "vae": ["11", 0]}},
        "23": {"class_type": "VAEDecodeAudio", "inputs": {"samples": ["14", 0], "vae": ["24", 0]}},
        "91": {"class_type": "CreateVideo", "inputs": {"images": ["10", 0], "audio": ["23", 0], "fps": 24}},
        "92": {"class_type": "SaveVideo", "inputs": {"video": ["91", 0], "filename_prefix": f"{CARPETA}/{prefijo}", "format": "auto", "codec": "auto"}},
    }
    if fin:
        f["31"] = {"class_type": "LoadImage", "inputs": {"image": f"{CARPETA}/{fin}.png"}}
        f["104"]["inputs"]["last_frame"] = ["31", 0]
    positivo = ["104", 0]
    if voz:
        f["40"] = {"class_type": "LoadAudio", "inputs": {"audio": f"{CARPETA}/{voz}.wav"}}
        f["41"] = {"class_type": "MiniMaxH3AddGuide", "inputs": {"positive": ["104", 0], "latent": ["104", 1], "audio_vae": ["24", 0], "audio": ["40", 0], "frame_idx": 0}}
        positivo = ["41", 0]
    f["16"] = {"class_type": "BasicGuider", "inputs": {"model": ["121", 0], "conditioning": positivo}}
    return f


@app.function(gpu="A100-80GB", volumes={"/datos": datos}, timeout=5400)
def clips(voces: dict, duraciones: dict, semilla: int = 2, solo: str = "", cuadros_png: dict = None):
    import glob, os, subprocess, time, requests

    carpeta = f"/datos/siena/{CARPETA}"
    os.makedirs(carpeta, exist_ok=True)
    for nombre, contenido in (cuadros_png or {}).items():           # cuadros aprobados (J3 y J4 compuestos) pisan los del volumen
        open(f"{carpeta}/{nombre}.png", "wb").write(contenido)
    for nombre, contenido in voces.items():
        open(f"{carpeta}/{nombre}.wav", "wb").write(contenido)
    open("/opt/ComfyUI/extra_model_paths.yaml", "w").write(
        "datos:\n  base_path: /datos/models\n  diffusion_models: diffusion_models\n  loras: loras\n"
        "  text_encoders: text_encoders\n  vae: vae\n")
    os.makedirs("/datos/siena/logs", exist_ok=True)
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
    for toma, (inicio, prompt) in TOMAS.items():
        fin = voz = None
        if solo and toma not in solo.split(","):
            continue
        largo = _largo(duraciones.get(voz, 5.0)) if voz else 124
        r = requests.post("http://127.0.0.1:8188/prompt", json={"prompt": _flujo(inicio, fin, voz, prompt, toma, semilla, largo)}).json()
        if "prompt_id" not in r:
            raise RuntimeError(json.dumps(r)[:3000])
        pid = r["prompt_id"]
        while True:
            h = requests.get(f"http://127.0.0.1:8188/history/{pid}").json()
            if pid in h:
                st = h[pid].get("status", {})
                if st.get("status_str") == "error":
                    raise RuntimeError(json.dumps(st)[:3000])
                break
            time.sleep(5)
        archivo = sorted(glob.glob(f"/datos/siena/out/{CARPETA}/{toma}_*.mp4"), key=os.path.getmtime)[-1]
        salida[toma] = open(archivo, "rb").read()
        print("clip", toma, largo, archivo, flush=True)
    log.close()
    datos.commit()
    return salida


@app.local_entrypoint()
def main(paso: str = "cuadros", semilla: int = 5, solo: str = ""):
    aqui = pathlib.Path(__file__).resolve().parent
    destino = aqui / ("cuadros" if paso == "cuadros" else "clips")
    destino.mkdir(exist_ok=True)
    if paso == "cuadros":
        refs = {p.stem: p.read_bytes() for p in list((aqui / "refs").glob("*.png")) + list((aqui / "refs").glob("*.jpg"))}
        res = cuadros.remote(refs, semilla, solo)
    else:
        res = clips.remote({}, {}, semilla, solo, {p.stem: p.read_bytes() for p in (aqui / "cuadros").glob("*.png")})
    for nombre, contenido in res.items():
        (destino / f"{nombre}.{'png' if paso == 'cuadros' else 'mp4'}").write_bytes(contenido)
        print("guardado", destino / nombre)
