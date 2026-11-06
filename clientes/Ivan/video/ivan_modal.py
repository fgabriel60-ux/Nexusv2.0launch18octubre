"""Fumicam (Iván): anima con MiniMax H3 las fotos REALES de sus trabajadores (la foto es el primer cuadro: identidad y uniforme se conservan).
Una sola GPU, un solo arranque de ComfyUI, tomas en serie. Uso: modal run ivan_modal.py"""
import io, pathlib, sys
import modal
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/XV")
from xv_modal import imagen, datos, _flujo, ANCHO, ALTO, CARPETA

app = modal.App("ivan-fumicam", image=imagen.add_local_python_source("xv_modal"))
AQUI = pathlib.Path(__file__).resolve().parent
FOTOS = AQUI.parent / "whatsapp" / "del_cliente_19oct"
FIN = " Keep the worker's face, blue uniform, mask and equipment exactly as in the first frame. Realistic documentary look, natural light, handheld feel. No text. Audio: soft ambient, no speech."
# toma: (foto, centro horizontal del recorte 9:16, prompt)
TOMAS = {
    "I1_cuarto": ("2043_2", .68, "Vertical shot of a pest control worker in a blue uniform and pink respirator mask fumigating a bedroom next to the bed. Slow gentle push-in, he sprays along the baseboard with a steady hand, a light mist is visible." + FIN),
    "I2_patio": ("2043_5", .50, "Vertical shot of a pest control worker with a green backpack sprayer fumigating the base of a large tree in a yard. Slow push-in, he raises the spray wand and a fine mist spreads, leaves move softly." + FIN),
    "I3_sala": ("2124_9", .45, "Vertical shot of a pest control worker fumigating the waiting room of a clinic, spraying under the metal chairs. Slow push-in, he walks a step and keeps spraying with the hose, steady and professional." + FIN),
    "I4_oficina": ("2124_11", .50, "Vertical shot of a pest control worker with a respirator fumigating the top of an office wall with a long spray wand near a filing cabinet. Slow push-in, a light mist drifts upward." + FIN),
    "I5_jardin": ("2124_10", .55, "Vertical shot of a pest control worker with a respirator spraying the garden beds next to a cactus and red volcanic gravel outside a building. Slow push-in, steady spraying motion." + FIN),
    "I6_pasillo": ("2124_7", .72, "Vertical shot of a pest control worker with a respirator fumigating a narrow hallway with pink walls and red tile floor, spraying along the wall base. Slow push-in, calm professional movement." + FIN),
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
    for n, (foto, cx, prompt) in TOMAS.items():
        im = ImageOps.exif_transpose(Image.open(FOTOS / f"{foto}.jpg")).convert("RGB")
        im = ImageOps.fit(im, (ANCHO, ALTO), Image.LANCZOS, centering=(cx, .5))
        b = io.BytesIO(); im.save(b, "PNG"); fotos[n] = b.getvalue(); prompts[n] = prompt
        im.save(AQUI / f"{n}_primer_cuadro.png")
    (AQUI / "tomas").mkdir(exist_ok=True)
    for n, v in lote.remote(fotos, prompts, semilla).items():
        (AQUI / "tomas" / f"{n}.mp4").write_bytes(v); print("guardado", n)
