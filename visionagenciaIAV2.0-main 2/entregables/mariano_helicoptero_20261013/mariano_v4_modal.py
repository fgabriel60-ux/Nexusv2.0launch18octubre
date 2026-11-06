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
CARPETA = "mariano_v4"

imagen = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("git", "ffmpeg")
    .run_commands("git clone --depth 1 https://github.com/comfyanonymous/ComfyUI /opt/ComfyUI")
    .pip_install("torch", "torchvision", "torchaudio")
    .run_commands("pip install -r /opt/ComfyUI/requirements.txt")
    .pip_install("git+https://github.com/huggingface/diffusers", "transformers", "accelerate", "pillow", "requests")
)
app = modal.App("mariano-v4", image=imagen)
datos = modal.Volume.from_name("h3-comprimido-gastro")
qwen = modal.Volume.from_name("qwen-image-edit-2511")

MARIANO = ("el hombre de la imagen 1 (hoja de personaje con 4 fotos reales de la MISMA persona: respeta exactamente su "
           "cara, nariz, cejas, frente amplia, barba completa canosa con bigote y pelo corto), saco azul claro de cuadros, "
           "camisa blanca, jeans y micrófono de solapa; presencia segura de influencer inmobiliario, aspecto real")
LUZ = ("misma iluminación cálida y suave de atardecer que favorece su rostro como en la imagen 3, "
       "lugar real de San Marino Residencial en Baja California: lomas secas, calles nuevas y el mar a cierta distancia "
       "como en la imagen 2 (NO Malibú, NO playa al pie de la casa)")
FOTO = "Foto vertical hiperrealista, cuerpo completo visible, espacio libre arriba de la cabeza, sin texto, sin letras."
MANOS = "manos relajadas con anatomía correcta, cinco dedos naturales, sin objetos en las manos"
AMPLIO = ("Foto vertical hiperrealista en PLANO AMPLIO: se ve de la cabeza a los zapatos completo, centrado, con espacio libre "
          "arriba y a los lados, cámara MUY lejos (a unos 6 metros): su cuerpo ocupa solo la mitad del alto del cuadro y se ven sus zapatos y el piso a sus pies (no primer plano), sin texto, sin letras. " + MANOS + ".")
BARRIO = ("alrededor una residencial TERMINADA, LIMPIA y habitada, igual a la imagen 2: hilera larga de casas blancas modernas idénticas "
          "a ambos lados, calle pavimentada limpia con banquetas, pasto verde cuidado, autos estacionados, cielo azul, "
          "SIN terreno baldío, SIN tierra seca, SIN mar ni playa al fondo")
CUADROS = {
    "V1": (["sanmarino2"], "El MISMO barrio real de la imagen 1 (mismas casas, misma calle con palmeras, sin cambiarlas), visto desde un dron "
           "cercano: un helicóptero negro GRANDE ocupa un tercio del cuadro en primer plano, con una columna de humo negro espeso saliendo del motor, "
           "girando en picada (inclinado casi vertical) sobre la calle. Foto vertical hiperrealista, sin texto."),
    "V2": (["hoja", "sanmarino2"], "Interior de la cabina de un helicóptero cayendo: el hombre de la imagen 1, misma cara y barba, con "
           "audífonos de piloto, agarrándose del asiento con cara de emoción, por la ventana se ve el mismo barrio de la imagen 2 "
           "inclinado. Foto vertical hiperrealista, sin texto."),
    "V3": (["casa", "sanmarino2"], "La casa blanca moderna de la imagen 1 en el barrio de la imagen 2: un helicóptero negro GRANDE, que ocupa "
           "buena parte del cuadro, se estrella contra la fachada; explosión gigantesca de polvo café y escombros volando. "
           "Foto vertical hiperrealista, sin texto."),
    "V4": (["hoja", "casa", "luz_final"], f"{MARIANO}, camina hacia la cámara frente a la casa blanca de la imagen 2 con la fachada dañada "
           "por el choque (grietas, ventana rota), el polvo del choque ya está en el aire y se está asentando detrás de él, escombros "
           f"en el piso, sin pasto, {LUZ}. Su rostro con iluminación buena y clara como en la imagen 3. " + AMPLIO),
    "V5": (["hoja", "calle1", "luz_final"], f"{MARIANO}. Colócalo de pie, centrado, en la calle real de la imagen 2 (mismo vecindario de casas blancas modernas en hilera, mismo asfalto ancho, mismo cielo azul) SUSTITUYENDO por completo al hombre que aparece ahí; "
           "no cambies las casas ni la calle. Lleva jeans azules y NO lleva cordón ni gafete. Habla a cámara con un gesto de mano abierta, rostro con iluminación buena y clara como en la imagen 3. " + AMPLIO),
    "V6": (["hoja", "calle2", "luz_final"], f"{MARIANO}. Colócalo caminando hacia la cámara, centrado, en la calle real de la imagen 2 (mismas casas blancas modernas pegadas a la calle, mismo asfalto, mismo cielo azul) SUSTITUYENDO por completo al hombre que aparece ahí; "
           "no cambies las casas ni la calle. Lleva jeans azules (NO pantalón verde olivo) y NO lleva cordón ni gafete al cuello. Sonríe con los brazos relajados a los lados, rostro con iluminación buena y clara como en la imagen 3. " + AMPLIO),
}
FIJO = ("STATIC locked-off tripod camera, wide full-body shot head to shoes, NO zoom, NO push-in, NO camera movement, face never "
        "enlarged; natural varied hand gestures at waist level, relaxed correct hands with five fingers, no objects in hands, no "
        "distorted fingers; warm soft golden-hour light on his face, perfect lip sync to the given voice")
TOMAS = {
    "T1": ("V1", None, None, "Epic cinematic Hollywood blockbuster shot, anamorphic look, dramatic slow-motion, rich contrast and film grain, low dynamic camera: the large black helicopter in the foreground, already trailing thick black smoke from the engine, spins violently around its axis "
           "in a nosedive plunge toward the neighborhood street, smoke spiraling behind it. Starts instantly with action. Audio: loud rotor, alarm beeps, "
           "no speech, no music."),
    "T1b": ("V2", None, None, "Cinematic blockbuster handheld shot inside a falling helicopter cockpit: the bearded man with pilot headset holds on with adrenaline, "
            "the cabin shakes violently. Starts instantly. Audio: alarms, rotor, wind, no speech, no music."),
    "T1c": ("V3", "V4", None, "Epic cinematic slow-motion blockbuster impact: the big black helicopter slams into the white house, a gigantic brown dust explosion; the dust is already "
            "settling when the bearded man in the light blue blazer walks out of it toward the camera. Static wide framing. Audio: "
            "heavy impact, debris falling, no speech, no music."),
    "T2": ("V4", None, "T2", "The bearded man in the light blue blazer stands in front of a damaged white house with settled dust and "
           "talks to the camera in Mexican Spanish. " + FIJO + "."),
    "T3": ("V5", None, "T3", "The bearded man in the light blue blazer stands in a clean residential street and talks to the camera "
           "in Mexican Spanish. " + FIJO + "."),
    "T4": ("V6", None, "T4", "The bearded man in the light blue blazer stands in a clean residential street and talks in Mexican "
           "Spanish, ending pointing at the camera. " + FIJO + "."),
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
    destino = aqui / ("cuadros_v4" if paso == "cuadros" else "clips_v4")
    destino.mkdir(exist_ok=True)
    if paso == "cuadros":
        refs = {k: (aqui / "refs" / f"{k}.png").read_bytes() for k in ("casa", "sanmarino", "sanmarino2", "luz_final", "calle1", "calle2")}
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
