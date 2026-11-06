"""Fernando / Anegocios · MOSTRADOR: cadena de ediciones Qwen-Image-Edit-2511 (escena de miscelánea donde el equipo REAL aparece pieza por pieza)
+ clips MiniMax H3 de ~5 s sin voz.   modal run mostrador_modal.py::main --paso escena | --paso clips
"""
import io, json, math, pathlib
import modal

CARPETA = "anegocios_mostrador"
imagen = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("git", "ffmpeg")
    .run_commands("git clone --depth 1 https://github.com/comfyanonymous/ComfyUI /opt/ComfyUI")
    .pip_install("torch", "torchvision", "torchaudio")
    .run_commands("pip install -r /opt/ComfyUI/requirements.txt")
    .pip_install("git+https://github.com/huggingface/diffusers", "transformers", "accelerate", "pillow", "requests")
)
app = modal.App("anegocios-mostrador", image=imagen)
datos = modal.Volume.from_name("h3-comprimido-gastro")
qwen = modal.Volume.from_name("qwen-image-edit-2511")
NEG = "texto legible inventado, letras deformes, logotipo ajeno, deforme, borroso, objetos flotando, duplicado, caricatura, ilustración"
COMUN = " Fotografía vertical realista de una miscelánea mexicana, luz cálida natural, sombras de contacto reales sobre la madera, sin texto añadido."
PASOS = {
    "S0": (["base"], "Conserva la misma composición, pero SIN ningún banner, etiqueta azul ni texto: el techo con luces desenfocadas es continuo. Mostrador de madera en primer plano al frente y anaqueles de tienda desenfocados al fondo. Quita por completo la gaveta de dinero, el teclado y cualquier logotipo: el mostrador de madera queda totalmente vacío. Cambia los productos de los anaqueles por abarrotes mexicanos (refrescos, botanas, latas, bolsas de pan dulce), muy desenfocados." + COMUN),
    "S1": (["prev", "laptop"], "Coloca sobre el mostrador de la imagen 1, al centro del encuadre, completamente dentro de la imagen, la laptop plateada de la imagen 2 abierta, vista de frente, con la pantalla mostrando el punto de venta Anegocios con su logo azul en la esquina superior; conserva su diseño. No cambies nada más de la imagen 1." + COMUN),
    "S2": (["prev", "lector"], "Agrega sobre el mostrador de la imagen 1, a la izquierda de la laptop, a un palmo de ella y completamente dentro del encuadre, el lector de códigos de barras negro con base flexible de la imagen 2, conservando exactamente su diseño. No cambies nada más." + COMUN),
    "S3": (["prev", "impresora"], "Agrega sobre el mostrador de la imagen 1, a la derecha de la laptop, a un palmo de ella y completamente dentro del encuadre (sin tocar el borde de la imagen), la impresora térmica negra de la imagen 2 con un ticket blanco saliendo por arriba, conservando su diseño. No cambies nada más." + COMUN),
    "S4": (["prev", "caja", "rollos"], "Agrega sobre el mostrador de la imagen 1: la caja blanca y azul del software Anegocios de la imagen 2 (conserva su logo y su diseño) de pie en primer plano a la izquierda del lector, y los rollos de papel térmico blancos apilados de la imagen 3 en primer plano a la derecha de la impresora; todo completamente dentro del encuadre, sin tocar los bordes. No cambies nada más." + COMUN),
}
CLIPS = {
    "K1": ("S3", "Vertical social media reel, real footage. Slow smooth camera push-in toward the shop counter with the silver laptop showing the Anegocios blue logo screen, the black barcode scanner and the black thermal printer, shelves softly blurred behind, warm light, subtle floating dust particles in the sunlight. No people, no text, the products keep exactly the same design and position."),
    "K2": ("S2", "Vertical social media reel, real footage. A hand places a small grocery product (a snack bag) under the black barcode scanner on the wooden counter, the scanner emits a red light flash as it scans, then the hand pulls the product away. Natural motion, five fingers, static camera, the laptop and scanner keep their exact design, no text."),
    "K3": ("S3", "Vertical social media reel, real footage. The black thermal printer on the right side of the counter prints a white receipt that slowly comes out upward, a hand tears it off. Natural motion, five fingers, static camera, the laptop and scanner stay unchanged, no text."),
    "K4": ("S1", "Vertical social media reel, real footage. Close view of the laptop on the wooden counter with the Anegocios point of sale screen; a hand touches the keyboard and the sale list on the screen updates with new lines being added. Subtle natural motion, static camera, the Anegocios blue logo stays sharp and unchanged, no extra text."),
}


@app.function(gpu="A100-80GB", volumes={"/datos": datos, "/qwen": qwen}, timeout=3600)
def escena(refs: dict, desde: str = "S0", hasta: str = "S4", semillas: dict = None, previo: bytes = b""):
    import os, torch
    from PIL import Image
    from diffusers import QwenImageEditPlusPipeline
    pipe = QwenImageEditPlusPipeline.from_pretrained("/qwen/Qwen-Image-Edit-2511", torch_dtype=torch.bfloat16).to("cuda")
    carpeta = f"/datos/siena/{CARPETA}"; os.makedirs(carpeta, exist_ok=True)
    img = lambda b: Image.open(io.BytesIO(b)).convert("RGB")
    prev = img(previo) if previo else None
    salida = {}; activo = False
    for n, (usar, prompt) in PASOS.items():
        if n == desde: activo = True
        if not activo: continue
        sem = (semillas or {}).get(n, (11,))
        entradas = [prev if u == "prev" else img(refs[u]) for u in usar]
        cand = []
        for s in sem:
            r = pipe(image=entradas, prompt=prompt, negative_prompt=NEG, true_cfg_scale=4.0, guidance_scale=1.0, num_inference_steps=40,
                     height=1280, width=720, generator=torch.Generator("cuda").manual_seed(s)).images[0].convert("RGB")
            b = io.BytesIO(); r.save(b, "PNG"); salida[f"{n}_{s}"] = b.getvalue(); cand.append(r); print("cuadro", n, s, flush=True)
        prev = cand[0]
        prev.save(f"{carpeta}/{n}.png")
        if n == hasta: break
    datos.commit()
    return salida


def _flujo(n, entrada, prompt, semilla, largo):
    return {
        "6": {"class_type": "UNETLoader", "inputs": {"unet_name": "minimax_h3_fl2va_pruned_fp8_scaled.safetensors", "weight_dtype": "default"}},
        "121": {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["6", 0], "lora_name": "minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors", "strength_model": 1.0}},
        "13": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors", "type": "minimax", "device": "default"}},
        "11": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_video_vae_fp16.safetensors"}},
        "24": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_audio_vae_fp32.safetensors"}},
        "30": {"class_type": "LoadImage", "inputs": {"image": f"{CARPETA}/{entrada}.png"}},
        "104": {"class_type": "MiniMaxH3ImageToVideo", "inputs": {"clip": ["13", 0], "vae": ["11", 0], "prompt": prompt, "width": 576, "height": 1024, "length": largo, "first_frame": ["30", 0]}},
        "15": {"class_type": "RandomNoise", "inputs": {"noise_seed": semilla}},
        "17": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "res_multistep"}},
        "9": {"class_type": "BasicScheduler", "inputs": {"model": ["121", 0], "scheduler": "simple", "steps": 8, "denoise": 1.0}},
        "16": {"class_type": "BasicGuider", "inputs": {"model": ["121", 0], "conditioning": ["104", 0]}},
        "14": {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["15", 0], "guider": ["16", 0], "sampler": ["17", 0], "sigmas": ["9", 0], "latent_image": ["104", 1]}},
        "10": {"class_type": "VAEDecode", "inputs": {"samples": ["14", 0], "vae": ["11", 0]}},
        "23": {"class_type": "VAEDecodeAudio", "inputs": {"samples": ["14", 0], "vae": ["24", 0]}},
        "91": {"class_type": "CreateVideo", "inputs": {"images": ["10", 0], "audio": ["23", 0], "fps": 24}},
        "92": {"class_type": "SaveVideo", "inputs": {"video": ["91", 0], "filename_prefix": f"{CARPETA}/{n}", "format": "auto", "codec": "auto"}},
    }


@app.function(gpu="A100-80GB", volumes={"/datos": datos}, timeout=5400)
def clips(cuadros: dict, solo: str = "", semilla: int = 2):
    import glob, os, subprocess, time, requests
    from PIL import Image
    carpeta = f"/datos/siena/{CARPETA}"; os.makedirs(carpeta, exist_ok=True); os.makedirs("/datos/siena/logs", exist_ok=True)
    for n, b in cuadros.items():
        Image.open(io.BytesIO(b)).convert("RGB").resize((576, 1024), Image.LANCZOS).save(f"{carpeta}/{n}.png")
    open("/opt/ComfyUI/extra_model_paths.yaml", "w").write(
        "datos:\n  base_path: /datos/models\n  diffusion_models: diffusion_models\n  loras: loras\n  text_encoders: text_encoders\n  vae: vae\n")
    log = open(f"/datos/siena/logs/comfy_{int(time.time())}.log", "w")
    subprocess.Popen(["python", "main.py", "--listen", "127.0.0.1", "--port", "8188", "--input-directory", "/datos/siena",
                      "--output-directory", "/datos/siena/out"], cwd="/opt/ComfyUI", stdout=log, stderr=subprocess.STDOUT)
    for _ in range(300):
        try: requests.get("http://127.0.0.1:8188/system_stats", timeout=2); break
        except Exception: time.sleep(2)
    salida = {}
    for n, (entrada, prompt) in CLIPS.items():
        if solo and n not in solo.split(","): continue
        r = requests.post("http://127.0.0.1:8188/prompt", json={"prompt": _flujo(n, entrada, prompt, semilla, 121)}).json()
        if "prompt_id" not in r: raise RuntimeError(json.dumps(r)[:3000])
        pid = r["prompt_id"]
        while True:
            h = requests.get(f"http://127.0.0.1:8188/history/{pid}").json()
            if pid in h:
                st = h[pid].get("status", {})
                if st.get("status_str") == "error": raise RuntimeError(json.dumps(st)[:3000])
                break
            time.sleep(5)
        f = sorted(glob.glob(f"/datos/siena/out/{CARPETA}/{n}_*.mp4"), key=os.path.getmtime)[-1]
        salida[n] = open(f, "rb").read(); print("clip", n, flush=True)
    datos.commit()
    return salida


@app.local_entrypoint()
def main(paso: str = "escena", desde: str = "S0", hasta: str = "S4", previo: str = "", solo: str = "", semilla: int = 2):
    aqui = pathlib.Path(__file__).resolve().parent; R = aqui / "refs_mostrador"
    if paso == "escena":
        refs = {"base": (R / "reel_base_limpio.jpg").read_bytes(), "laptop": (R / "video_laptop_s.jpg").read_bytes(), "lector": (R / "lector.png").read_bytes(),
                "impresora": (R / "impresora.png").read_bytes(), "caja": (R / "caja.png").read_bytes(), "rollos": (R / "rollos.png").read_bytes()}
        res = escena.remote(refs, desde, hasta, {"S0": (11, 12), "S4": (11, 12)}, pathlib.Path(previo).read_bytes() if previo else b"")
        d = aqui / "mostrador_cuadros"
    else:
        cu = {n: (aqui / "mostrador_cuadros_v2" / f"{n}.png").read_bytes() for n in ("S1", "S2", "S3")}
        res = clips.remote(cu, solo, semilla); d = aqui / ("mostrador_clips" + (f"_s{semilla}" if semilla != 2 else ""))
    d.mkdir(exist_ok=True)
    for k, v in res.items():
        (d / f"{k}.{'png' if paso == 'escena' else 'mp4'}").write_bytes(v); print("guardado", d / k)
