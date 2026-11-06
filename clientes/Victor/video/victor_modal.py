"""Servilin (Víctor): escenas animadas a partir de cuadros REALES del video de su equipo de limpieza (uniforme azul, chaleco amarillo).
El cuadro real es el primer cuadro de cada toma (caras y uniformes no cambian). Una sola GPU, un solo arranque de ComfyUI, tomas en serie. Uso: modal run guillermo_modal.py"""
import io, pathlib, sys
import modal
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/XV")
from xv_modal import imagen, datos, _flujo, ANCHO, ALTO, CARPETA

app = modal.App("victor-servilin", image=imagen.add_local_python_source("xv_modal"))
AQUI = pathlib.Path(__file__).resolve().parent
FOTOS = AQUI / "cuadros"
FIN = " Keep every worker's face, the blue uniforms, yellow reflective vests and red gloves exactly as in the first frame. Realistic documentary look, natural light, handheld feel. No text. Audio: soft ambient, no speech."
# toma: (cuadro real, centro horizontal del recorte 9:16, prompt)
TOMAS = {
    "V1_equipo": ("f_1.5", .5, "Vertical shot of a large professional cleaning crew in blue uniforms and yellow reflective vests standing in a bright industrial building hallway while a supervisor gives instructions. Slow gentle push-in, the workers listen attentively and nod slightly." + FIN),
    "V2_escucha": ("f_8", .5, "Vertical shot of cleaning workers in blue uniforms and yellow reflective vests gathered for a morning briefing, the supervisor at the back raises his hand to point. Slow lateral camera move, calm attentive people." + FIN),
    "V3_supervisor": ("f_15", .5, "Vertical shot of a supervisor in a blue uniform giving instructions to his cleaning team in yellow reflective vests inside a bright facility. Slow push-in toward the supervisor, workers turn their heads to listen." + FIN),
    "V4_listos": ("f_23", .5, "Vertical shot of an organized cleaning crew in blue uniforms and yellow reflective vests ready to start the shift in a bright industrial hallway. Slow pull-back revealing the whole team, confident professional mood." + FIN),
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
