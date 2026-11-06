"""BD Pro Monterrey (pistas de baile) · antes y después: el ANTES son SUS fotos reales del montaje; Qwen genera el DESPUÉS (misma pista y mismo lugar, ya en
plena fiesta) y H3 anima la transformación de uno al otro (primer → último cuadro). Una sola GPU. Uso: modal run bdpro_modal.py"""
import io, json, pathlib, sys
import modal
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/XV")
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/Mariano/flyers_animados")
from flyers_modal import imagen, datos, qwen
from xv_modal import _flujo, ANCHO, ALTO, CARPETA

app = modal.App("bdpro-antes-despues", image=imagen.add_local_python_source("flyers_modal", "xv_modal"))
AQUI = pathlib.Path(__file__).resolve().parent
MAT = AQUI.parent / "material"
IGUAL = "Conserva EXACTAMENTE la misma pista de baile (mismo diseño, colores y monograma), el mismo lugar y el mismo encuadre. "
PARES = {  # nombre: (foto real del antes, cómo es el después, cómo se transforma)
    "AD1_jardin": ("20_1024_0029_f", IGUAL + "Ahora es de noche y es una boda: mesas con manteles blancos y velas, guirnaldas de focos cálidos, la pareja de novios bailando en el centro de la pista y los invitados alrededor. Foto vertical 9:16 realista, sin texto.",
                   "Time-lapse transformation: the empty lawn with the white monogram dance floor becomes a wedding night party, string lights turn on, tables appear and the couple dances on the floor. Smooth slow push-in. No text. Audio: soft party ambience, no speech."),
    "AD2_hacienda": ("03_1023_2128", IGUAL + "Ahora el salón está en plena fiesta de XV años: luces de colores, la quinceañera con vestido bailando al centro de la pista con sus chambelanes, invitados alrededor. Foto vertical 9:16 realista, sin texto.",
                     "Time-lapse transformation: the empty hacienda hall with the dance floor fills with colorful party lights and a quinceañera dancing with her partners, guests around. Smooth slow push-in. No text. Audio: party ambience, no speech."),
    "AD3_empresa": ("18_1024_0029_f", IGUAL + "Ahora es un evento de empresa: al fondo un escenario con pantalla LED grande, bocinas profesionales e iluminación, ejecutivos de traje en la pista. Foto vertical 9:16 realista, sin texto, la pantalla sin letras.",
                    "Time-lapse transformation: the empty hall with the striped dance floor turns into a corporate event with an LED screen stage, pro speakers and lights, executives gather on the floor. Smooth slow push-in. No text. Audio: event ambience, no speech."),
}


@app.function(gpu="A100-80GB", volumes={"/datos": datos, "/qwen": qwen}, timeout=5400)
def todo(fotos: dict, semilla: int = 5) -> dict:
    import gc, glob, os, subprocess, time, requests, torch
    from PIL import Image
    from diffusers import QwenImageEditPlusPipeline
    carpeta = f"/datos/siena/{CARPETA}"
    os.makedirs(carpeta, exist_ok=True)
    salida = {}
    pendientes = [n for n in PARES if not os.path.exists(f"{carpeta}/{n}_fin.png")]   # si Modal reinicia el contenedor, no repite lo hecho
    if pendientes:
        pipe = QwenImageEditPlusPipeline.from_pretrained("/qwen/Qwen-Image-Edit-2511", torch_dtype=torch.bfloat16).to("cuda")
        for n in pendientes:
            foto, despues, _ = PARES[n]
            real = Image.open(io.BytesIO(fotos[foto])).convert("RGB")
            real.resize((ANCHO, ALTO), Image.LANCZOS).save(f"{carpeta}/{n}_ini.png")
            im = pipe(image=[real], prompt=despues, negative_prompt="texto, letras, pista distinta, deforme, borroso, caras deformes", true_cfg_scale=4.0, guidance_scale=1.0,
                      num_inference_steps=40, height=1280, width=720, generator=torch.Generator("cuda").manual_seed(semilla)).images[0]
            im.resize((ANCHO, ALTO), Image.LANCZOS).save(f"{carpeta}/{n}_fin.png"); datos.commit()
            print("despues", n, flush=True)
        del pipe; gc.collect(); torch.cuda.empty_cache()
    for n in PARES:
        salida[f"{n}_despues.png"] = open(f"{carpeta}/{n}_fin.png", "rb").read()
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
    for n, (_, _, mover) in PARES.items():
        r = requests.post("http://127.0.0.1:8188/prompt", json={"prompt": _flujo(f"{n}_ini", f"{n}_fin", None, mover, n, semilla, 124)}).json()
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
def main(semilla: int = 5):
    from PIL import Image, ImageOps
    fotos = {}
    for foto, _, _ in PARES.values():
        im = ImageOps.fit(ImageOps.exif_transpose(Image.open(MAT / f"{foto}.jpg")).convert("RGB"), (720, 1280), Image.LANCZOS)
        b = io.BytesIO(); im.save(b, "PNG"); fotos[foto] = b.getvalue()
    out = AQUI / "tomas"; out.mkdir(exist_ok=True)
    for n, v in todo.remote(fotos, semilla).items():
        (out / n).write_bytes(v); print("guardado", n)
