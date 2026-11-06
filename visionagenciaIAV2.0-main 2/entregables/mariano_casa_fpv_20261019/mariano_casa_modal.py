"""Mariano · recorrido de casa Benjamina: cada escena de su video real (primer cuadro) pasa por MiniMax H3 en Modal para dar movimiento FPV fluido, como la referencia four horsemen.

Uso:  MODAL_PROFILE=fgabriel60 modal run mariano_casa_modal.py::main
"""
import glob
import json
import os
import pathlib
import subprocess
import time
import modal

ANCHO, ALTO = 576, 1024
CARPETA = "mariano_casa_fpv"
LARGO = 124   # ~5 s a 24 fps

imagen = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("git", "ffmpeg")
    .run_commands("git clone --depth 1 https://github.com/comfyanonymous/ComfyUI /opt/ComfyUI")
    .pip_install("torch", "torchvision", "torchaudio")
    .run_commands("pip install -r /opt/ComfyUI/requirements.txt")
    .pip_install("pillow", "requests")
)
app = modal.App("mariano-casa-fpv", image=imagen)
datos = modal.Volume.from_name("h3-comprimido-gastro")

MANTENER = ("Keep the room exactly as in the image: same architecture, furniture, colors and light, nothing added, nothing removed, "
            "no people, no text, no warping or melting of straight lines. Smooth stable cinematic FPV drone glide, subtle motion blur, "
            "premium real-estate commercial look. Audio: soft airy whoosh, no music, no speech.")
# toma: (segundo del video real, movimiento)
TOMAS = {
    "E0": (0.0, "The camera flies low and fast toward the front door of the house, rising slightly, then glides past the entrance. "),
    "E1": (7.0, "The camera glides forward through the bright living room past the sofa and the TV wall. "),
    "E2": (13.2, "The camera glides forward past the kitchen counter toward the stainless steel refrigerator. "),
    "E3": (21.0, "The camera glides forward along the dining table under the pendant lights. "),
    "E4": (18.0, "The camera glides forward through the private patio between the planters and the bench, tilting up slightly to the sky. "),
    "E5": (38.0, "The camera glides forward into the bedroom toward the bed, soft natural light from the window. "),
    "E7": (0.8, "The camera pulls back and rises smoothly away from the front of the house, revealing the whole street and the neighboring houses under the blue sky. "),
    "E6": (48.2, "The camera glides forward over the rooftop terrace, rising slightly to reveal the sea on the horizon. "),
}


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
def clips(cuadros: dict, semilla: int = 2, solo: str = ""):
    import requests
    from PIL import Image
    import io

    carpeta = f"/datos/siena/{CARPETA}"
    os.makedirs(carpeta, exist_ok=True)
    for nombre, contenido in cuadros.items():
        img = Image.open(io.BytesIO(contenido)).convert("RGB")
        escala = max(ANCHO / img.width, ALTO / img.height)
        img = img.resize((round(img.width * escala), round(img.height * escala)), Image.LANCZOS)
        x, y = (img.width - ANCHO) // 2, (img.height - ALTO) // 2
        img.crop((x, y, x + ANCHO, y + ALTO)).save(f"{carpeta}/{nombre}.png")
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
    for toma, (_, mov) in TOMAS.items():
        if solo and toma not in solo.split(","):
            continue
        r = requests.post("http://127.0.0.1:8188/prompt", json={"prompt": _flujo(toma, None, None, mov + MANTENER, toma, semilla, LARGO)}).json()
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
        print("clip", toma, archivo, flush=True)
    log.close()
    datos.commit()
    return salida


@app.local_entrypoint()
def main(semilla: int = 2, solo: str = ""):
    import imageio_ffmpeg
    aqui = pathlib.Path(__file__).resolve().parent
    origen = pathlib.Path("/workspaces/Nexusv2.0launch18octubre/clientes/Mariano/whatsapp/del_cliente/20261017_173518_video.mp4")
    (aqui / "cuadros").mkdir(exist_ok=True); (aqui / "clips").mkdir(exist_ok=True)
    cuadros = {}
    for toma, (t, _) in TOMAS.items():
        png = aqui / "cuadros" / f"{toma}.png"
        subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-y", "-ss", str(t), "-i", str(origen), "-frames:v", "1", str(png)], check=True)
        cuadros[toma] = png.read_bytes()
    for nombre, contenido in clips.remote(cuadros, semilla, solo).items():
        (aqui / "clips" / f"{nombre}.mp4").write_bytes(contenido)
        print("guardado", aqui / "clips" / f"{nombre}.mp4")
