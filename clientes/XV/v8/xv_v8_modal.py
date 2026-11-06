"""XV Manuel v8 (video musical sobre la canción de GIO XV) — antes v7 · 8 escenas de la FIESTA de la referencia «GIO XV» generadas SIN caras (siluetas, CO2, piso LED, vestido, DJ, celulares, robot, confeti).

1. `cuadros`: Qwen-Image-Edit-2511 lleva cada foto real del cliente a vertical 9:16 (mismo producto, mismo cuarto).
2. `clips`: MiniMax H3 anima cada cuadro (sin voz; la narración Fish va en armar.py).

Uso:  MODAL_PROFILE=fgabriel60 modal run jeremias_modal.py::main --paso cuadros   |   --paso clips
"""
import io, json, math, pathlib
import modal

ANCHO, ALTO = 576, 1024
CARPETA = "xv_v8"

imagen = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("git", "ffmpeg")
    .run_commands("git clone --depth 1 https://github.com/comfyanonymous/ComfyUI /opt/ComfyUI")
    .pip_install("torch", "torchvision", "torchaudio")
    .run_commands("pip install -r /opt/ComfyUI/requirements.txt")
    .pip_install("git+https://github.com/huggingface/diffusers", "transformers", "accelerate", "pillow", "requests")
)
app = modal.App("xv-v8", image=imagen)
datos = modal.Volume.from_name("h3-comprimido-gastro")
qwen = modal.Volume.from_name("qwen-image-edit-2511")

VERT = "Foto vertical 9:16 hiperrealista de cine, sin texto, sin letras, sin logotipos. "
LOOK = ("Look de video musical de fiesta de quinceañera: ESTE salón cálido con candiles de cristal, arco de flores blancas y letras XV iluminadas, "
        "luz dorada cálida con acentos de escenario magenta y azul, neblina suave, grano fino de cine. ")
SINCARA = "No se ve ninguna cara de frente: espalda, silueta a contraluz, manos o detalle. "
CUADROS = {   # v8: escenas que le faltan al video musical (apertura, preparación, detalles, contraluz, clímax), en el MISMO salón y con el MISMO vestido
    "H1": (["salon"], "Vista aérea nocturna tipo dron de un salón de eventos elegante iluminado con luces cálidas doradas, jardín con focos colgantes, cielo azul profundo de noche, "
           "por las ventanas se ven los candiles encendidos. " + VERT),
    "H2": (["vestido"], "Este MISMO vestido verde esmeralda de quinceañera colgado de un gancho dorado junto a una ventana con cortinas, luz dorada de tarde, polvo brillando en el aire, "
           "recámara elegante, la tiara sobre un tocador. Sin personas. " + VERT),
    "H3": (["retrato"], "Macro extremo de la tiara verde esmeralda y plateada sobre el cabello oscuro rizado, vista desde atrás, destellos de luz en los cristales, fondo desenfocado cálido. " + SINCARA + VERT),
    "H4": (["vestido", "salon"], "Quinceañera de espaldas con este MISMO vestido verde esmeralda (imagen 1) entrando al salón de la imagen 2, silueta a contraluz con luz dorada y neblina, "
           "las puertas abiertas y los candiles al fondo. " + SINCARA + LOOK + VERT),
    "H5": (["vestido_pista", "salon"], "Este MISMO vestido verde esmeralda girando y abriéndose en vuelo en la pista del salón, toma baja de la cintura para abajo, confeti dorado cayendo, "
           "luces de escenario. " + SINCARA + LOOK + VERT),
    "H6": (["vestido", "salon"], "Retrato de espalda de la quinceañera con este MISMO vestido verde esmeralda frente al arco de flores blancas y las letras XV, neblina, "
           "contraluz rosa y azul del escenario. " + SINCARA + LOOK + VERT),
    "H7": (["robot", "salon"], "Este MISMO robot de luces LED azules y verdes bailando en la pista de este salón con candiles, chorros de humo blanco de CO2 a los lados, "
           "invitados como siluetas a contraluz con brazos arriba. " + SINCARA + LOOK + VERT),
}
SUAVE = " Cinematic music-video camera, smooth motion, warm film look. Audio: soft party ambience, no speech."
TOMAS = {
    "M1": ("H1", "Slow aerial drone push-in toward the glowing event hall at night, warm lights twinkle." + SUAVE),
    "M2": ("H2", "Slow dolly toward the emerald ball gown hanging by the window, dust sparkles drift in golden light, curtain moves gently." + SUAVE),
    "M3": ("H3", "Extreme macro slow orbit around the emerald tiara, light glints sparkle on the crystals, shallow depth of field." + SUAVE),
    "M4": ("H4", "The girl in the emerald ball gown walks slowly away from camera through the open doors into the hall, backlit, haze, slow motion." + SUAVE),
    "M5": ("H5", "The emerald gown spins and flares in slow motion on the dance floor, golden confetti falling, camera low." + SUAVE),
    "M6": ("H6", "Slow push-in on the girl from behind facing the white flower arch and glowing XV letters, haze drifts, pink and blue light pulses." + SUAVE),
    "M7": ("H7", "The LED robot dances energetically as CO2 jets blast white smoke, guests jump with raised arms, lights flash." + SUAVE),
    "M8": ("H1", "Slow aerial drone pulling back and rising away from the glowing event hall at night, ending wide." + SUAVE),
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
                   negative_prompt="texto, letras, logotipo, deforme, borroso, cara de frente, rostro mirando a cámara, antro, láser",
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
