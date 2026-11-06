"""Blanca v3: su foto de escritorio SIN la mano en la barbilla (Qwen-Image-Edit) y hablando con las manos (H3 con su voz clonada como guía de labios).
Una sola GPU: Qwen primero, se libera memoria y arranca ComfyUI. Uso: modal run blanca_v3_modal.py"""
import io, json, pathlib, sys
import modal
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/XV")
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/Mariano/flyers_animados")
from flyers_modal import imagen, datos, qwen
from xv_modal import _flujo, _largo, ANCHO, ALTO, CARPETA

app = modal.App("blanca-habla-v3", image=imagen.add_local_python_source("flyers_modal", "xv_modal"))
AQUI = pathlib.Path(__file__).resolve().parent
Q_MANOS = ("Conserva EXACTAMENTE a esta mujer y toda la escena: la misma cara, ojos, cabello castaño largo con luces, saco negro, blusa blanca, el muro de bloques de colores, "
           "la laptop, la taza y la libreta. Solo cambia su pose: quita la mano de la barbilla; ahora tiene ambas manos sobre el escritorio frente a ella, relajadas, "
           "con las palmas ligeramente abiertas como cuando explica algo, y una expresión cálida y amable. Foto vertical 9:16, realista, nítida, sin texto nuevo.")
FIN = (" She explains with natural, expressive hand gestures, both hands moving gently above the desk, her hands never touch her chin. Natural lip movement matching the speech, "
       "small head movements and a warm, confident expression. Keep her face, long brown hair with highlights, black blazer, white blouse and the colorful block wall exactly as in the first frame. "
       "Realistic, soft natural light. No text. Audio: clear female voice speaking Spanish.")
TOMAS = [("B1_gancho", "bl_A2", 8.05, "Vertical medium shot of a professional speech therapist seated at her desk in front of a colorful toy-block wall, speaking to the camera, caring and attentive." + FIN),
         ("B2_cierre", "bl_C2", 3.92, "Vertical medium shot of a professional speech therapist seated at her desk in front of a colorful toy-block wall, inviting the viewer with an open-hand gesture and a soft smile." + FIN)]


@app.function(gpu="A100-80GB", volumes={"/datos": datos, "/qwen": qwen}, timeout=7200)
def todo(foto: bytes, voces: dict, semilla: int = 2) -> dict:
    import gc, glob, os, subprocess, time, requests, torch
    from PIL import Image
    from diffusers import QwenImageEditPlusPipeline
    carpeta = f"/datos/siena/{CARPETA}"
    os.makedirs(carpeta, exist_ok=True)
    for n, v in voces.items():
        open(f"{carpeta}/{n}.wav", "wb").write(v)
    pipe = QwenImageEditPlusPipeline.from_pretrained("/qwen/Qwen-Image-Edit-2511", torch_dtype=torch.bfloat16).to("cuda")
    im = pipe(image=[Image.open(io.BytesIO(foto)).convert("RGB")], prompt=Q_MANOS, negative_prompt="mano en la barbilla, cara distinta, manos deformes, dedos extra, borroso",
              true_cfg_scale=4.0, guidance_scale=1.0, num_inference_steps=40, height=1280, width=720, generator=torch.Generator("cuda").manual_seed(semilla)).images[0]
    del pipe; gc.collect(); torch.cuda.empty_cache()
    im.resize((ANCHO, ALTO), Image.LANCZOS).save(f"{carpeta}/blanca_manos.png")
    salida = {}
    b = io.BytesIO(); im.save(b, "PNG"); salida["blanca_manos.png"] = b.getvalue(); print("cuadro manos", flush=True)
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
    for n, voz, seg, prompt in TOMAS:
        r = requests.post("http://127.0.0.1:8188/prompt", json={"prompt": _flujo("blanca_manos", None, voz, prompt, n, semilla, _largo(seg))}).json()
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
def main(semilla: int = 2):
    voces = {k: (AQUI / "voz" / f"{k}.wav").read_bytes() for k in ("bl_A2", "bl_C2")}
    out = AQUI / "tomas_v3"; out.mkdir(exist_ok=True)
    for n, v in todo.remote((AQUI.parent / "whatsapp" / "del_cliente" / "foto_nueva_240009_1.jpg").read_bytes(), voces, semilla).items():
        (out / n).write_bytes(v); print("guardado", n)
