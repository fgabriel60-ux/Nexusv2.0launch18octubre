"""Omar (Red Natura) v2: su voz real con lip-sync y logo en la pared — Modal.

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
CARPETA = "jose"

imagen = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("git", "ffmpeg")
    .run_commands("git clone --depth 1 https://github.com/comfyanonymous/ComfyUI /opt/ComfyUI")
    .pip_install("torch", "torchvision", "torchaudio")
    .run_commands("pip install -r /opt/ComfyUI/requirements.txt")
    .pip_install("git+https://github.com/huggingface/diffusers", "transformers", "accelerate", "pillow", "requests")
)
app = modal.App("jose-v1", image=imagen)
datos = modal.Volume.from_name("h3-comprimido-gastro")
qwen = modal.Volume.from_name("qwen-image-edit-2511")

CASA = ("la misma azotea y casa de la imagen 1 en Puebla, México, con el volcán Popocatépetl al fondo, la casa mostrada en corte con su sala "
        "interior visible, fotografía vertical realista y cinematográfica, sin texto, sin letras, sin logotipos. ")
CUADROS = {
    "J1": (["gris"], "Cielo de tormenta muy oscuro y dramático sobre " + CASA + "Llueve fuerte, la azotea de concreto gris está agrietada con charcos "
           "y manchas de humedad, la sala interior se ve fría y oscura con una gotera."),
    "J2": (["gris"], "Primer plano de las manos de un obrero con guantes aplicando con un rodillo una capa delgada, uniforme y pareja de impermeabilizante blanco (sin charcos, sin chorreados, sin escurrimientos) "
           "sobre la azotea de concreto gris, mañana soleada y limpia, al fondo desenfocados las casas de Puebla y el volcán Popocatépetl. Fotografía "
           "vertical realista y cinematográfica, sin texto."),
    "J3": (["gris"], "Primer plano bajo y a ras de la superficie de una azotea completamente cubierta de impermeabilizante blanco, liso, mate y pareja; lluvia "
           "cayendo y gotas de agua redondas y perladas posadas sobre la superficie; al fondo desenfocados las casas de Puebla y el volcán Popocatépetl con cielo "
           "de tormenta que se abre con luz dorada. No se ve ningún borde de la azotea, ni paredes, ni el interior de la casa, ni escurrimientos. Fotografía "
           "vertical realista y cinematográfica, sin texto."),
    "J4": (["blanca"], "Mientras llueve afuera, " + CASA + "En la sala interior luminosa y seca una familia mexicana (mamá, papá y dos hijos) sentada en el sofá "
           "sonríe tranquila y segura, luz cálida, la azotea blanca arriba con gotas de lluvia."),
}
# toma: (cuadro inicial, cuadro final, voz, prompt)
TOMAS = {
    "J1": ("J1", None, None, "Cinematic vertical shot, heavy rain falling on a cracked gray concrete roof in Puebla with a stormy dark sky and the Popocatepetl "
           "volcano behind, slow push-in, raindrops splashing in puddles, thunderclouds moving. Audio: heavy rain and distant thunder, no music, no speech."),
    "J2": ("J2", None, None, "Cinematic close-up, gloved hands roll thick white waterproofing coating onto the gray concrete roof with a paint roller, the thin even white "
           "layer spreads smoothly behind the roller with no puddles and no dripping, sunny morning, slow tracking shot. Audio: soft roller sound, no music, no speech."),
    "J3": ("J3", None, None, "Cinematic vertical low-angle close-up of a perfectly smooth dry matte white waterproofed rooftop surface, rain falls and round water beads "
           "bounce and sit on the surface, the camera glides very slowly forward across the flat surface, the volcano and clouds opening to golden light blurred in the "
           "background. The roof edge and the walls are never visible, no water runs anywhere, nothing drips. Audio: rain on the roof, no music, no speech."),
    "J4": ("J4", None, None, "Cinematic vertical shot of a cozy dry living room seen from the cutaway, a smiling Mexican family on the sofa looks up relaxed "
           "while rain falls outside on the white roof, warm light, very slow push-in. Audio: soft rain, no music, no speech."),
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
                   negative_prompt="texto, letras, subtítulos, logotipo, deforme, borroso, pintura escurriendo, chorreado, goteo blanco, estalactitas de pintura, charcos de pintura",
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
        refs = {k: (aqui / "refs" / f"{k}.png").read_bytes() for k in ("gris", "blanca")}
        res = cuadros.remote(refs, semilla, solo)
    else:
        voces, dur = {}, {}
        for w in sorted((aqui / "voz").glob("G*.wav")):
            voces[w.stem] = w.read_bytes()
            err = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-i", str(w)], capture_output=True, text=True).stderr
            h, m, s = err.split("Duration: ")[1].split(",")[0].split(":")
            dur[w.stem] = int(h) * 3600 + int(m) * 60 + float(s)
        res = clips.remote(voces, dur, semilla, solo)
    for nombre, contenido in res.items():
        (destino / f"{nombre}.{'png' if paso == 'cuadros' else 'mp4'}").write_bytes(contenido)
        print("guardado", destino / nombre)
