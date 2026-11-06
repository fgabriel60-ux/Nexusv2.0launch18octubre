"""XV Manuel v7 · 8 escenas de la FIESTA de la referencia «GIO XV» generadas SIN caras (siluetas, CO2, piso LED, vestido, DJ, celulares, robot, confeti).

1. `cuadros`: Qwen-Image-Edit-2511 lleva cada foto real del cliente a vertical 9:16 (mismo producto, mismo cuarto).
2. `clips`: MiniMax H3 anima cada cuadro (sin voz; la narración Fish va en armar.py).

Uso:  MODAL_PROFILE=fgabriel60 modal run jeremias_modal.py::main --paso cuadros   |   --paso clips
"""
import io, json, math, pathlib
import modal

ANCHO, ALTO = 576, 1024
CARPETA = "xv_v7"

imagen = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("git", "ffmpeg")
    .run_commands("git clone --depth 1 https://github.com/comfyanonymous/ComfyUI /opt/ComfyUI")
    .pip_install("torch", "torchvision", "torchaudio")
    .run_commands("pip install -r /opt/ComfyUI/requirements.txt")
    .pip_install("git+https://github.com/huggingface/diffusers", "transformers", "accelerate", "pillow", "requests")
)
app = modal.App("xv-v7", image=imagen)
datos = modal.Volume.from_name("h3-comprimido-gastro")
qwen = modal.Volume.from_name("qwen-image-edit-2511")

VERT = "Foto vertical 9:16 hiperrealista, sin texto, sin letras, sin logotipos. "
LOOK = "Iluminación de fiesta de cine como un video musical: salón oscuro con neblina azul turquesa, rayos de luz de escenario, acentos magenta y rosa, piso de pista de cristal iluminado con cuadrícula LED, pantallas LED al fondo, confeti brillando en el aire. "
SINCARA = "Nadie mira a la cámara, NO se ven caras de frente: solo siluetas a contraluz, espaldas, manos o figuras lejanas. "
CUADROS = {   # escenas de la fiesta de la referencia «GIO XV», SIN caras: la gente identificable va en video real
    "G1": (["salon"], "Vista desde atrás de la multitud: siluetas a contraluz con los brazos arriba frente al arco de flores blancas y las letras XV iluminadas de este salón. " + SINCARA + LOOK + VERT),
    "G2": (["salon"], "Cañones de CO2 disparando chorros blancos de humo frío sobre la pista llena de este salón, siluetas bailando a contraluz. " + SINCARA + LOOK + VERT),
    "G3": (["salon"], "Toma a ras de piso de la pista de cristal iluminada con cuadrícula LED, piernas y zapatos de gente bailando, confeti dorado cayendo, neblina. Solo se ven piernas, ninguna cara. " + LOOK + VERT),
    "G4": (["vestido"], "Este MISMO vestido verde esmeralda de quinceañera girando y abriéndose en vuelo sobre una pista de cristal iluminada, toma baja de la cintura para abajo, la tela se mueve. No se ve la cara, solo el vestido. " + LOOK + VERT),
    "G5": (["salon"], "Cabina de DJ en este salón: manos sobre la mezcladora con botones encendidos, de espaldas, frente a la pista llena con brazos arriba. " + SINCARA + LOOK + VERT),
    "G6": (["salon"], "Multitud de siluetas levantando las lámparas de sus celulares y pulseras luminosas, vista desde atrás, hacia el escenario con el arco de flores. " + SINCARA + LOOK + VERT),
    "G7": (["robot"], "Este MISMO robot de luces LED azules y verdes bailando en medio de la pista, rayos láser y humo, gente alrededor como siluetas a contraluz. " + SINCARA + LOOK + VERT),
    "G8": (["salon"], "Explosión de confeti dorado y plateado sobre la pista frente a las letras XV iluminadas y el arco de flores, siluetas de brazos arriba en primer plano. " + SINCARA + LOOK + VERT),
}
SUAVE = " Energetic music-video camera, smooth motion. Audio: party crowd ambience, no speech."
TOMAS = {
    "F1": ("G1", "Camera pushes forward through the crowd of silhouettes with raised arms toward the glowing XV stage, stage lights sweep, haze." + SUAVE),
    "F2": ("G2", "CO2 cannons blast white cold smoke jets over the dancing crowd, lights flash, camera slowly rises." + SUAVE),
    "F3": ("G3", "Low tracking shot gliding across the illuminated LED glass dance floor, feet dancing, golden confetti falling." + SUAVE),
    "F4": ("G4", "The emerald green ball gown spins and flares out in slow motion on the glowing dance floor, camera circles low around it." + SUAVE),
    "F5": ("G5", "DJ hands move the mixer knobs and raise one hand, the crowd jumps with raised arms in front, lights pulse." + SUAVE),
    "F6": ("G6", "Crowd silhouettes wave phone lights and glow bracelets side to side, camera drifts sideways, haze and stage beams." + SUAVE),
    "F7": ("G7", "The LED robot dances energetically in the middle of the floor, lasers sweep through the smoke, camera orbits." + SUAVE),
    "F8": ("G8", "Confetti cannons explode, gold and silver confetti rains over the crowd with raised arms in front of the XV letters, camera tilts up." + SUAVE),
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
                   negative_prompt="texto, letras, logotipo, deforme, borroso, cara, rostro, personas",
                   true_cfg_scale=4.0, guidance_scale=1.0, num_inference_steps=40, height=1280, width=720,
                   generator=torch.Generator("cuda").manual_seed(semilla)).images[0]
        img = _a_vertical(img)
        img.save(f"{carpeta}/{nombre}.png")
        b = io.BytesIO(); img.save(b, "PNG"); salida[nombre] = b.getvalue()
        print("cuadro", nombre, flush=True)
    datos.commit()
    return salida


def _flujo(inicio, prompt, prefijo, semilla, largo):
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
        "16": {"class_type": "BasicGuider", "inputs": {"model": ["121", 0], "conditioning": ["104", 0]}},
        "14": {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["15", 0], "guider": ["16", 0], "sampler": ["17", 0], "sigmas": ["9", 0], "latent_image": ["104", 1]}},
        "10": {"class_type": "VAEDecode", "inputs": {"samples": ["14", 0], "vae": ["11", 0]}},
        "23": {"class_type": "VAEDecodeAudio", "inputs": {"samples": ["14", 0], "vae": ["24", 0]}},
        "91": {"class_type": "CreateVideo", "inputs": {"images": ["10", 0], "audio": ["23", 0], "fps": 24}},
        "92": {"class_type": "SaveVideo", "inputs": {"video": ["91", 0], "filename_prefix": f"{CARPETA}/{prefijo}", "format": "auto", "codec": "auto"}},
    }
    return f


@app.function(gpu="A100-80GB", volumes={"/datos": datos}, timeout=5400)
def clips(cuadros_png: dict, semilla: int = 2, solo: str = ""):
    import glob, os, subprocess, time, requests

    carpeta = f"/datos/siena/{CARPETA}"
    os.makedirs(carpeta, exist_ok=True)
    for nombre, contenido in cuadros_png.items():
        open(f"{carpeta}/{nombre}.png", "wb").write(contenido)
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
        if solo and toma not in solo.split(","):
            continue
        r = requests.post("http://127.0.0.1:8188/prompt", json={"prompt": _flujo(inicio, prompt, toma, semilla, 124)}).json()
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
def main(paso: str = "cuadros", semilla: int = 5, solo: str = ""):
    aqui = pathlib.Path(__file__).resolve().parent
    destino = aqui / ("cuadros" if paso == "cuadros" else "clips")
    destino.mkdir(exist_ok=True)
    if paso == "cuadros":
        refs = {p.stem: p.read_bytes() for p in (aqui / "refs").glob("*.jpg")}
        res = cuadros.remote(refs, semilla, solo)
    else:
        res = clips.remote({p.stem: p.read_bytes() for p in (aqui / "cuadros").glob("*.png")}, semilla, solo)
    for nombre, contenido in res.items():
        (destino / f"{nombre}.{'png' if paso == 'cuadros' else 'mp4'}").write_bytes(contenido)
        print("guardado", destino / nombre)
