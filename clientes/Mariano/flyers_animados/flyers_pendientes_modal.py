"""Mariano · flyer de Benjamina sin texto y animado: Qwen-Image-Edit borra TODO el texto (las 4 fotos se quedan igual),
luego H3 anima ese cuadro limpio con primer y último cuadro iguales (la composición regresa a su lugar). El texto original se vuelve a poner nítido en armar.
Una sola GPU: Qwen primero, se libera la memoria y arranca ComfyUI. Uso: modal run flyer_sin_texto_modal.py"""
import io, json, pathlib
import modal
from flyers_modal import imagen, datos, qwen, ANCHO, ALTO, CARPETA

app = modal.App("mariano-flyers-pendientes", image=imagen.add_local_python_source("flyers_modal"))
AQUI = pathlib.Path(__file__).resolve().parent
LIMPIAR = ("Elimina TODO el texto y los gráficos del flyer: los globos de chat con sus frases, el logotipo Grupo Lagsa, el logotipo Vizcaíno Residencial, "
           "la barra de mensaje con íconos, el nombre del modelo, el precio, la ubicación, las etiquetas y las letras pequeñas. "
           "Reconstruye detrás de ellos el cielo azul con nubes, la casa, los árboles, el pasto y el camino de forma natural. "
           "Conserva EXACTAMENTE a la pareja abrazada, la casa, su composición, colores y luz. No agregues nada.")
MOVER = ("Dynamic cinematic real-estate lifestyle shot: a clearly visible smooth camera push-in toward the couple combined with a slow arc to the right, the couple holds the hug and sways gently, "
         "her long dress and hair flow in a steady breeze, tree leaves and the lavender bushes move, clouds drift across the blue sky, warm lights in the house windows glow brighter. "
         "The faces stay natural and undistorted, the house and the couple keep their shape. No text. Audio: soft breeze ambience, no speech.")


def _flujo(nombre, prompt, semilla, largo):
    return {
        "6": {"class_type": "UNETLoader", "inputs": {"unet_name": "minimax_h3_fl2va_pruned_fp8_scaled.safetensors", "weight_dtype": "default"}},
        "121": {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["6", 0], "lora_name": "minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors", "strength_model": 1.0}},
        "13": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors", "type": "minimax", "device": "default"}},
        "11": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_video_vae_fp16.safetensors"}},
        "24": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_audio_vae_fp32.safetensors"}},
        "30": {"class_type": "LoadImage", "inputs": {"image": f"{CARPETA}/{nombre}.png"}},
        "31": {"class_type": "LoadImage", "inputs": {"image": f"{CARPETA}/{nombre}.png"}},
        "104": {"class_type": "MiniMaxH3ImageToVideo", "inputs": {"clip": ["13", 0], "vae": ["11", 0], "prompt": prompt, "width": ANCHO, "height": ALTO, "length": largo,
                                                                  "first_frame": ["30", 0], "last_frame": ["31", 0]}},
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


@app.function(gpu="A100-80GB", volumes={"/datos": datos, "/qwen": qwen}, timeout=5400)
def todo(flyer: bytes, semilla: int = 5, limpio_listo: bool = False, solo_limpio: bool = False, limpieza: str = LIMPIAR, movimiento: str = MOVER) -> dict:
    import gc, glob, os, subprocess, time, requests, torch
    from PIL import Image
    from diffusers import QwenImageEditPlusPipeline
    carpeta = f"/datos/siena/{CARPETA}"
    os.makedirs(carpeta, exist_ok=True)
    if limpio_listo:
        limpio = Image.open(io.BytesIO(flyer)).convert("RGB")
    else:
      pipe = QwenImageEditPlusPipeline.from_pretrained("/qwen/Qwen-Image-Edit-2511", torch_dtype=torch.bfloat16).to("cuda")
      limpio = pipe(image=[Image.open(io.BytesIO(flyer)).convert("RGB")], prompt=limpieza, negative_prompt="texto, letras, números, logotipo, íconos, botones, deforme, borroso",
                  true_cfg_scale=4.0, guidance_scale=1.0, num_inference_steps=40, height=1280, width=720,
                  generator=torch.Generator("cuda").manual_seed(semilla)).images[0]
      del pipe; gc.collect(); torch.cuda.empty_cache()
    limpio_hd = io.BytesIO(); limpio.save(limpio_hd, "PNG")
    limpio.resize((ANCHO, ALTO), Image.LANCZOS).save(f"{carpeta}/pendiente_limpio.png")
    print("cuadro limpio", flush=True)
    if solo_limpio:
        return {"limpio.png": limpio_hd.getvalue()}
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
    r = requests.post("http://127.0.0.1:8188/prompt", json={"prompt": _flujo("pendiente_limpio", movimiento, semilla, 175)}).json()
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
    archivo = sorted(glob.glob(f"/datos/siena/out/{CARPETA}/pendiente_limpio_*.mp4"), key=os.path.getmtime)[-1]
    datos.commit()
    return {"limpio.png": limpio_hd.getvalue(), "clip.mp4": open(archivo, "rb").read()}


@app.local_entrypoint()
def main(paso: str = "limpio", solo: str = ""):
    from PIL import Image
    configs = {
      "Sotol_familia": ("1018_005111_BA9020.jpg", "Conserva exactamente a la familia de cuatro personas cocinando, rostros, cocina y muebles.", "A family of four cooking together in their kitchen, subtle natural smiles and hand movements, gentle steam above the pot. Very slow camera push in. Keep all four faces and anatomy consistent, preserve the kitchen. No text, no speech."),
      "Bugambilia_mejor_opcion": ("1020_210408_4AF9D8.jpg", "Conserva exactamente la casa blanca de dos pisos, ventanas, camino, arboles y cielo. Mantén la franja superior blanca y la franja inferior gris lisas.", "Real estate photograph with an extremely gentle camera push toward the white two-story house, soft clouds drifting, tree leaves subtly moving, warm windows. Keep house architecture unchanged and keep the upper white area and lower gray band static. No text, no speech.")
    }
    for nombre, (archivo, mantener, mover) in configs.items():
        if solo and nombre != solo: continue
        out = AQUI / 'nuevos' / nombre; out.mkdir(parents=True, exist_ok=True)
        if paso == 'limpio':
            img = Image.open(AQUI.parent / 'flyers_recibidos' / archivo).convert('RGB').resize((720,1280),Image.Resampling.LANCZOS)
            b=io.BytesIO(); img.save(b,'PNG'); data=b.getvalue()
        else: data=(out/'limpio.png').read_bytes()
        limpiar = "Elimina todos los textos, numeros, logos, etiquetas y graficos publicitarios. Reconstruye el fondo detrás. " + mantener
        for n,v in todo.remote(data, 11, paso!='limpio', paso=='limpio', limpiar, mover).items():
            (out/n).write_bytes(v); print('guardado',out/n,flush=True)
