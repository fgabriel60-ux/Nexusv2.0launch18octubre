"""Servilin (Víctor) · limpieza de OBRA FINA v5: escenas SOLO de casas y departamentos nuevos (sin planta, bodega ni montacargas). 4 escenas nuevas con Qwen (misma obrera uniformada de v4) + H3.
Se combinan con O1, O2 y O4 de v4. Uso: python3 gasto_modal.py run clientes/Victor/video/obra_v5/victor_obra_modal.py"""
import io, json, pathlib, sys
import modal
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/XV")
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/Mariano/flyers_animados")
from flyers_modal import imagen, datos, qwen
from xv_modal import _flujo, _largo, ANCHO, ALTO, CARPETA

app = modal.App("victor-obra-v5", image=imagen.add_local_python_source("flyers_modal", "xv_modal"))
AQUI = pathlib.Path(__file__).resolve().parent
FOTO = "Fotografía realista y nítida, vertical 9:16, luz natural de día, sin texto, sin letras, sin logotipos. "
OBR = ("La MISMA trabajadora de limpieza de la imagen (misma cara, cabello recogido, chaleco amarillo reflejante sobre uniforme azul con franjas naranjas, guantes rojos). ")
SOLO = " Es una vivienda residencial nueva: NO hay maquinaria, montacargas, lavadoras industriales, bodegas ni plantas."
QWEN = {
    "H3_cocina": (["obrera"], FOTO + OBR + "Limpia con un paño la barra de granito blanco de una cocina residencial nueva y moderna, con estufa y gabinetes de madera, quitando restos de polvo de obra. Plano medio." + SOLO),
    "H4_bano": (["obrera"], FOTO + OBR + "Limpia con una espátula y un trapo el azulejo y el lavabo de un baño residencial recién remodelado, regadera de cristal al fondo. Plano medio." + SOLO),
    "H5_recamara": (["obrera"], FOTO + OBR + "Pasa una aspiradora por el piso de madera clara de una recámara amplia y luminosa de una casa nueva, ventana grande con cortinas blancas. Plano medio." + SOLO),
    "H6_entrega": (["obrera"], FOTO + OBR + "Está de pie con una sonrisa y el pulgar arriba en la sala impecable de una casa nueva lista para entregar: piso brillante, sofá nuevo, ventanales y jardín al fondo. Plano medio." + SOLO),
}
H3 = [
    ("H3_cocina", "H3_cocina", 4.0, "Vertical realistic shot: the worker wipes the white granite kitchen counter with a cloth, leaving it spotless, smooth slow push-in. Keep the same person and kitchen. No text. Audio: soft ambient, no speech."),
    ("H4_bano", "H4_bano", 4.0, "Vertical realistic shot: the worker cleans the bathroom tile and sink with a cloth, careful natural movement, slow push-in. Keep the same person and bathroom. No text. Audio: soft ambient, no speech."),
    ("H5_recamara", "H5_recamara", 4.0, "Vertical realistic shot: the worker vacuums the light wood floor of the bedroom, smooth slow dolly. Keep the same person and room. No text. Audio: soft vacuum ambience, no speech."),
    ("H6_entrega", "H6_entrega", 4.0, "Vertical realistic shot: the worker smiles to the camera with a thumbs up in the spotless living room, slow push-in. Keep the same person and room. No text. Audio: soft ambient, no speech."),
]


@app.function(gpu="A100-80GB", volumes={"/datos": datos, "/qwen": qwen}, timeout=7200)
def todo(refs: dict, semilla: int = 8) -> dict:
    import gc, glob, os, subprocess, time, requests, torch
    from PIL import Image
    from diffusers import QwenImageEditPlusPipeline
    carpeta = f"/datos/siena/{CARPETA}"
    os.makedirs(carpeta, exist_ok=True)
    imgs = {k: Image.open(io.BytesIO(v)).convert("RGB") for k, v in refs.items()}
    pipe = QwenImageEditPlusPipeline.from_pretrained("/qwen/Qwen-Image-Edit-2511", torch_dtype=torch.bfloat16).to("cuda")
    salida = {}
    for n, (usar, p) in QWEN.items():
        im = pipe(image=[imgs[u] for u in usar], prompt=p, negative_prompt="texto, letras, logotipo, montacargas, maquinaria, lavadora industrial, bodega, cara distinta, deforme, borroso, manos extra",
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
    for n, ini, seg, prompt in H3:
        r = requests.post("http://127.0.0.1:8188/prompt", json={"prompt": _flujo(ini, None, None, prompt, n, semilla, _largo(seg))}).json()
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
def main(semilla: int = 8):
    refs = {"obrera": (AQUI / "ref_obrera.png").read_bytes()}
    out = AQUI / "salida"; out.mkdir(exist_ok=True)
    for n, v in todo.remote(refs, semilla).items():
        (out / n).write_bytes(v); print("guardado", n)
