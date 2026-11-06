"""José · Grupo JR · obrero Pixar v3 (correcciones de José 28-29 oct): impermeabilizador de verdad (casco + overol AZUL MARINO), recubrimiento LÍQUIDO blanco en CUBETAS,
sin cemento/costales/mezcladora, losa con volcán de Puebla. 6 escenas Qwen → 6 clips H3 (sin voz; la voz clonada va en el armado).
Uso: python3 gasto_modal.py run clientes/Jose/obrero_v3_20261029/jose_v3_modal.py"""
import io, json, pathlib, sys
import modal
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/XV")
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/Mariano/flyers_animados")
from flyers_modal import imagen, datos, qwen
from xv_modal import _flujo, _largo, ANCHO, ALTO, CARPETA

app = modal.App("jose-v3-obrero", image=imagen.add_local_python_source("flyers_modal", "xv_modal"))
AQUI = pathlib.Path(__file__).resolve().parent
ESTILO = "Estilo animación 3D tipo Pixar, proporciones tiernas, texturas suaves, iluminación cálida de cine, colores vivos, foto vertical 9:16, sin texto, sin letras, sin subtítulos, sin logotipos. "
OBRERO = ("Un obrero animado estilo Pixar, con la misma cara y casco blanco que la referencia, con OVEROL AZUL MARINO completo de trabajo, guantes y botas negras. ")
LOSA = "sobre la losa de concreto de una azotea mexicana con el volcán nevado de Puebla al fondo y cielo azul. "
NO = "El fondo es SOLO la azotea, el volcán nevado y el cielo: NO hay ningún camión, vehículo, máquina, mezcladora, manguera, costal, cemento ni bulto. "
CUBETA = "cubeta de plástico blanca con tapa abierta llena de recubrimiento líquido blanco cremoso (sin letras en la cubeta)"
QWEN = {  # nombre: (referencias, prompt)
    "J1_gancho": (["obrero"], ESTILO + OBRERO + "Está de pie al frente, sin escoba, " + LOSA + f"Junto a él hay una {CUBETA} y un rodillo. Mira a cámara con confianza, un pulgar hacia arriba. Plano medio-cercano, él ocupa gran parte del cuadro. " + NO),
    "J2_prepara": (["obrero"], ESTILO + OBRERO + "Barre con una escoba SOLO en este cuadro, " + LOSA + "Plano medio-cercano ligeramente picado, él grande en el cuadro. " + NO),
    "J3_cubeta": (["obrero"], ESTILO + OBRERO + f"Está agachado y vierte con cuidado recubrimiento líquido blanco desde una {CUBETA} en una charola de pintura, SIN escoba, " + LOSA + "Plano medio-cercano, él grande en el cuadro. " + NO),
    "J4_rodillo": (["obrero"], ESTILO + OBRERO + "Aplica con un rodillo grande una capa uniforme de recubrimiento líquido blanco brillante sobre la losa gris, SIN escoba, la mitad de la losa ya blanca, " + LOSA + "Plano medio-cercano, él grande en el cuadro. " + NO),
    "J5_lluvia": (["obrero"], ESTILO + OBRERO + "Está de pie, SIN escoba, con los brazos abiertos sobre la losa ya completamente blanca e impermeabilizada; llueve, las gotas ruedan sobre la superficie blanca sin filtrarse, " + LOSA.replace("cielo azul", "cielo con nubes de lluvia") + "Plano medio. " + NO),
    "J6_cierre": (["obrero"], ESTILO + OBRERO + f"Sonríe a cámara, SIN escoba, sosteniendo con una mano una {CUBETA} y saluda con la otra, losa blanca limpia detrás, " + LOSA + "Plano medio, ligeramente contrapicado. " + NO),
}
H3 = [  # (toma, primer cuadro, último cuadro, seg, prompt)
    ("J1_gancho", "J1_gancho", None, 4.0, "Vertical animated shot: the cartoon worker in navy overalls and white helmet gives a confident thumbs-up to the camera and nods, the white bucket and roller beside him, slow camera push-in. Keep the same character. No text. Audio: soft ambient, no speech."),
    ("J2_prepara", "J2_prepara", None, 4.0, "Vertical animated shot: the cartoon worker in navy overalls sweeps the concrete slab with a broom, a little dust rises, smooth side dolly. Keep the same character. No text. Audio: soft sweeping sound, no speech."),
    ("J3_cubeta", "J3_cubeta", None, 4.0, "Vertical animated shot: the cartoon worker carefully pours white liquid coating from the bucket into the paint tray, smooth creamy liquid flows, slow push-in. Keep the same character. No text. Audio: soft pouring sound, no speech."),
    ("J4_rodillo", "J4_rodillo", None, 5.0, "Vertical animated shot: the cartoon worker rolls glossy white liquid coating across the grey concrete slab, the white area grows, slow lateral dolly. Keep the same character. No text. Audio: soft roller sound, no speech."),
    ("J5_lluvia", "J5_lluvia", None, 4.0, "Vertical animated shot: rain falls on the fully white waterproofed slab, drops bead up and roll off, the cartoon worker opens his arms happily under the rain, slow camera pull-back. Keep the same character. No text. Audio: soft rain, no speech."),
    ("J6_cierre", "J6_cierre", None, 4.0, "Vertical animated shot: the cartoon worker smiles, waves and lifts the white bucket toward the camera, slow push-in. Keep the same character. No text. Audio: soft ambient, no speech."),
]


@app.function(gpu="A100-80GB", volumes={"/datos": datos, "/qwen": qwen}, timeout=7200)
def todo(refs: dict, semilla: int = 21) -> dict:
    import gc, glob, os, subprocess, time, requests, torch
    from PIL import Image
    from diffusers import QwenImageEditPlusPipeline
    carpeta = f"/datos/siena/{CARPETA}"
    os.makedirs(carpeta, exist_ok=True)
    imgs = {k: Image.open(io.BytesIO(v)).convert("RGB") for k, v in refs.items()}
    pipe = QwenImageEditPlusPipeline.from_pretrained("/qwen/Qwen-Image-Edit-2511", torch_dtype=torch.bfloat16).to("cuda")
    salida = {}
    for n, (usar, p) in QWEN.items():
        im = pipe(image=[imgs[u] for u in usar], prompt=p, negative_prompt="escoba (excepto escena de barrer), camión, vehículo, máquina, texto, letras, subtítulos, logotipo, cemento, costales, camión, mezcladora, manguera, cara distinta, deforme, borroso, manos extra",
                  true_cfg_scale=4.0, guidance_scale=1.0, num_inference_steps=40, height=1280, width=720, generator=torch.Generator("cuda").manual_seed(semilla)).images[0]
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
def main(semilla: int = 21):
    refs = {"obrero": (AQUI / "ref_obrero_recorte.png").read_bytes()}
    out = AQUI / "salida"; out.mkdir(exist_ok=True)
    for n, v in todo.remote(refs, semilla).items():
        (out / n).write_bytes(v); print("guardado", n)
