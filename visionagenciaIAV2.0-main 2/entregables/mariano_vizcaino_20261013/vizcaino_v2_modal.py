"""Mariano llega en helicóptero a Vizcaíno Residencial (Rosarito) y presenta Bugambilia, Benjamina y Salvia — Modal.

Uso:  modal run vizcaino_modal.py::main --paso cuadros   |   modal run vizcaino_modal.py::main --paso clips
"""
import io
import json
import math
import pathlib
import modal

ANCHO, ALTO = 576, 1024
CARPETA = "mariano_vizcaino_v2"

imagen = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("git", "ffmpeg")
    .run_commands("git clone --depth 1 https://github.com/comfyanonymous/ComfyUI /opt/ComfyUI")
    .pip_install("torch", "torchvision", "torchaudio")
    .run_commands("pip install -r /opt/ComfyUI/requirements.txt")
    .pip_install("git+https://github.com/huggingface/diffusers", "transformers", "accelerate", "pillow", "requests")
)
app = modal.App("mariano-vizcaino-v2", image=imagen)
datos = modal.Volume.from_name("h3-comprimido-gastro")
qwen = modal.Volume.from_name("qwen-image-edit-2511")

MARIANO = ("el hombre de la imagen 1 (hoja de personaje con 4 fotos reales de la MISMA persona: respeta exactamente su "
           "cara, nariz, cejas, frente amplia, barba completa canosa con bigote y pelo corto), saco azul claro de cuadros, "
           "camisa blanca, jeans y micrófono de solapa; presencia segura de influencer inmobiliario, aspecto real")
LUZ = ("luz cálida de hora dorada que favorece su rostro como en la imagen 3, en Vizcaíno Residencial, Rosarito, Baja California: "
       "casas de dos pisos color arena con ventanas verticales y detalles de madera, pasto verde, andadores de concreto, cielo azul")
FOTO = "Foto vertical hiperrealista, cuerpo completo visible, espacio libre arriba de la cabeza, sin texto, sin letras."
MANOS = "manos relajadas con anatomía correcta, cinco dedos naturales, sin objetos en las manos"
AMPLIO = ("Foto vertical hiperrealista en PLANO AMPLIO: se ve de la cabeza a los zapatos completo, centrado, con espacio libre "
          "arriba y a los lados, cámara MUY lejos (a unos 6 metros): su cuerpo ocupa solo la mitad del alto del cuadro y se ven sus zapatos y el piso a sus pies (no primer plano), sin texto, sin letras. " + MANOS + ".")
VIZ = "las MISMAS casas de la imagen {n} (color arena, dos pisos, ventanas verticales con madera, pasto y andadores), sin cambiarlas ni dañarlas"
GALAN = "postura erguida y segura, se ve muy bien: saco planchado que le queda perfecto, sonrisa natural, presencia de estrella de cine"
HELI = "un helicóptero negro elegante y brillante, sin humo, sin polvo, sin daños"
CUADROS = {
    "R1": (["viz"], "Vista de dron a la hora dorada: " + HELI + " vuela suspendido a baja altura sobre la calle frente a " + VIZ.format(n=1) +
           "; de su puerta abierta cuelga una cuerda negra hasta el andador. Todo limpio e intacto. Foto vertical hiperrealista, cinematográfica, sin texto."),
    "R2": (["hoja", "viz", "luz_final"], f"{MARIANO}, {GALAN}, haciendo RAPPEL como agente de acción: cuelga vertical de UNA sola cuerda negra tensa, agarrándola con las dos manos "
           "a la altura del pecho, piernas juntas colgando rectas, sin asiento, sin columpio, sin arnés visible; arriba en la parte superior del cuadro flota " + HELI +
           " del que sale la cuerda; él va a media altura sobre el andador frente a " + VIZ.format(n=2) + f", {LUZ}. Cuerpo completo visible de la cabeza a los zapatos. "
           "Foto vertical hiperrealista, cinematográfica, sin texto."),
    "R3": (["hoja", "viz", "luz_final"], f"{MARIANO}, {GALAN}, acaba de aterrizar de pie en el andador de concreto soltando la cuerda negra que sube hacia " + HELI +
           " que flota arriba, frente a " + VIZ.format(n=2) + f", {LUZ}. Su rostro con iluminación buena y clara como en la imagen 3. " + AMPLIO),
    "R4a": (["viz"], "Vista de dron alta en picada mirando hacia abajo: " + HELI + " flota a dos metros ENCIMA del techo plano (azotea) de la casa de dos pisos del centro de "
            + VIZ.format(n=1) + ", con sus patines a punto de tocar la azotea; abajo se ven las otras casas y los andadores. Nada en el piso. A la hora dorada. "
            "Foto vertical hiperrealista, cinematográfica, sin texto."),
    "R4": (["viz"], HELI + " ya aterrizado y estacionado con cuidado sobre la azotea plana de la casa del centro de " + VIZ.format(n=1) +
           ", aspas quietas, a la hora dorada. Todo limpio e intacto, sin polvo. Foto vertical hiperrealista, cinematográfica, sin texto."),
    "R5": (["hoja", "viz", "luz_final"], f"{MARIANO}, {GALAN}, de pie en el andador de concreto frente a " + VIZ.format(n=2) + ", con " + HELI +
           f" estacionado sobre la azotea de la casa del centro detrás de él; habla a cámara con un gesto de mano abierta, {LUZ}. "
           "Rostro con iluminación buena y clara como en la imagen 3. " + AMPLIO),
    "R6": (["hoja", "viz", "luz_final"], f"{MARIANO}, {GALAN}, caminando hacia la cámara por el andador frente a la puerta de madera de una de " + VIZ.format(n=2) + ", con " + HELI +
           f" estacionado en una azotea al fondo, sonriendo con los brazos relajados, {LUZ}. Rostro con iluminación buena y clara como en la imagen 3. " + AMPLIO),
}
FIJO = ("STATIC locked-off tripod camera, wide full-body shot head to shoes, NO zoom, NO push-in, NO camera movement, face never "
        "enlarged; natural varied hand gestures at waist level, relaxed correct hands with five fingers, no objects in hands, no "
        "distorted fingers; warm soft golden-hour light on his face, perfect lip sync to the given voice")
TOMAS = {
    "T1": ("R1", "R2", None, "Epic cinematic Hollywood blockbuster shot at golden hour, anamorphic look, film grain: a sleek black helicopter hovers over the street of sand-colored "
           "two-story houses, the bearded man in the light blue blazer jumps out and slides fast down the black ropes like an action hero, landing smoothly on his feet on the walkway "
           "still holding the ropes. Full body visible. No smoke, no dust, nothing damaged. Starts instantly with action. Audio: helicopter rotor, wind, rope whoosh, no speech, no music."),
    "T1c": ("R2", "R3", None, "Cinematic slow-motion: the bearded man in the light blue blazer lets go of the black ropes, they rise back toward the hovering helicopter, he adjusts his blazer "
            "with a confident smile, full body visible, houses intact behind. Audio: rotor, wind, no speech, no music."),
    "T1d": ("R4a", None, None, "Cinematic golden-hour drone shot slowly orbiting a sleek black helicopter that has just landed on the flat rooftop of a sand-colored modern house, its rotor "
            "slowing down to a stop, everything clean and intact, no dust, no smoke. Smooth stable camera. Audio: rotor winding down, no speech, no music."),
    "T2": ("R5", None, "T2", "The bearded man in the light blue blazer stands on a concrete walkway in front of sand-colored modern houses, a black helicopter parked on a rooftop behind him, "
           "and talks to the camera in Mexican Spanish. " + FIJO + "."),
    "T4": ("R6", None, "T4", "The bearded man in the light blue blazer stands in front of a sand-colored house, a black helicopter parked on a rooftop in the background, and talks in "
           "Mexican Spanish, ending pointing at the camera. " + FIJO + "."),
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
                   true_cfg_scale=4.0, guidance_scale=1.0, num_inference_steps=40, height=1280, width=720,
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
    import subprocess
    import imageio_ffmpeg
    aqui = pathlib.Path(__file__).resolve().parent
    destino = aqui / ("cuadros_v2" if paso == "cuadros" else "clips_v2")
    destino.mkdir(exist_ok=True)
    if paso == "cuadros":
        refs = {k: (aqui / "refs" / f"{'vizcaino' if k == 'viz' else k}.png").read_bytes() for k in ("viz", "luz_final")}
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
