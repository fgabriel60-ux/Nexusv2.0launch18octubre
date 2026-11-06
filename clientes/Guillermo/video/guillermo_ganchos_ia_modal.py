"""Guillermo · ganchos con IA para TECHOS y ZAGUANES + escenas de ZAGUANES, CORTINAS Y PUERTAS (lo pidió él) (como el de pérgolas): Qwen quita lo que construyó él (el techo / el portón y celosías) de SU foto real,
y H3 anima de esa versión «antes» a la foto real terminada (primer → último cuadro): la obra se arma sola. Una sola GPU. Uso: modal run guillermo_ganchos_ia_modal.py"""
import io, json, pathlib, sys
import modal
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/XV")
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/Mariano/flyers_animados")
from flyers_modal import imagen, datos, qwen
from xv_modal import _flujo, ANCHO, ALTO, CARPETA

app = modal.App("guillermo-ganchos-ia", image=imagen.add_local_python_source("flyers_modal", "xv_modal"))
AQUI = pathlib.Path(__file__).resolve().parent
FOTOS = AQUI.parent / "whatsapp" / "del_cliente"
SIN = " Mismo encuadre, misma luz y mismo cielo. Foto vertical 9:16 realista, sin texto."
OBRAS = {  # gancho: (foto real terminada, cómo era antes, cómo se arma)
    "H_techo_se_arma": ("20261022_170712_image", "Quita por completo la estructura verde y el techo de lámina: deja el mismo patio de la escuela al aire libre, con el mismo piso, los mismos muros, el mural y el cielo azul." + SIN,
                        "Vertical time-lapse: a green steel roof structure rises over the school patio, beams are placed and metal roof sheets with skylights cover it piece by piece until the roof is finished. Fast construction time-lapse, smooth slow push-in. No text. Audio: construction ambience, no speech."),
    "H_zaguan_se_arma": ("20261022_170428_image", "Quita el portón blanco de acero y todas las celosías blancas de las ventanas: deja la misma casa blanca con los vanos vacíos de la puerta y las ventanas, y el mismo barandal negro." + SIN,
                         "Vertical time-lapse: white steel lattice grilles and a white steel gate are installed piece by piece on the white house until the facade is finished. Fast construction time-lapse, smooth slow push-in. No text. Audio: metal work ambience, no speech."),
}

ESTILO = "Mismo estilo de obra real de herrería en Puebla que la foto de referencia: casas blancas, acero pintado, luz de día y cielo azul. "
NUEVAS = {  # escenas nuevas generadas con su obra como referencia: (prompt de Qwen, movimiento H3)
    "N1_cortina": (ESTILO + "Una cortina metálica enrollable negra recién instalada en la fachada de un local comercial, a medio subir. Foto vertical 9:16 realista, sin texto, sin letreros.",
                   "Vertical shot: the black rolling steel shutter of the shop rolls up smoothly, revealing the shop entrance. Slow push-in. No text. Audio: metal shutter rolling, no speech."),
    "N2_puerta": (ESTILO + "Una puerta principal de herrería negra con diseño de líneas y vidrio en una casa blanca moderna, recién instalada. Foto vertical 9:16 realista, sin texto.",
                  "Vertical shot: the black steel front door slowly opens, sunlight on the glass, slow push-in toward the door. No text. Audio: soft door sound, no speech."),
    "N3_zaguan": (ESTILO + "Un zaguán de acero negro de dos hojas con celosía horizontal en la cochera de una casa blanca, recién instalado. Foto vertical 9:16 realista, sin texto.",
                  "Vertical shot: the two leaves of the black steel garage gate (zaguán) swing open slowly, revealing the driveway. Slow push-in. No text. Audio: metal gate, no speech."),
}


@app.function(gpu="A100-80GB", volumes={"/datos": datos, "/qwen": qwen}, timeout=5400)
def todo(fotos: dict, semilla: int = 4) -> dict:
    import gc, glob, os, subprocess, time, requests, torch
    from PIL import Image
    from diffusers import QwenImageEditPlusPipeline
    carpeta = f"/datos/siena/{CARPETA}"
    os.makedirs(carpeta, exist_ok=True)
    pipe = QwenImageEditPlusPipeline.from_pretrained("/qwen/Qwen-Image-Edit-2511", torch_dtype=torch.bfloat16).to("cuda")
    salida = {}
    for n, (foto, antes, _) in OBRAS.items():
        real = Image.open(io.BytesIO(fotos[foto])).convert("RGB")
        real.resize((ANCHO, ALTO), Image.LANCZOS).save(f"{carpeta}/{n}_fin.png")
        im = pipe(image=[real], prompt=antes, negative_prompt="texto, letras, deforme, borroso, encuadre distinto", true_cfg_scale=4.0, guidance_scale=1.0,
                  num_inference_steps=40, height=1280, width=720, generator=torch.Generator("cuda").manual_seed(semilla)).images[0]
        im.resize((ANCHO, ALTO), Image.LANCZOS).save(f"{carpeta}/{n}_ini.png")
        b = io.BytesIO(); im.save(b, "PNG"); salida[f"{n}_antes.png"] = b.getvalue(); print("antes", n, flush=True)
    ref = Image.open(io.BytesIO(fotos["20261022_170428_image"])).convert("RGB")
    for n, (p, _) in NUEVAS.items():
        im = pipe(image=[ref], prompt=p, negative_prompt="texto, letras, letreros, deforme, borroso", true_cfg_scale=4.0, guidance_scale=1.0,
                  num_inference_steps=40, height=1280, width=720, generator=torch.Generator("cuda").manual_seed(semilla)).images[0]
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
    trabajos = [(n, f"{n}_ini", f"{n}_fin", mover) for n, (_, _, mover) in OBRAS.items()] + [(n, n, None, mover) for n, (_, mover) in NUEVAS.items()]
    for n, ini, fin, mover in trabajos:
        r = requests.post("http://127.0.0.1:8188/prompt", json={"prompt": _flujo(ini, fin, None, mover, n, semilla, 124)}).json()
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
    from PIL import Image, ImageOps
    fotos = {}
    for foto, _, _ in OBRAS.values():
        im = ImageOps.fit(ImageOps.exif_transpose(Image.open(FOTOS / f"{foto}.jpg")).convert("RGB"), (720, 1280), Image.LANCZOS)
        b = io.BytesIO(); im.save(b, "PNG"); fotos[foto] = b.getvalue()
    for n, v in todo.remote(fotos, semilla).items():
        (AQUI / "tomas_v3" / n).write_bytes(v); print("guardado", n)
