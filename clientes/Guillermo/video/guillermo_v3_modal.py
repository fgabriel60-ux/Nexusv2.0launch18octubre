"""Guillermo (Proyectos Metálicos Vicens) · 3 videos: PÉRGOLAS v3, TECHOS y ZAGUANES con SUS fotos reales.
Gancho con IA: la pérgola se arma sola (primer cuadro = estructura roja, último = pérgola terminada, misma casa). Más tomas H3 de techos y zaguanes.
Una sola GPU, un solo arranque de ComfyUI. Uso: modal run guillermo_v3_modal.py"""
import io, json, pathlib, sys
import modal
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/XV")
from xv_modal import imagen, datos, _flujo, ANCHO, ALTO, CARPETA

app = modal.App("guillermo-3-videos", image=imagen.add_local_python_source("xv_modal"))
AQUI = pathlib.Path(__file__).resolve().parent
FOTOS = AQUI.parent / "whatsapp" / "del_cliente"
FIN = " Keep the buildings, the steel structures and the workers exactly as in the first frame. Realistic documentary look, natural daylight. No text. Audio: soft ambient, no speech."
# toma: (foto inicio, foto final o None, centro horizontal del recorte, prompt)
TOMAS = {
    "H_pergola_se_arma": ("20261022_170427_image", "20261022_170425_image", .5, "Vertical time-lapse shot of a steel pergola being built on the roof terrace of a white house: the red primer beams turn black and translucent roof panels are placed one by one until the pergola is finished. Smooth slow push-in, clouds move fast." + FIN),
    "T1_lamina": ("20261022_170717_image", None, .5, "Vertical shot of workers on scaffolding installing metal roof sheets on a green steel roof structure over a school patio. Slow push-in, a worker lifts and places a sheet." + FIN),
    "T2_techumbre": ("20261022_170712_image", None, .5, "Vertical shot of a finished green steel roof structure with metal sheets and translucent skylights over a large school patio. Slow cinematic push-in, sunlight through the skylights." + FIN),
    "T3_nave": ("20261022_170524_image", None, .5, "Vertical shot inside a large industrial warehouse with a new red metal roof on a black steel truss structure. Slow upward tilt revealing the roof, dust in the light." + FIN),
    "Z1_porton": ("20261022_170428_image", None, .5, "Vertical low-angle shot of a white house with a white steel grille gate (zaguán) and lattice windows under a blue sky. Slow push-in toward the white steel gate." + FIN),
    "Z2_celosia": ("20261022_170425_image", None, .5, "Vertical shot of a white two-story house with white steel lattice window grilles and gate, and a black balcony railing. Slow lateral camera move along the facade." + FIN),
}


@app.function(gpu="A100-80GB", volumes={"/datos": datos}, timeout=7200)
def lote(fotos: dict, tomas: dict, semilla: int = 2) -> dict:
    import glob, os, subprocess, time, requests
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
    for n, (ini, fin, prompt) in tomas.items():
        r = requests.post("http://127.0.0.1:8188/prompt", json={"prompt": _flujo(ini, fin, None, prompt, n, semilla, 124)}).json()
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
        salida[n] = open(archivo, "rb").read(); print("listo", n, flush=True)
    datos.commit()
    return salida


@app.local_entrypoint()
def main(semilla: int = 2):
    from PIL import Image, ImageOps
    fotos, tomas = {}, {}
    (AQUI / "tomas_v3").mkdir(exist_ok=True)
    for n, (ini, fin, cx, prompt) in TOMAS.items():
        for f in (ini, fin):
            if f and f not in fotos:
                im = ImageOps.fit(ImageOps.exif_transpose(Image.open(FOTOS / f"{f}.jpg")).convert("RGB"), (ANCHO, ALTO), Image.LANCZOS, centering=(cx, .5))
                b = io.BytesIO(); im.save(b, "PNG"); fotos[f] = b.getvalue()
        tomas[n] = (ini, fin, prompt)
    for n, v in lote.remote(fotos, tomas, semilla).items():
        (AQUI / "tomas_v3" / f"{n}.mp4").write_bytes(v); print("guardado", n)
