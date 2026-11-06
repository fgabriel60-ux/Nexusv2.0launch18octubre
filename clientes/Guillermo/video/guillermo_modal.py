"""Guillermo (herrería, Puebla): «del fierro al resultado» con las FOTOS reales de UNA sola obra (casa con pérgola negra y techo translúcido).
La foto es el primer cuadro de cada toma (la obra no cambia). Una sola GPU, un solo arranque de ComfyUI, tomas en serie. Uso: modal run guillermo_modal.py"""
import io, pathlib, sys
import modal
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/XV")
from xv_modal import imagen, datos, _flujo, ANCHO, ALTO, CARPETA

app = modal.App("guillermo-perg", image=imagen.add_local_python_source("xv_modal"))
AQUI = pathlib.Path(__file__).resolve().parent
FOTOS = AQUI.parent / "whatsapp" / "del_cliente"
FIN = " Keep the house, the steel structure, the panels and the worker exactly as in the first frame. Realistic documentary look, natural daylight, handheld feel. No text. Audio: soft ambient, no speech."
# toma: (foto, centro horizontal del recorte 9:16, prompt)
TOMAS = {
    "G1_estructura": ("20261022_170427_image", .5, "Vertical shot of the black and red steel pergola frame built on the roof terrace of a white two-story house under a cloudy sky. Slow gentle push-in, the clouds drift slowly behind the steel beams, no people." + FIN),
    "G2_colocacion": ("20261022_170426_image", .5, "Vertical shot of a worker in a reflective vest standing on an aluminum ladder, placing a translucent panel on the black steel pergola frame on top of a white house. Slow push-in, he adjusts the panel with calm professional movements." + FIN),
    "G3_terminada": ("20261022_170425_image", .5, "Vertical shot of the finished black steel pergola with a translucent roof above the balcony railing of a white house with white window grilles. Slow smooth push-in, soft sunlight glints on the panels." + FIN),
    "G4_cielo": ("20261022_170428_image", .5, "Vertical low-angle shot of the finished black steel pergola above the black balcony railing of a white house against a bright blue sky with white clouds. Slow gentle push-in and a very slight upward tilt, the clouds move softly." + FIN),
}


@app.function(gpu="A100-80GB", volumes={"/datos": datos}, timeout=7200)
def lote(fotos: dict, prompts: dict, semilla: int = 2) -> dict:
    import glob, os, subprocess, time, requests, json
    carpeta = f"/datos/siena/{CARPETA}"
    os.makedirs(carpeta, exist_ok=True)
    for n, f in fotos.items():
        open(f"{carpeta}/{n}.png", "wb").write(f)
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
    salida = {}
    for n in fotos:
        r = requests.post("http://127.0.0.1:8188/prompt", json={"prompt": _flujo(n, None, None, prompts[n], n, semilla, 124)}).json()
        if "prompt_id" not in r:
            raise RuntimeError(json.dumps(r)[:3000])
        pid = r["prompt_id"]
        while True:
            h = requests.get(f"http://127.0.0.1:8188/history/{pid}").json()
            if pid in h:
                st = h[pid].get("status", {})
                if st.get("status_str") == "error":
                    raise RuntimeError(json.dumps(st)[:3000])
                break
            time.sleep(5)
        archivo = sorted(glob.glob(f"/datos/siena/out/{CARPETA}/{n}_*.mp4"), key=os.path.getmtime)[-1]
        salida[n] = open(archivo, "rb").read()
        print("listo", n, flush=True)
    datos.commit()
    return salida


@app.local_entrypoint()
def main(semilla: int = 2):
    from PIL import Image, ImageOps
    fotos, prompts = {}, {}
    (AQUI / "tomas").mkdir(exist_ok=True)
    for n, (foto, cx, prompt) in TOMAS.items():
        im = ImageOps.exif_transpose(Image.open(FOTOS / f"{foto}.jpg")).convert("RGB")
        im = ImageOps.fit(im, (ANCHO, ALTO), Image.LANCZOS, centering=(cx, .5))
        b = io.BytesIO(); im.save(b, "PNG"); fotos[n] = b.getvalue(); prompts[n] = prompt
        im.save(AQUI / f"{n}_primer_cuadro.png")
    for n, v in lote.remote(fotos, prompts, semilla).items():
        (AQUI / "tomas" / f"{n}.mp4").write_bytes(v); print("guardado", n)
