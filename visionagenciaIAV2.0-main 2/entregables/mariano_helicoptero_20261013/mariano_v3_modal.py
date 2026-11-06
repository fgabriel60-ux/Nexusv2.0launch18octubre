"""Mariano Herrera llega en helicóptero a San Marino (estilo del reel de referencia) — Modal.

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
CARPETA = "mariano_v3"

imagen = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("git", "ffmpeg")
    .run_commands("git clone --depth 1 https://github.com/comfyanonymous/ComfyUI /opt/ComfyUI")
    .pip_install("torch", "torchvision", "torchaudio")
    .run_commands("pip install -r /opt/ComfyUI/requirements.txt")
    .pip_install("git+https://github.com/huggingface/diffusers", "transformers", "accelerate", "pillow", "requests")
)
app = modal.App("mariano-v3", image=imagen)
datos = modal.Volume.from_name("h3-comprimido-gastro")
qwen = modal.Volume.from_name("qwen-image-edit-2511")

MARIANO = ("el hombre de la imagen 1 (hoja de personaje con 4 fotos reales de la MISMA persona: respeta exactamente su "
           "cara, nariz, cejas, frente amplia, barba completa canosa con bigote y pelo corto), saco azul claro de cuadros, "
           "camisa blanca, jeans y micrófono de solapa; presencia segura de influencer inmobiliario, aspecto real")
LUZ = ("misma iluminación cálida y suave de atardecer que favorece su rostro como en la imagen 3, "
       "lugar real de San Marino Residencial en Baja California: lomas secas, calles nuevas y el mar a cierta distancia "
       "como en la imagen 2 (NO Malibú, NO playa al pie de la casa)")
FOTO = "Foto vertical hiperrealista, cuerpo completo visible, espacio libre arriba de la cabeza, sin texto, sin letras."
CUADROS = {
    "V1": (["sanmarino", "sanmarino2"], "Vista de drone real de San Marino Residencial como en las imágenes 1 y 2: un helicóptero "
           "negro viene rápido desde el mar, a lo lejos, volando bajo hacia las lomas con casas blancas modernas y calles nuevas. "
           "Foto vertical hiperrealista, sin texto."),
    "V2": (["hoja", "sanmarino"], "Interior de la cabina de un helicóptero cayendo: el hombre de la imagen 1, misma cara y barba, "
           "con audífonos de piloto, sujetándose con cara de emoción y adrenalina, por la ventana se ven las lomas y casas de "
           "la imagen 2 inclinadas. Foto vertical hiperrealista, sin texto."),
    "V3": (["casa", "sanmarino"], "La casa blanca moderna de dos pisos de la imagen 1 en las lomas secas de la imagen 2: una "
           "explosión gigantesca de polvo café y tierra cubre todo el frente, el helicóptero queda completamente oculto dentro "
           "de la nube, escombros volando. Foto vertical hiperrealista, sin texto."),
    "V4": (["hoja", "casa", "luz_final"], f"{MARIANO}, sale caminando de una nube de polvo café que se disipa, frente a la casa "
           "blanca de la imagen 2 con la fachada dañada por el choque (grietas, ventana rota), el piso cubierto de escombros y "
           f"tierra, sin pasto, {LUZ}. " + FOTO),
    "V5": (["hoja", "casa", "luz_final"], f"{MARIANO}, de pie frente a la casa blanca de la imagen 2 intacta y limpia, la casa se "
           f"ve en parte a un lado, explicando con una mano abierta, {LUZ}, alrededor una residencial HABITADA y viva: casas blancas vecinas terminadas con jardines verdes, autos estacionados, calle pavimentada con banquetas y palmeras, vecinos a lo lejos, NO terreno baldío. " + FOTO),
    "V6": (["hoja", "casa", "luz_final"], f"{MARIANO}, caminando hacia la cámara frente a la casa blanca intacta de la imagen 2, "
           f"con una mano abierta invitando y sonrisa de confianza, {LUZ}, alrededor una residencial HABITADA y viva: casas blancas vecinas terminadas con jardines verdes, autos estacionados, calle pavimentada con banquetas y palmeras, vecinos a lo lejos, NO terreno baldío. " + FOTO),
}
GESTOS = ("natural, confident, varied and non-repetitive hand gestures with correct anatomy, influencer real estate presence, "
          "warm soft golden-hour light on his face, perfect lip sync to the given voice")
TOMAS = {
    "T1": ("V1", None, None, "Fast cinematic drone shot: a black helicopter races low from the distant sea toward dry hills with "
           "new white houses, then suddenly tilts and starts falling. Audio: loud rotor, alarm beeps, wind, no speech, no music."),
    "T1b": ("V2", None, None, "Inside a falling helicopter cockpit: the bearded man with pilot headset holds on with adrenaline, "
            "the cabin shakes violently, the hills spin outside the window. Audio: alarms, rotor, wind, no speech, no music."),
    "T1c": ("V3", "V4", None, "A gigantic brown dust explosion in front of a white modern house swallows the crashed helicopter; "
            "the dust clears quickly and the bearded man in the light blue blazer walks out of it over debris, dusting himself "
            "off. Audio: heavy impact, debris falling, dust whoosh, no speech, no music."),
    "T2": ("V4", None, "T2", "The bearded man in the light blue blazer walks out of the settling dust over debris in front of a "
           "damaged white house and talks to the camera in Mexican Spanish, " + GESTOS + "."),
    "T2b": ("V4", "V5", None, "Spectacular magical reconstruction: the cracked damaged white house rebuilds itself around the bearded man "
            "in the light blue blazer, debris flies back into place, walls repair, windows reassemble, grass and gardens grow, the "
            "neighborhood fills with finished houses and life. Smooth cinematic camera. Audio: magical whoosh and rebuilding "
            "sounds, no speech, no music."),
    "T3": ("V5", None, "T3", "Full body shot, the bearded man in the light blue blazer stands in front of a clean white modern house "
           "and talks to the camera in Mexican Spanish, " + GESTOS + "."),
    "T4": ("V6", None, "T4", "Full body shot, the bearded man in the light blue blazer walks toward the camera in front of a clean "
           "white modern house and talks in Mexican Spanish, ending pointing at the camera, " + GESTOS + "."),
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
                   negative_prompt="texto, letras, logotipo, deforme, borroso, otra cara",
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
    destino = aqui / ("cuadros_v3" if paso == "cuadros" else "clips_v3b")
    destino.mkdir(exist_ok=True)
    if paso == "cuadros":
        refs = {k: (aqui / "refs" / f"{k}.png").read_bytes() for k in ("casa", "sanmarino", "sanmarino2", "luz_final")}
        refs["hoja"] = (aqui / "refs" / "hoja_personaje.png").read_bytes()
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
