"""Guillermo · techo de placa teja sobre las 2 columnas de la señora: imagen final + video del proceso (columnas → travesaños → techo). Una sola GPU.
Audio de Guillermo (29 oct): de la barda hacia las columnas van 6 travesaños (incluido columna a columna) y hacia el fondo 3; referencia = techo de placa teja roja sobre estructura negra.
Para otra foto: cambiar SITIO/--sitio. Uso: python3 gasto_modal.py run clientes/Guillermo/techo_20261029/techo_modal.py [--sitio otra.jpg]"""
import io, json, pathlib, sys
import modal
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/XV")
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/Mariano/flyers_animados")
from flyers_modal import imagen, datos, qwen
from xv_modal import _flujo, _largo, ANCHO, ALTO, CARPETA

app = modal.App("guillermo-techo-v3", image=imagen.add_local_python_source("flyers_modal", "xv_modal"))
AQUI = pathlib.Path(__file__).resolve().parent
SIN = " Foto vertical 9:16, realista, nítida, luz de día, sin texto, sin letras, sin personas, sin logotipos."
MISMO = ("Misma cámara y MISMO encuadre que la primera foto: las dos columnas de concreto con varillas en el MISMO lugar y del MISMO tamaño, la barda de block al fondo, el cielo azul y el piso. "
         "El techo queda ENTRE la línea de las dos columnas y la barda del fondo. ")
ESTR = ("Estructura de acero NEGRO: una viga de columna a columna al frente (apoyada en las dos columnas), 6 travesaños (vigas) paralelos y parejos que van desde esa viga HACIA LA BARDA del fondo "
        "(alejándose de la cámara, perpendiculares a la barda, no hacia la cámara), y 3 vigas transversales a lo ancho hacia el fondo. TECHO DE UNA SOLA CAÍDA (una sola agua, NO a dos aguas, sin cumbrera ni caballete): el lado pegado a la barda queda más ALTO y el techo baja en una sola pendiente suave hacia el borde de las columnas, que queda más BAJO. ")
QWEN = {
    "T2_techo": (["T1_estructura", "ref"], "La primera foto muestra una estructura de acero NEGRO sobre dos columnas de concreto. NO cambies NADA: misma cámara, mismas columnas, misma barda, mismo cielo, mismo piso y EXACTAMENTE la misma estructura de vigas. Solo agrega ENCIMA de la estructura láminas de placa teja ondulada color ROJO TEJA, como la de la segunda foto, en UN SOLO plano inclinado de UNA SOLA CAÍDA (más alto del lado de la barda, bajando hacia las columnas, nunca dos aguas), cubriendo toda la estructura. Los perfiles NO sobresalen por el frente: sus extremos quedan al ras de las columnas y del borde de las láminas, sin vigas sueltas apuntando hacia afuera." + SIN),
}
H3 = [
    ("T_lamina", "T1_estructura", "T2_techo", 5.0, "Vertical time-lapse shot, camera static: corrugated red roof panels are laid one by one over the existing black steel structure until the roof is complete as ONE single-slope plane (high at the wall, lower at the column edge, not a gable), the steel structure does not change and no beams stick out at the front, smooth realistic construction, no people. Keep the same place exactly. No text. Audio: soft construction ambience, no speech."),
]


@app.function(gpu="A100-80GB", volumes={"/datos": datos, "/qwen": qwen}, timeout=7200)
def todo(refs: dict, semilla: int = 3) -> dict:
    import gc, glob, os, subprocess, time, requests, torch
    from PIL import Image
    from diffusers import QwenImageEditPlusPipeline
    carpeta = f"/datos/siena/{CARPETA}"
    os.makedirs(carpeta, exist_ok=True)
    imgs = {k: Image.open(io.BytesIO(v)).convert("RGB") for k, v in refs.items()}
    imgs["T1_estructura"].resize((ANCHO, ALTO)).save(f"{carpeta}/T1_estructura.png")
    pipe = QwenImageEditPlusPipeline.from_pretrained("/qwen/Qwen-Image-Edit-2511", torch_dtype=torch.bfloat16).to("cuda")
    salida = {}
    for n, (usar, p) in QWEN.items():
        im = pipe(image=[imgs[u] for u in usar], prompt=p, negative_prompt="techo a dos aguas, cumbrera, caballete, techo en forma de A, vigas hacia la cámara, vigas apuntando al frente, zoom, acercamiento, texto, letras, logotipo, personas, columnas distintas, otra barda, deforme, borroso, láminas planas, techo inclinado extremo",
                  true_cfg_scale=4.0, guidance_scale=1.0, num_inference_steps=40, height=1280, width=720, generator=torch.Generator("cuda").manual_seed(semilla)).images[0]
        imgs[n] = im
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
    for n, ini, fin, seg, prompt in H3:
        r = requests.post("http://127.0.0.1:8188/prompt", json={"prompt": _flujo(ini, fin, None, prompt, n, semilla, _largo(seg))}).json()
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
def main(sitio: str = "sitio_columnas.jpg", semilla: int = 3):
    refs = {"T1_estructura": (AQUI / "salida_v2" / "T1_estructura_limpio.png").read_bytes(), "ref": (AQUI / "ref_placateja.jpg").read_bytes()}
    out = AQUI / "salida_v3"; out.mkdir(exist_ok=True)
    for n, v in todo.remote(refs, semilla).items():
        (out / n).write_bytes(v); print("guardado", n)
