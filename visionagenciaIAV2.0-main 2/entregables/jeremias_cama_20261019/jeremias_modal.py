"""Jeremías (Mueblería Medina, Mérida) · transformación de cuarto vacío a recámara con SU cama de $3,500, como el reel de referencia.

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
CARPETA = "jeremias_cama"

imagen = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("git", "ffmpeg")
    .run_commands("git clone --depth 1 https://github.com/comfyanonymous/ComfyUI /opt/ComfyUI")
    .pip_install("torch", "torchvision", "torchaudio")
    .run_commands("pip install -r /opt/ComfyUI/requirements.txt")
    .pip_install("git+https://github.com/huggingface/diffusers", "transformers", "accelerate", "pillow", "requests")
)
app = modal.App("jeremias-cama", image=imagen)
datos = modal.Volume.from_name("h3-comprimido-gastro")
qwen = modal.Volume.from_name("qwen-image-edit-2511")

CAMA = ("la MISMA cama de la imagen 1, idéntica: cabecera negra tapizada con botones, colchón blanco empacado en plástico con su etiqueta, "
        "base negra de patas bajas y dos burós negros a los lados con lámparas blancas")
CUARTO = "una recámara amplia con una ventana grande con cortinas blancas de gasa y luz natural suave de la mañana"
ESTILO = "Foto vertical hiperrealista de interiorismo, cámara a la altura de los ojos, sin texto, sin letras, sin personas."
CUADROS = {   # encadenados: J2 se edita desde J1, J3 coloca la cama (imagen 1) en el cuarto de J2, J4 sale de J3
    "J1": (["vacio"], f"Crea una imagen nueva: {CUARTO} en OBRA NEGRA: muros y techo de concreto gris sin terminar, piso de cemento rústico, "
           "completamente VACÍA, sin cama ni muebles. " + ESTILO),
    "J2": (["J1"], "Edita esta recámara: la MISMA habitación, misma cámara y mismo encuadre, pero ya terminada: piso de duela de madera nogal brillante, "
           "TODOS los muros y el techo pintados de blanco liso y limpio (ya no se ve nada de concreto ni manchas), cielo raso con luz led cálida indirecta, cortinas blancas. Sigue completamente VACÍA, sin cama ni muebles. " + ESTILO),
    "J3": (["cama", "J2"], f"Coloca {CAMA} dentro de la recámara terminada de la imagen 2, centrada contra el muro del fondo sobre una alfombra gris clara, "
           "misma cámara, mismo encuadre, mismo piso, muros blancos lisos y mismas cortinas, luz cálida acogedora, sin manchas ni concreto. " + ESTILO),
    "J4": (["cama", "J3"], f"Crea una imagen nueva: acercamiento macro cinematográfico a la esquina del colchón blanco de {CAMA}, en la recámara de la imagen 2 con muros blancos lisos, "
           "una mano de persona adulta presiona suavemente la superficie del colchón y se hunde con suavidad, luz cálida de recámara. Foto vertical hiperrealista, sin texto."),
}
TOMAS = {
    "T1": ("J1", "J2", None, "Cinematic interior transformation: the camera slowly pushes forward in a raw concrete empty bedroom while a polished walnut wood floor, "
           "white walls and warm ceiling lights magically spread across the space until the room is finished. Smooth steady camera. "
           "Audio: soft magical whoosh and shimmer, no music, no speech."),
    "T2": ("J2", "J3", None, "The same finished empty bedroom: the camera keeps pushing in slowly while a black upholstered bed with a white mattress and two black nightstands "
           "with lamps assemble themselves piece by piece and appear in the room, light sparkles at each piece. Smooth steady camera. "
           "Audio: gentle whoosh and soft pops, no music, no speech."),
    "T3": ("J3", "J4", None, "The camera glides forward quickly and softly toward the bed and ends in a macro close-up of the white mattress as an adult hand gently presses it "
           "and it sinks softly, slow motion, warm light. Audio: soft fabric sound, no music, no speech."),
    "T4": ("J3", None, None, "Slow elegant cinematic push-in on the finished bedroom with the black upholstered bed, white mattress and black nightstands with glowing lamps, "
           "warm light, tiny dust motes floating. The bed and room stay exactly the same. Audio: calm room tone, no music, no speech."),
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
                   negative_prompt="texto, letras, logotipo, deforme, borroso, otra cara" + (", cama, colchón, base de cama, burós, lámparas, muebles, objetos" if nombre in ("J1", "J2") else ""),
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
    aqui = pathlib.Path(__file__).resolve().parent
    destino = aqui / ("cuadros" if paso == "cuadros" else "clips")
    destino.mkdir(exist_ok=True)
    if paso == "cuadros":
        from PIL import Image
        gris = io.BytesIO(); Image.new("RGB", (720, 1280), (150, 150, 150)).save(gris, "PNG")   # referencia neutra sin muebles para J1
        refs = {"cama": (aqui / "refs" / "cama.jpg").read_bytes(), "vacio": gris.getvalue()}
        if (aqui / "cuadros" / "J1.png").exists():
            refs["J1"] = (aqui / "cuadros" / "J1.png").read_bytes()          # J1 ya aprobado: se conserva
        res = cuadros.remote(refs, semilla, solo)
    else:
        res = clips.remote({}, {}, semilla, solo, {n: (aqui / "cuadros" / f"{n}.png").read_bytes() for n in ("J1", "J2", "J3", "J4")})
    for nombre, contenido in res.items():
        (destino / f"{nombre}.{'png' if paso == 'cuadros' else 'mp4'}").write_bytes(contenido)
        print("guardado", destino / nombre)
