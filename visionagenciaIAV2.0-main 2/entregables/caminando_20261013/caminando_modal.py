"""Marcos y Omar caminando hacia la cámara (estilo real estate, texto detrás) con su voz y lip-sync — Modal.

1. `cuadros`: Qwen-Image-Edit-2511 crea H1..H5 con Mariano (refs/mariano.png), la casa Brescia (refs/casa.png)
   y la vista aérea con mar (refs/aerea.png).
2. `clips`: MiniMax H3 hace T1 (H1→H2 aterrizaje con polvo) y T2..T4 hablando; en T2..T4 la voz clonada de Mariano
   (voz/T*.wav, Fish Audio) se ancla con MiniMaxH3AddGuide para que los labios sigan su voz real.

Uso:  modal run mariano_modal.py::main --paso cuadros   |   modal run mariano_modal.py::main --paso clips
"""
import io
import json
import math
import pathlib
import modal

ANCHO, ALTO = 576, 1024
CARPETA = "caminando"

imagen = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("git", "ffmpeg")
    .run_commands("git clone --depth 1 https://github.com/comfyanonymous/ComfyUI /opt/ComfyUI")
    .pip_install("torch", "torchvision", "torchaudio")
    .run_commands("pip install -r /opt/ComfyUI/requirements.txt")
    .pip_install("git+https://github.com/huggingface/diffusers", "transformers", "accelerate", "pillow", "requests")
)
app = modal.App("caminando-marcos-omar", image=imagen)
datos = modal.Volume.from_name("h3-comprimido-gastro")
qwen = modal.Volume.from_name("qwen-image-edit-2511")

FOTO = ("Foto vertical realista estilo reel de bienes raíces, cuerpo completo visible de la cabeza a los pies, mucho espacio "
        "libre arriba de la cabeza, luz natural suave, piel real, sin texto nuevo.")
MARCOS = ("el hombre de la imagen 1, EXACTAMENTE la misma cara, en su mejor versión: bien peinado, sonrisa cálida y amigable, "
          "mirada confiable, camisa azul marino con el logo dorado de Ortega y pantalón azul marino")
OMAR = ("el hombre de la imagen 1, EXACTAMENTE la misma cara, mismos lentes de armazón delgado, sonrisa amigable, traje gris, "
        "camisa blanca y corbata azul")
CUADROS = {
    # Marcos: 3 tomas, cada una de lejos (A) a media distancia (B)
    "M1A": (["marcos", "marcos_afore"], f"{MARCOS}, caminando hacia la cámara por la banqueta frente a la Afore de la imagen 2, lejos, cuerpo completo, una mano abierta saludando. " + FOTO),
    "M1B": (["marcos", "marcos_afore"], f"{MARCOS}, un poco más cerca caminando frente a la Afore de la imagen 2, todavía de CUERPO COMPLETO (se ven sus zapatos), explicando con una mano abierta. " + FOTO),
    "M2A": (["marcos", "marcos_logo"], f"{MARCOS}, caminando hacia la cámara en la oficina con la pared del logo de Ortega de la imagen 2, lejos, cuerpo completo. " + FOTO),
    "M2B": (["marcos", "marcos_logo"], f"{MARCOS}, un poco más cerca en la misma oficina de la imagen 2, todavía de CUERPO COMPLETO (se ven sus zapatos), contando con los dedos de una mano. " + FOTO),
    "M3A": (["marcos", "marcos_oficina"], f"{MARCOS}, caminando hacia la cámara en la oficina con el tablero de servicios de la imagen 2, lejos, cuerpo completo. " + FOTO),
    "M3B": (["marcos", "marcos_oficina"], f"{MARCOS}, más cerca en la misma oficina de la imagen 2, plano americano, con la mano en el pecho en gesto de confianza. " + FOTO),
    # Omar: 2 tomas
    "O1A": (["omar", "omar_oficina"], f"{OMAR}, caminando hacia la cámara en una oficina moderna con pared azul LISA SIN LETRAS NI LOGOTIPOS, lejos, cuerpo completo. " + FOTO),
    "O1B": (["omar", "omar_oficina"], f"{OMAR}, un poco más cerca en la misma oficina de pared azul lisa sin letras, de cuerpo completo, explicando con las dos manos abiertas, boca cerrada sonriendo. " + FOTO),
    "O2A": (["omar", "omar_oficina"], f"{OMAR}, caminando hacia la cámara desde el fondo de la oficina de la imagen 2, lejos, cuerpo completo, sonriendo. " + FOTO),
    "O2B": (["omar", "omar_oficina"], f"{OMAR}, más cerca en la misma oficina de la imagen 2, plano americano, señalando con el índice hacia abajo como invitando a escribir. " + FOTO),
}
CAMINA = ("Real estate style vertical reel. {quien} walks slowly and confidently toward the camera with a friendly, trustworthy "
          "smile, talking in Mexican Spanish with varied, natural, non-repetitive hand gestures with real anatomy, stopping at a "
          "medium distance (never too close to the camera), full body visible at the start, steady gimbal camera, perfect lip "
          "sync to the given voice.")
TOMAS = {
    "M1": ("M1A", "M1B", "TM1", CAMINA.format(quien="The man in the navy Ortega shirt")),
    "M2": ("M2A", "M2B", "TM2", CAMINA.format(quien="The man in the navy Ortega shirt")),
    "M3": ("M3A", "M3B", "TM3", CAMINA.format(quien="The man in the navy Ortega shirt")),
    "O1": ("O1A", "O1B", "TO1", CAMINA.format(quien="The man in the grey suit and glasses")),
    "O2": ("O2A", "O2B", "TO2", CAMINA.format(quien="The man in the grey suit and glasses")),
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
                   negative_prompt="deforme, borroso, otra cara, manos deformes, dedos extra",
                   true_cfg_scale=4.0, guidance_scale=1.0, num_inference_steps=40, height=1024, width=576,
                   generator=torch.Generator("cuda").manual_seed(semilla)).images[0]
        img = _a_vertical(img)
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
def clips(voces: dict, duraciones: dict, semilla: int = 2, solo: str = ""):
    import glob, os, subprocess, time, requests

    carpeta = f"/datos/siena/{CARPETA}"
    os.makedirs(carpeta, exist_ok=True)
    for nombre, contenido in voces.items():
        open(f"{carpeta}/{nombre}.wav", "wb").write(contenido)
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
    for toma, (inicio, fin, voz, prompt) in TOMAS.items():
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
    import subprocess
    import imageio_ffmpeg
    aqui = pathlib.Path(__file__).resolve().parent
    destino = aqui / ("cuadros" if paso == "cuadros" else "clips")
    destino.mkdir(exist_ok=True)
    if paso == "cuadros":
        refs = {k: (aqui / "refs" / f"{k}.png").read_bytes() for k in ("marcos", "marcos_afore", "marcos_logo", "marcos_oficina", "omar", "omar_oficina")}
        res = cuadros.remote(refs, semilla, solo)
    else:
        voces, dur = {}, {}
        for w in sorted((aqui / "voz").glob("T*.wav")):
            voces[w.stem] = w.read_bytes()
            err = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-i", str(w)], capture_output=True, text=True).stderr
            h, m, s = err.split("Duration: ")[1].split(",")[0].split(":")
            dur[w.stem] = int(h) * 3600 + int(m) * 60 + float(s)
        res = clips.remote(voces, dur, semilla, solo)
    for nombre, contenido in res.items():
        (destino / f"{nombre}.{'png' if paso == 'cuadros' else 'mp4'}").write_bytes(contenido)
        print("guardado", destino / nombre)
