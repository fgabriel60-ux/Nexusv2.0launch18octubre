"""Lisbeth (Tomatlán): ella lanza el dron hacia arriba y desde el aire se ve la casa construyéndose sobre el terreno.
Qwen-Image-Edit crea 4 cuadros (ella con el dron en el campo; el lote aéreo limpio; obra negra; casa terminada) y H3 anima 5 tomas:
habla (su voz) → lanza el dron → el lote se construye (primer→último cuadro) → casa terminada → cierre hablando. Una sola GPU.
Uso: modal run lisbeth_dron_modal.py"""
import io, json, pathlib, sys
import modal
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/XV")
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/Mariano/flyers_animados")
from flyers_modal import imagen, datos, qwen
from xv_modal import _flujo, _largo, ANCHO, ALTO, CARPETA

app = modal.App("lisbeth-dron", image=imagen.add_local_python_source("flyers_modal", "xv_modal"))
AQUI = pathlib.Path(__file__).resolve().parent
WA = AQUI.parent / "whatsapp" / "del_cliente"
SIN = " Foto vertical 9:16, realista, nítida, alta resolución, sin texto, sin letras, sin líneas dibujadas."
Q_DRON = ("Conserva EXACTAMENTE a esta mujer: la misma cara, ojos, cejas, nariz, labios, edad, tono de piel y su cabello oscuro recogido. "
          "Ponla de pie en un terreno de campo en Tomatlán, Jalisco, con lomas verdes, montañas al fondo y cielo azul con nubes, luz cálida de tarde. "
          "Viste blusa negra. Sostiene con ambas manos un pequeño dron blanco frente a ella a la altura del pecho y mira a la cámara con una sonrisa segura. Plano medio." + SIN)
Q_LOTE = ("Quita TODAS las líneas naranjas, la línea punteada y todo el texto. Deja la misma vista aérea de dron del mismo terreno de lomas con vegetación y el camino, "
          "con montañas al fondo y luz dorada de tarde." + SIN)
Q_OBRA = ("Misma vista aérea EXACTA del mismo terreno, mismo encuadre y misma luz. Ahora en el centro del lote se ve la obra negra de una casa moderna de una planta: "
          "cimientos, muros de block gris, castillos de varilla y montones de material de construcción. El resto del paisaje igual." + SIN)
Q_CASA = ("Misma vista aérea EXACTA del mismo terreno, mismo encuadre y misma luz. Ahora en el centro del lote hay una casa moderna de una planta terminada, "
          "muros blancos con detalles de madera, terraza techada, pequeña alberca y jardín verde. El resto del paisaje igual." + SIN)
FIN = " Keep her face, hair and black blouse exactly as in the first frame. Realistic, natural light. No text."
TOMAS = [  # (nombre, primer cuadro, último cuadro, voz, prompt, segundos)
    ("L0_habla", "Q_dron", None, "L_A", "Vertical medium shot: the woman holding a small white drone in a green countryside field speaks directly to the camera with natural lip movement matching the speech and a confident smile." + FIN + " Audio: clear female voice speaking Spanish.", 5.85),
    ("L1_lanza", "Q_dron", None, None, "Vertical shot: the woman smiles and tosses the small white drone upward with both hands, the drone's propellers spin and it flies up out of the top of the frame, the camera tilts up following it toward the blue sky." + FIN + " Audio: wind and a soft drone buzz, no speech.", 5.0),
    ("L2_obra", "Q_lote", "Q_obra", None, "Aerial drone shot slowly descending over the hillside lot as a house construction appears in the middle: foundations and block walls rise. Smooth cinematic drone movement, the landscape stays the same. No text. Audio: wind, no speech.", 5.0),
    ("L3_casa", "Q_obra", "Q_casa", None, "Aerial drone shot slowly orbiting the lot while the construction is completed into a finished modern white house with a terrace, a small pool and a green garden. Smooth cinematic drone movement, the landscape stays the same. No text. Audio: wind, no speech.", 5.0),
    ("L4_cierre", "Q_dron", None, "L_C", "Vertical medium shot: the woman holding a small white drone in a green countryside field speaks to the camera with natural lip movement matching the speech and a warm inviting smile." + FIN + " Audio: clear female voice speaking Spanish.", 3.13),
]


@app.function(gpu="A100-80GB", volumes={"/datos": datos, "/qwen": qwen}, timeout=7200)
def todo(foto: bytes, terreno: bytes, voces: dict, semilla: int = 6) -> dict:
    import gc, glob, os, subprocess, time, requests, torch
    from PIL import Image
    from diffusers import QwenImageEditPlusPipeline
    carpeta = f"/datos/siena/{CARPETA}"
    os.makedirs(carpeta, exist_ok=True)
    for n, v in voces.items():
        open(f"{carpeta}/{n}.wav", "wb").write(v)
    pipe = QwenImageEditPlusPipeline.from_pretrained("/qwen/Qwen-Image-Edit-2511", torch_dtype=torch.bfloat16).to("cuda")
    def gen(imgs, p):
        return pipe(image=imgs, prompt=p, negative_prompt="texto, letras, líneas naranjas, cara distinta, deforme, borroso, manos extra",
                    true_cfg_scale=4.0, guidance_scale=1.0, num_inference_steps=40, height=1280, width=720, generator=torch.Generator("cuda").manual_seed(semilla)).images[0]
    salida, cuadros = {}, {}
    cuadros["Q_dron"] = gen([Image.open(io.BytesIO(foto)).convert("RGB")], Q_DRON)
    cuadros["Q_lote"] = gen([Image.open(io.BytesIO(terreno)).convert("RGB")], Q_LOTE)
    cuadros["Q_obra"] = gen([cuadros["Q_lote"]], Q_OBRA)
    cuadros["Q_casa"] = gen([cuadros["Q_lote"]], Q_CASA)
    for n, im in cuadros.items():
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
    for n, ini, fin, voz, prompt, seg in TOMAS:
        r = requests.post("http://127.0.0.1:8188/prompt", json={"prompt": _flujo(ini, fin, voz, prompt, n, semilla, _largo(seg))}).json()
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
def main(semilla: int = 6):
    voces = {k: (AQUI / "voz" / f"{k}.wav").read_bytes() for k in ("L_A", "L_C")}
    out = AQUI / "tomas"; out.mkdir(exist_ok=True)
    res = todo.remote((WA / "20261022_161302_image.jpg").read_bytes(), (WA / "20261013_143945_image.jpg").read_bytes(), voces, semilla)
    for n, v in res.items():
        (out / n).write_bytes(v); print("guardado", n)
