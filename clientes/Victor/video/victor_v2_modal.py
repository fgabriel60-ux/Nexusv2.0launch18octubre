"""Servilin (Víctor) v2: escenas NUEVAS de trabajo con SUS trabajadores reales (mismo uniforme azul con franjas naranjas, chaleco amarillo y guantes rojos del video de su equipo).
Qwen-Image-Edit crea cada escena tomando los cuadros reales como referencia; H3 la anima. Una sola GPU: Qwen primero, se libera memoria y arranca ComfyUI.
Uso: modal run victor_v2_modal.py"""
import io, json, pathlib, sys
import modal
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/XV")
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/Mariano/flyers_animados")
from flyers_modal import imagen, datos, qwen
from xv_modal import _flujo, ANCHO, ALTO, CARPETA

app = modal.App("victor-servilin-v2", image=imagen.add_local_python_source("flyers_modal", "xv_modal"))
AQUI = pathlib.Path(__file__).resolve().parent
UNIFORME = ("Usa EXACTAMENTE el uniforme de los trabajadores de las imágenes de referencia: camisa y pantalón azul rey con franjas naranjas, chaleco amarillo fluorescente reflejante, "
            "guantes rojos y zapatos negros, y personas mexicanas reales como las de la referencia. ")
FINAL_Q = "Foto vertical 9:16, realista, documental, nítida, luz natural, sin texto, sin letras, sin logotipos."
ESCENAS = {
    "S1_trapeo": UNIFORME + "Una trabajadora trapea con un trapeador profesional el piso amplio y brillante de una planta industrial limpia y ordenada, con carrito de limpieza amarillo. " + FINAL_Q,
    "S2_ventanas": UNIFORME + "Dos trabajadores limpian con jalador los ventanales de una oficina corporativa moderna, el vidrio queda reluciente. " + FINAL_Q,
    "S3_maquina": UNIFORME + "Un trabajador opera una máquina lavadora de pisos industrial en una nave de producción amplia y luminosa, el piso húmedo brilla. " + FINAL_Q,
    "S4_supervision": UNIFORME + "Un supervisor con tableta revisa un baño de planta impecable junto a una trabajadora que muestra el área limpia, ambos sonríen con seguridad. " + FINAL_Q,
}
FIN = " Keep the people, the blue uniforms with orange stripes, yellow reflective vests and red gloves exactly as in the first frame. Realistic documentary look, natural light, handheld feel. No text. Audio: soft ambient, no speech."
MOVER = {
    "S1_trapeo": "Vertical shot: the cleaning worker mops the shiny industrial floor with steady strokes, slow gentle push-in." + FIN,
    "S2_ventanas": "Vertical shot: the two workers wipe the large office windows with squeegees, the glass becomes spotless, slow lateral camera move." + FIN,
    "S3_maquina": "Vertical shot: the worker drives the floor scrubber forward across the factory floor leaving a clean shiny trail, slow tracking shot." + FIN,
    "S4_supervision": "Vertical shot: the supervisor checks the tablet and nods approvingly while the worker points at the clean area, slow push-in." + FIN,
}


@app.function(gpu="A100-80GB", volumes={"/datos": datos, "/qwen": qwen}, timeout=7200)
def todo(refs: list, semilla: int = 4) -> dict:
    import gc, glob, os, subprocess, time, requests, torch
    from PIL import Image
    from diffusers import QwenImageEditPlusPipeline
    carpeta = f"/datos/siena/{CARPETA}"
    os.makedirs(carpeta, exist_ok=True)
    pipe = QwenImageEditPlusPipeline.from_pretrained("/qwen/Qwen-Image-Edit-2511", torch_dtype=torch.bfloat16).to("cuda")
    imgs = [Image.open(io.BytesIO(r)).convert("RGB") for r in refs]
    salida = {}
    for n, p in ESCENAS.items():
        im = pipe(image=imgs, prompt=p, negative_prompt="texto, letras, logotipo, uniforme distinto, deforme, borroso, manos extra",
                  true_cfg_scale=4.0, guidance_scale=1.0, num_inference_steps=40, height=1280, width=720,
                  generator=torch.Generator("cuda").manual_seed(semilla)).images[0]
        im.resize((ANCHO, ALTO), Image.LANCZOS).save(f"{carpeta}/{n}.png")
        b = io.BytesIO(); im.save(b, "PNG"); salida[f"{n}.png"] = b.getvalue(); print("escena", n, flush=True)
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
    for n in ESCENAS:
        r = requests.post("http://127.0.0.1:8188/prompt", json={"prompt": _flujo(n, None, None, MOVER[n], n, semilla, 124)}).json()
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
def main(semilla: int = 4):
    refs = [(AQUI / "cuadros" / f"{c}.jpg").read_bytes() for c in ("f_8", "f_15")]
    out = AQUI / "v2"; out.mkdir(exist_ok=True)
    for n, v in todo.remote(refs, semilla).items():
        (out / n).write_bytes(v); print("guardado", n)
