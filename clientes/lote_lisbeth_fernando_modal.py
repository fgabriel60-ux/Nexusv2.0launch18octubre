"""Lote en UNA sola GPU: (1) Lisbeth v2: selfie con su terreno atrás diciendo el gancho → lanza el celular y la cámara sube rápida y fluida hasta el
primer cuadro aéreo de su v22 (sin corte); (2) Fernando: 5 escenas de capacitación en una tiendita con SU cara. Qwen primero, luego H3.
Uso: modal run lote_lisbeth_fernando_modal.py"""
import io, json, pathlib, sys
import modal
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/XV")
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/Mariano/flyers_animados")
from flyers_modal import imagen, datos, qwen
from xv_modal import _flujo, _largo, ANCHO, ALTO, CARPETA

app = modal.App("lote-lisbeth-fernando", image=imagen.add_local_python_source("flyers_modal", "xv_modal"))
AQUI = pathlib.Path(__file__).resolve().parent
SIN = " Foto vertical 9:16, realista, nítida, sin texto, sin letras."
CARA = "Conserva EXACTAMENTE la cara de esta persona: mismos ojos, cejas, nariz, boca, edad, tono de piel y cabello. "
QWEN = {  # nombre: (referencias, prompt)
    "LIS_selfie": (["lisbeth"], CARA + "Es una selfie: ella sostiene el celular con el brazo extendido hacia la cámara (se ve su brazo saliendo del borde inferior), de pie en un terreno de lomas secas con matorral y árboles, cielo azul con nubes, luz cálida de tarde. Blusa negra, cabello oscuro recogido, sonrisa segura." + SIN),
    "LIS_aereo": (["v22"], "Quita TODO el texto, letras y subtítulos de la imagen. Deja exactamente la misma vista aérea del terreno con la cuadrícula de lotes, el camino y la vegetación." + SIN),
    "FER_1": (["fernando"], CARA + "Él llega con una caja de cartón de un kit de punto de venta a una tiendita de abarrotes en la Ciudad de México y saluda de mano al dueño junto al mostrador, donde hay una computadora de escritorio. Camisa polo clara." + SIN),
    "FER_2": (["fernando"], CARA + "Él conecta una pequeña impresora térmica de tickets a la computadora del mostrador de una tiendita de abarrotes en la Ciudad de México. Camisa polo clara." + SIN),
    "FER_3": (["fernando"], CARA + "Él escanea un producto con un lector de código de barras en el mostrador de una tiendita; en el monitor de la computadora se ve un programa de punto de venta. Camisa polo clara." + SIN),
    "FER_4": (["fernando"], CARA + "Él hace una venta de prueba y de la impresora térmica sale un ticket, junto a la computadora del mostrador de una tiendita de abarrotes. Camisa polo clara." + SIN),
    "FER_5": (["fernando"], CARA + "Él capacita a la dueña de la tiendita frente a la computadora del mostrador; ella usa el lector de código y ambos sonríen. Camisa polo clara." + SIN),
}
H3 = [  # (toma, primer cuadro, último cuadro, voz, segundos, prompt)
    ("LIS_habla", "LIS_selfie", None, "L_gancho", 4.52, "Vertical selfie video: the woman holds the phone at arm's length in a dry hillside field and speaks to the camera with natural lip movement matching the speech, warm confident smile, slight handheld shake. Keep her face exactly. No text. Audio: clear female voice speaking Spanish."),
    ("LIS_sube", "LIS_selfie", "LIS_aereo", None, 3.0, "Continuous single shot, no cut: the woman tosses the phone camera straight up into the air, the camera view rises very fast and smoothly with slight spin and motion blur, higher and higher above the hills until it settles into a stable top-down drone view of the land plots. Fast-motion rise. No text. Audio: whoosh of wind, no speech."),
    ("FER_1", "FER_1", None, None, 3.4, "Vertical shot: he arrives at the small grocery store counter carrying the boxed point-of-sale kit and shakes hands with the owner, friendly. Slow push-in. Keep his face exactly. No text. Audio: soft store ambience, no speech."),
    ("FER_2", "FER_2", None, None, 3.4, "Vertical shot: he plugs the thermal receipt printer cable into the store's desktop computer, focused hands. Slow push-in. Keep his face exactly. No text. Audio: soft ambience, no speech."),
    ("FER_3", "FER_3", None, None, 3.4, "Vertical shot: he scans a product with the barcode scanner, a red light flashes and the price appears on the monitor. Slow push-in. Keep his face exactly. No text. Audio: a beep of the scanner, no speech."),
    ("FER_4", "FER_4", None, None, 3.4, "Vertical shot: a paper receipt prints out of the thermal printer and he tears it off and shows it with a smile. Slow push-in. Keep his face exactly. No text. Audio: printer sound, no speech."),
    ("FER_5", "FER_5", None, None, 3.4, "Vertical shot: the store owner scans a product herself while he points at the screen and nods, both smile. Slow push-in. Keep his face exactly. No text. Audio: soft store ambience, no speech."),
]


@app.function(gpu="A100-80GB", volumes={"/datos": datos, "/qwen": qwen}, timeout=7200)
def todo(refs: dict, voces: dict, semilla: int = 3) -> dict:
    import gc, glob, os, subprocess, time, requests, torch
    from PIL import Image
    from diffusers import QwenImageEditPlusPipeline
    carpeta = f"/datos/siena/{CARPETA}"
    os.makedirs(carpeta, exist_ok=True)
    for n, v in voces.items():
        open(f"{carpeta}/{n}.wav", "wb").write(v)
    imgs = {k: Image.open(io.BytesIO(v)).convert("RGB") for k, v in refs.items()}
    pipe = QwenImageEditPlusPipeline.from_pretrained("/qwen/Qwen-Image-Edit-2511", torch_dtype=torch.bfloat16).to("cuda")
    salida = {}
    for n, (usar, p) in QWEN.items():
        im = pipe(image=[imgs[u] for u in usar], prompt=p, negative_prompt="texto, letras, subtítulos, cara distinta, deforme, borroso, manos extra, dedos extra",
                  true_cfg_scale=4.0, guidance_scale=1.0, num_inference_steps=40, height=1280, width=720, generator=torch.Generator("cuda").manual_seed(semilla)).images[0]
        im.resize((ANCHO, ALTO), Image.LANCZOS).save(f"{carpeta}/{n}.png")
        b = io.BytesIO(); im.save(b, "PNG"); salida[f"{n}.png"] = b.getvalue(); print("cuadro", n, flush=True)
    del pipe; gc.collect(); torch.cuda.empty_cache()
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
    for n, ini, fin, voz, seg, prompt in H3:
        r = requests.post("http://127.0.0.1:8188/prompt", json={"prompt": _flujo(ini, fin, voz, prompt, n, semilla, _largo(seg))}).json()
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
        salida[f"{n}.mp4"] = open(archivo, "rb").read(); print("listo", n, flush=True)
    datos.commit()
    return salida


@app.local_entrypoint()
def main(semilla: int = 3):
    refs = {"lisbeth": (AQUI / "Lisbeth/whatsapp/del_cliente/20261022_161302_image.jpg").read_bytes(),
            "v22": (AQUI / "Lisbeth/referencia/v22_primer_cuadro.png").read_bytes(),
            "fernando": (AQUI / "Fernando/whatsapp/del_cliente/foto_1023_015446.jpg").read_bytes()}
    voces = {"L_gancho": (AQUI / "Lisbeth/video/voz/L_gancho.wav").read_bytes()}
    for n, v in todo.remote(refs, voces, semilla).items():
        destino = AQUI / ("Lisbeth/video/v2" if n.startswith("LIS") else "Fernando/video/tomas"); destino.mkdir(parents=True, exist_ok=True)
        (destino / n).write_bytes(v); print("guardado", n)
