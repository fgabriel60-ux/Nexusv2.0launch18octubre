"""XV Manuel: planos «mágicos» generados con MiniMax H3 a partir de las FOTOS reales de la quinceañera (identidad y vestido se conservan: la foto es el primer cuadro).
Uso: modal run xv_modal.py --toma S1     (un plano a la vez; se autoriza el siguiente)"""
import io, json, math, pathlib
import modal

ANCHO, ALTO = 576, 1024
CARPETA = "xv_manuel"
imagen = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("git", "ffmpeg")
    .run_commands("git clone --depth 1 https://github.com/comfyanonymous/ComfyUI /opt/ComfyUI")
    .pip_install("torch", "torchvision", "torchaudio")
    .run_commands("pip install -r /opt/ComfyUI/requirements.txt")
    .pip_install("pillow", "requests")
)
app = modal.App("xv-manuel", image=imagen)
datos = modal.Volume.from_name("h3-comprimido-gastro")

# toma: (foto, centrado vertical del recorte, prompt)
TOMAS = {
    "S1": ("BV8B6048-Editar", .38, "Cinematic vertical close-up portrait of a young woman in an emerald green ball gown with a jeweled tiara, smiling softly and holding a bouquet of red roses. "
           "Very slow gentle push-in, she blinks naturally and tilts her head slightly, her curled hair and the tulle move softly in a light breeze, warm golden light, shallow depth of field, "
           "filmic look. Keep her face, dress and roses exactly as in the first frame. No text. Audio: soft ambient, no speech."),
    "S2": ("S2_salon", .5, "Cinematic vertical shot gliding slowly forward through an empty quinceañera reception hall: a white floral arch with soft green uplights, glowing XV letters, polished wooden dance floor with golden confetti, "
           "warm chandeliers. Smooth steady dolly-in toward the arch, gentle sparkle of the lights and confetti, filmic look. Keep the hall exactly as in the first frame. No people, no text changes. Audio: soft hall ambience, no speech."),
    "S3": ("BV8B6090", .45, "Cinematic vertical wide-angle shot of a young woman in an emerald green ball gown with a jeweled tiara standing in front of a rustic wooden door. "
           "She smiles, lifts the sides of her gown with both hands and does a small graceful twirl, the tulle skirt flowing and sparkling in warm golden light, "
           "the camera pushes in slowly with a slight wide-angle fisheye feel. Keep her face, tiara and dress exactly as in the first frame. No text. Audio: soft ambient, no speech."),
    "S4": ("S4_base", .5, "Cinematic vertical macro close-up of a bouquet of red roses held in a young woman's hands with a beaded emerald green sleeve. "
           "Very slow push-in with soft rack focus, tiny golden sparkles and warm bokeh lights drifting in the background, the rose petals shimmer slightly. "
           "Keep the roses, hands and sleeve exactly as in the first frame. No text. Audio: soft ambient, no speech."),
    "S5": ("S5_base", .5, "Cinematic vertical shot of a young woman in an emerald green ball gown and jeweled tiara standing beside a black horse in a sunny plaza. "
           "Slow smooth camera push-in with a very slight orbit, the horse breathes and gently moves its head and mane, her curled hair and the tulle move softly in a light breeze, warm sunlight. "
           "She stays standing almost still, looking at the camera with a calm soft expression, no turning, no big movements. Keep her face, tiara, dress and the horse exactly as in the first frame. No text. Audio: soft ambient, no speech."),
}


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



@app.function(gpu="A100-80GB", volumes={"/datos": datos}, timeout=3600)
def clip(foto: bytes, prompt: str, nombre: str, semilla: int = 2):
    import glob, os, subprocess, time, requests
    carpeta = f"/datos/siena/{CARPETA}"
    os.makedirs(carpeta, exist_ok=True)
    open(f"{carpeta}/{nombre}.png", "wb").write(foto)
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
    r = requests.post("http://127.0.0.1:8188/prompt", json={"prompt": _flujo(nombre, None, None, prompt, nombre, semilla, 124)}).json()
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
    archivo = sorted(glob.glob(f"/datos/siena/out/{CARPETA}/{nombre}_*.mp4"), key=os.path.getmtime)[-1]
    datos.commit()
    return open(archivo, "rb").read()


@app.local_entrypoint()
def main(toma: str = "S1", semilla: int = 2):
    from PIL import Image, ImageOps
    aqui = pathlib.Path(__file__).resolve().parent
    foto, cy, prompt = TOMAS[toma]
    ruta = aqui / "modal_tomas" / f"{foto}.png"
    if not ruta.exists(): ruta = aqui / "originales" / f"{foto}.jpg"
    im = Image.open(ruta).convert("RGB"); im.draft("RGB", (1500, 2000))
    im = ImageOps.fit(im, (ANCHO, ALTO), Image.LANCZOS, centering=(.5, cy))
    b = io.BytesIO(); im.save(b, "PNG")
    (aqui / "modal_tomas").mkdir(exist_ok=True)
    im.save(aqui / "modal_tomas" / f"{toma}_primer_cuadro.png")
    (aqui / "modal_tomas" / f"{toma}.mp4").write_bytes(clip.remote(b.getvalue(), prompt, toma, semilla))
    print("guardado", aqui / "modal_tomas" / f"{toma}.mp4")
