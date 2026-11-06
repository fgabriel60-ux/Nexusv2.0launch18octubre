"""Mariano · flyers nuevos (Sotol familia y Bugambilia «La mejor opción»): Qwen-Image-Edit-2511 borra el texto → cuadro limpio;
MiniMax H3 (fl2va fp8 + LoRA turbo 8 pasos) anima el cuadro limpio. El texto ORIGINAL se superpone después en armar_flyers_nuevos.py.
UNA sola GPU (A100-80GB) por llamada, todo secuencial dentro de la función (sin starmap).

Uso (perfil fijo):
  MODAL_PROFILE=fabelagabriel645 modal run flyers_nuevos_modal.py --paso limpio [--solo sotol] [--semilla 5]
  MODAL_PROFILE=fabelagabriel645 modal run flyers_nuevos_modal.py --paso clip  [--solo bugambilia2] [--semilla 7] [--sufijo _r2]
Salida: nuevos/<flyer>/limpio.png · nuevos/<flyer>/clip<sufijo>.mp4"""
import io, json, pathlib
import modal
from flyers_modal import imagen, datos, qwen, CARPETA

app = modal.App("mariano-flyers-nuevos", image=imagen.add_local_python_source("flyers_modal"))
AQUI = pathlib.Path(__file__).resolve().parent
RECIBIDOS = AQUI.parent / "flyers_recibidos"
ANCHO, ALTO = 704, 1280          # H3 (el cuadro 9:16 se comprime 2 % en X y se re-estira al armar)
LARGO = 175                       # 175 cuadros a 24 fps = 7.3 s (largo ≡ 5 mod 17): animación completa, sin cuadros congelados

FLYERS = {
    "sotol": {
        "original": "1018_005111_BA9020.jpg",
        "limpiar": ("Elimina TODO el texto y los gráficos superpuestos de este flyer: el titular blanco de arriba, el recuadro azul con el modelo y el precio, "
                    "las cuatro etiquetas con borde blanco, el logotipo Vizcaíno Residencial, el ícono de ubicación y su texto, las líneas divisorias verticales, "
                    "el logotipo Grupo Lagsa y las letras pequeñas. Reconstruye detrás de ellos de forma natural el techo de madera, las lámparas, la silla café, "
                    "el piso, el tapete y el sillón. Conserva EXACTAMENTE a la familia (mamá, papá, niño y niña), sus caras, manos, ropa y poses, la mesa, "
                    "la cocina, la composición, los colores y la luz cálida. No agregues nada."),
        "mover": ("Warm cozy family lifestyle scene in a modern kitchen, cinematic real-estate commercial. A smooth, clearly visible slow camera push-in toward the family at the table. "
                  "The mother gently tosses the salad with the wooden spoons, the father slowly turns the pepper grinder, the boy and the girl smile and look at their parents, "
                  "small natural head movements and blinking, a thin wisp of steam rises from the bowl, the three pendant lamps glow warm, the plant leaves sway slightly. "
                  "Faces, hands and fingers stay natural and undistorted, everyone keeps their identity, no extra people, no text. Audio: soft cozy kitchen ambience, no speech."),
        "ultimo": False,          # solo primer cuadro: el push-in de cámara es real
    },
    "bugambilia2": {
        "original": "1020_210408_4AF9D8.jpg",
        "limpiar": ("Elimina TODO el texto y los gráficos de este flyer: el titular, el precio con la palabra DESDE, la frase de abajo del precio, las cuatro etiquetas ovaladas, "
                    "la palabra CASA y la palabra gigante BUGAMBILIA, y en la franja gris de abajo el logotipo Vizcaíno Residencial, el ícono de ubicación con su texto, "
                    "las letras pequeñas y el logotipo Grupo Lagsa. Deja el fondo blanco liso arriba y la franja gris lisa abajo, y completa la copa del árbol de la izquierda. "
                    "Conserva EXACTAMENTE la casa blanca con su luz, la persona en la ventana, los árboles, los arbustos, el pasto, la banqueta y el cielo del atardecer, "
                    "su posición, tamaño y colores. No agregues nada."),
        "mover": ("Golden-hour real-estate commercial of a modern white two-story house. The warm entrance light and the vertical LED light strips on the facade glow and pulse softly, "
                  "the interior window lights brighten, the sun flares gently on the right, soft clouds drift slowly across the sky, the tree leaves and the bushes sway in a light breeze, "
                  "the grass moves slightly. The house keeps its exact shape and position, the white area at the top and the grey band at the bottom stay plain and still. "
                  "No text. Audio: soft evening breeze ambience, no speech."),
        "ultimo": True,           # primer y último cuadro iguales: la casa no se deforma; el push-in se hace digital al armar
    },
}


def _flujo(nombre, prompt, semilla, largo, ultimo):
    f = {
        "6": {"class_type": "UNETLoader", "inputs": {"unet_name": "minimax_h3_fl2va_pruned_fp8_scaled.safetensors", "weight_dtype": "default"}},
        "121": {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["6", 0], "lora_name": "minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors", "strength_model": 1.0}},
        "13": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors", "type": "minimax", "device": "default"}},
        "11": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_video_vae_fp16.safetensors"}},
        "24": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_audio_vae_fp32.safetensors"}},
        "30": {"class_type": "LoadImage", "inputs": {"image": f"{CARPETA}/{nombre}.png"}},
        "104": {"class_type": "MiniMaxH3ImageToVideo", "inputs": {"clip": ["13", 0], "vae": ["11", 0], "prompt": prompt, "width": ANCHO, "height": ALTO, "length": largo,
                                                                  "first_frame": ["30", 0]}},
        "15": {"class_type": "RandomNoise", "inputs": {"noise_seed": semilla}},
        "17": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "res_multistep"}},
        "9": {"class_type": "BasicScheduler", "inputs": {"model": ["121", 0], "scheduler": "simple", "steps": 8, "denoise": 1.0}},
        "16": {"class_type": "BasicGuider", "inputs": {"model": ["121", 0], "conditioning": ["104", 0]}},
        "14": {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["15", 0], "guider": ["16", 0], "sampler": ["17", 0], "sigmas": ["9", 0], "latent_image": ["104", 1]}},
        "10": {"class_type": "VAEDecode", "inputs": {"samples": ["14", 0], "vae": ["11", 0]}},
        "23": {"class_type": "VAEDecodeAudio", "inputs": {"samples": ["14", 0], "vae": ["24", 0]}},
        "91": {"class_type": "CreateVideo", "inputs": {"images": ["10", 0], "audio": ["23", 0], "fps": 24}},
        "92": {"class_type": "SaveVideo", "inputs": {"video": ["91", 0], "filename_prefix": f"{CARPETA}/{nombre}", "format": "auto", "codec": "auto"}},
    }
    if ultimo:
        f["31"] = {"class_type": "LoadImage", "inputs": {"image": f"{CARPETA}/{nombre}.png"}}
        f["104"]["inputs"]["last_frame"] = ["31", 0]
    return f


@app.function(gpu="A100-80GB", volumes={"/datos": datos, "/qwen": qwen}, timeout=3600)
def limpiar(trabajos: dict, semilla: int = 5) -> dict:
    """trabajos: {nombre: (png_720x1280, prompt)} → {nombre: png limpio 720x1280}"""
    import torch
    from PIL import Image
    from diffusers import QwenImageEditPlusPipeline
    pipe = QwenImageEditPlusPipeline.from_pretrained("/qwen/Qwen-Image-Edit-2511", torch_dtype=torch.bfloat16).to("cuda")
    out = {}
    for n, (png, prompt) in trabajos.items():
        im = pipe(image=[Image.open(io.BytesIO(png)).convert("RGB")], prompt=prompt,
                  negative_prompt="texto, letras, números, logotipo, íconos, etiquetas, botones, marca de agua, deforme, borroso, caras deformes, manos deformes",
                  true_cfg_scale=4.0, guidance_scale=1.0, num_inference_steps=40, height=1280, width=720,
                  generator=torch.Generator("cuda").manual_seed(semilla)).images[0]
        b = io.BytesIO(); im.save(b, "PNG"); out[n] = b.getvalue(); print("limpio", n, flush=True)
    return out


@app.function(gpu="A100-80GB", volumes={"/datos": datos}, timeout=5400)
def animar(trabajos: dict, semilla: int = 5) -> dict:
    """trabajos: {nombre: (png, prompt, ultimo)} → {nombre: mp4}. Un ComfyUI, clips en serie."""
    import glob, os, subprocess, time, requests
    from PIL import Image
    carpeta = f"/datos/siena/{CARPETA}"; os.makedirs(carpeta, exist_ok=True)
    for n, (png, _, _) in trabajos.items():
        Image.open(io.BytesIO(png)).convert("RGB").resize((ANCHO, ALTO), Image.LANCZOS).save(f"{carpeta}/{n}.png")
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
    out = {}
    for n, (_, prompt, ultimo) in trabajos.items():
        t0 = time.time()
        r = requests.post("http://127.0.0.1:8188/prompt", json={"prompt": _flujo(n, prompt, semilla, LARGO, ultimo)}).json()
        if "prompt_id" not in r:
            raise RuntimeError(json.dumps(r)[:3000])
        pid = r["prompt_id"]
        while True:
            h = requests.get(f"http://127.0.0.1:8188/history/{pid}").json()
            if pid in h:
                if h[pid].get("status", {}).get("status_str") == "error":
                    raise RuntimeError(json.dumps(h[pid]["status"])[:3000])
                break
            time.sleep(5)
        archivo = sorted(glob.glob(f"/datos/siena/out/{CARPETA}/{n}_*.mp4"), key=os.path.getmtime)[-1]
        out[n] = open(archivo, "rb").read(); print("clip", n, f"{time.time() - t0:.0f}s", flush=True)
    datos.commit()
    return out


@app.local_entrypoint()
def main(paso: str = "limpio", solo: str = "", semilla: int = 5, sufijo: str = ""):
    from PIL import Image
    nombres = [n for n in FLYERS if not solo or n in solo.split(",")]
    if paso == "limpio":
        trabajos = {}
        for n in nombres:
            d = AQUI / "nuevos" / n; d.mkdir(parents=True, exist_ok=True)
            Image.open(RECIBIDOS / FLYERS[n]["original"]).convert("RGB").resize((720, 1280), Image.LANCZOS).save(d / "flyer_720.png")
            trabajos[n] = ((d / "flyer_720.png").read_bytes(), FLYERS[n]["limpiar"])
        for n, v in limpiar.remote(trabajos, semilla).items():
            p = AQUI / "nuevos" / n / f"limpio{sufijo}.png"; p.write_bytes(v); print("guardado", p)
    else:
        trabajos = {n: ((AQUI / "nuevos" / n / "limpio_ok.png").read_bytes(), FLYERS[n]["mover"], FLYERS[n]["ultimo"]) for n in nombres}
        for n, v in animar.remote(trabajos, semilla).items():
            p = AQUI / "nuevos" / n / f"clip{sufijo}.mp4"; p.write_bytes(v); print("guardado", p)
