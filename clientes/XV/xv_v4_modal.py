"""XV Manuel v4: anima con MiniMax H3 los 6 cuadros de IA aprobados (✅ del 19 oct). Una sola GPU, un solo arranque de ComfyUI, tomas en serie.
Uso: modal run xv_v4_modal.py"""
import io, json, pathlib
import modal
from xv_modal import imagen, datos, _flujo, ANCHO, ALTO, CARPETA

app = modal.App("xv-manuel-v4", image=imagen.add_local_python_source("xv_modal"))
FIN = " Keep her face, tiara, dress and everything exactly as in the first frame. Filmic, shallow depth of field, soft stage lights, glitter in the air. No text. Audio: soft ambient, no speech."
TOMAS = {  # nombre: (cuadro IA aprobado, prompt de movimiento)
    "V1_heroe": ("ia_1_heroe_s5", "Cinematic vertical shot of a young woman in an emerald green ball gown and jeweled tiara smiling softly at the camera, guests behind her. Very slow gentle push-in, she blinks and tilts her head slightly, her curls and the tulle move in a light breeze." + FIN),
    "V2_pista": ("ia_2_pista_s9", "Cinematic vertical shot of a quinceañera in an emerald green gown on a glowing dance floor with her friends around her. Slow smooth push-in, she sways and smiles, friends dance softly, light beams sweep and confetti drifts." + FIN),
    "V3_xv": ("ia_3_xv_s9", "Cinematic vertical shot of a young woman in an emerald green gown beside a white floral arch with a glowing XV sign. Slow steady push-in, she smiles and gently lifts one side of her gown, the sign glows and sparkles." + FIN),
    "V5_robot": ("ia_5_robot_s5", "Cinematic vertical shot of a tall LED robot with glowing blue lights dancing among party guests. Slow push-in, the robot moves its arms to the beat, lights pulse, guests cheer and clap, confetti in the air. Keep the robot identical to the first frame. No text. Audio: party ambience, no speech."),
    "V6_familia": ("ia_6_familia_s9", "Cinematic vertical shot of a young woman in an emerald green gown at the center of her family raising glasses for a toast in front of a white floral arch. Slow push-in, everyone smiles and lifts their glasses, warm light." + FIN),
    "V8_detalle": ("ia_8_detalle_s5", "Cinematic vertical macro close-up of a jeweled crystal tiara and the beaded emerald green gown, slow push-in with a soft rack focus, tiny golden sparkles glinting and bokeh lights drifting. No people movement, no text. Audio: soft ambient, no speech."),
}


@app.function(gpu="A100-80GB", volumes={"/datos": datos}, timeout=7200)
def lote(fotos: dict, prompts: dict, semilla: int = 2) -> dict:
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
    from PIL import Image
    aqui = pathlib.Path(__file__).resolve().parent
    fotos, prompts = {}, {}
    for n, (cuadro, prompt) in TOMAS.items():
        im = Image.open(aqui / "frames_real" / f"{cuadro}.png").convert("RGB").resize((ANCHO, ALTO), Image.LANCZOS)
        b = io.BytesIO(); im.save(b, "PNG"); fotos[n] = b.getvalue(); prompts[n] = prompt
    (aqui / "modal_v4").mkdir(exist_ok=True)
    for n, v in lote.remote(fotos, prompts, semilla).items():
        (aqui / "modal_v4" / f"{n}.mp4").write_bytes(v); print("guardado", n)
