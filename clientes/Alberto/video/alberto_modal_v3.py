"""Veneers Dental (Dra. Ángeles): 2 tomas hablando con H3 a partir de SUS fotos reales; el audio Fish guía los labios (AddGuide).
Una sola GPU, un solo arranque de ComfyUI, tomas en serie. Uso: modal run alberto_modal.py"""
import io, math, pathlib, sys
import modal
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/XV")
from xv_modal import imagen, datos, _flujo, _largo, ANCHO, ALTO, CARPETA

app = modal.App("alberto-doctora", image=imagen.add_local_python_source("xv_modal"))
AQUI = pathlib.Path(__file__).resolve().parent
FOTOS = AQUI.parent / "whatsapp" / "del_cliente"
FIN = " She speaks directly to the camera with natural lip movement matching the speech, small head movements and a warm professional smile. Keep her face, blonde hair, glasses, black scrubs and the clinic exactly as in the first frame. Realistic, soft natural light. No text. Audio: clear female voice speaking Spanish."
# toma: (foto, centrado vertical del recorte, audio, prompt)
TOMAS = {
    "A1_presenta3": ("doctora_1", .42, "dra3_A", "Vertical medium shot of a female dentist with long blonde hair, glasses and black scrubs holding a dental implant model in both hands, speaking to the camera in a bright white clinic." + FIN),
    "A2_precio3": ("doctora_2", .40, "dra3_B", "Vertical medium shot of a female dentist with long blonde hair, glasses and black scrubs seated at a desk with a tooth cross-section model, speaking to the camera in a bright clinic." + FIN),
}


@app.function(gpu="A100-80GB", volumes={"/datos": datos}, timeout=7200)
def lote(fotos: dict, voces: dict, prompts: dict, segundos: dict, semilla: int = 2) -> dict:
    import glob, os, subprocess, time, requests, json
    carpeta = f"/datos/siena/{CARPETA}"
    os.makedirs(carpeta, exist_ok=True)
    for n, f in fotos.items():
        open(f"{carpeta}/{n}.png", "wb").write(f)
    for n, v in voces.items():
        open(f"{carpeta}/{n}.wav", "wb").write(v)
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
        voz = n.split("_")[0] + "_voz"
        r = requests.post("http://127.0.0.1:8188/prompt", json={"prompt": _flujo(n, None, voz, prompts[n], n, semilla, _largo(segundos[n]))}).json()
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
    import subprocess
    fotos, voces, prompts, segundos = {}, {}, {}, {}
    (AQUI / "tomas").mkdir(exist_ok=True)
    for n, (foto, cy, audio, prompt) in TOMAS.items():
        im = ImageOps.exif_transpose(Image.open(FOTOS / f"{foto}.jpg")).convert("RGB")
        im = ImageOps.fit(im, (ANCHO, ALTO), Image.LANCZOS, centering=(.5, cy))
        b = io.BytesIO(); im.save(b, "PNG"); fotos[n] = b.getvalue(); prompts[n] = prompt
        im.save(AQUI / f"{n}_primer_cuadro.png")
        voces[n.split("_")[0] + "_voz"] = (AQUI / "voz" / f"{audio.replace('dra_', 'dra_')}.wav").read_bytes()
        segundos[n] = len((AQUI / "voz" / f"{audio}.wav").read_bytes()) / 32000  # 16 kHz mono 16 bit
    for n, v in lote.remote(fotos, voces, prompts, segundos, semilla).items():
        (AQUI / "tomas" / f"{n}.mp4").write_bytes(v); print("guardado", n)
