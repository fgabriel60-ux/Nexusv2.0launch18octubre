"""José · Grupo JR · obrero v4 COMO LA REFERENCIA que mandó José el 30 oct (casco GRUPO JR, chaleco azul, cubetas rotuladas, taladro mezclador); antes v3 (correcciones de José 28-29 oct): impermeabilizador de verdad (casco + overol AZUL MARINO), recubrimiento LÍQUIDO blanco en CUBETAS,
sin cemento/costales/mezcladora, losa con volcán de Puebla. 6 escenas Qwen → 6 clips H3 (sin voz; la voz clonada va en el armado).
Uso: python3 gasto_modal.py run clientes/Jose/obrero_v4_20261030/jose_v4_modal.py"""
import io, json, pathlib, sys
import modal
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/XV")
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/Mariano/flyers_animados")
from flyers_modal import imagen, datos, qwen
from xv_modal import _flujo, _largo, ANCHO, ALTO, CARPETA

app = modal.App("jose-v4-obrero", image=imagen.add_local_python_source("flyers_modal", "xv_modal"))
AQUI = pathlib.Path(__file__).resolve().parent
ESTILO = "Estilo animación 3D tipo Pixar, proporciones tiernas, texturas suaves, iluminación cálida de cine, colores vivos, foto vertical 9:16, sin texto en la imagen salvo el rotulado de las cubetas, sin subtítulos. "
OBRERO = ("El mismo obrero animado de la referencia: CASCO BLANCO con el logo rojo y azul «GRUPO JR», CHALECO AZUL de seguridad con franjas reflejantes grises y el logo «JR» en el pecho, camisa blanca de manga larga, pantalón azul marino y botas negras, misma cara. ")
LOSA = "sobre la losa gris de concreto de una azotea mexicana, con el volcán nevado de Puebla al fondo y cielo azul. "
NO = "El fondo es SOLO la azotea, el volcán nevado y el cielo: NO hay camión, vehículo, máquina grande, costales, cemento ni bultos. "
CUB = ("dos cubetas blancas grandes con etiqueta: una dice «POLIURETANO ACRÍLICO 12 AÑOS» y la otra «PRIMARIO FIBRATADO ELÁSTICO», ambas con el logo GRUPO JR")
QWEN = {  # nombre: (referencias, prompt)
    "V1_barre": (["obrero"], ESTILO + OBRERO + "Inclinado hacia adelante barre con una escoba la losa de concreto, " + LOSA + "Plano medio-cercano, él grande en el cuadro. " + NO),
    "V2_cubetas": (["cubetas", "obrero"], ESTILO + OBRERO + "Está en cuclillas y señala con una mano hacia " + CUB + " puestas a su lado, " + LOSA + "Plano medio, composición como la primera imagen. " + NO),
    "V3_mezcla": (["mezcla", "obrero"], ESTILO + OBRERO + "Está en cuclillas y mezcla con un taladro mezclador rojo el primario café-rojizo dentro de la cubeta blanca que dice «PRIMARIO FIBRATADO ELÁSTICO», " + LOSA + "Plano medio-cercano, composición como la primera imagen. " + NO),
    "V4_primario": (["obrero"], ESTILO + OBRERO + "Aplica con un rodillo grande una capa de primario café-rojizo sobre la losa gris, la cubeta blanca de primario junto a él, " + LOSA + "Plano medio-cercano, él grande en el cuadro. " + NO),
    "V5_poliuretano": (["obrero"], ESTILO + OBRERO + "Aplica con un rodillo grande poliuretano acrílico blanco brillante sobre la losa; la mitad de la losa ya está blanca, " + LOSA + "Plano medio, ligeramente picado. " + NO),
    "V6_terminada": (["obrero"], ESTILO + OBRERO + "Está de pie con las manos en la cintura, orgulloso, mirando a cámara, sobre la losa ya completamente blanca e impermeabilizada, " + LOSA + "Plano entero. " + NO),
    "V7_lluvia": (["obrero"], ESTILO + OBRERO + "Está de pie con los brazos abiertos sobre la losa blanca impermeabilizada mientras llueve; las gotas ruedan sobre la superficie blanca sin filtrarse, " + LOSA.replace("cielo azul", "cielo con nubes de lluvia") + "Plano medio. " + NO),
    "V8_cierre": (["obrero"], ESTILO + OBRERO + "Sonríe a cámara y saluda con una mano, con " + CUB + " a sus pies, losa blanca limpia detrás, " + LOSA + "Plano medio, ligeramente contrapicado. " + NO),
}
H3 = [  # (toma, primer cuadro, último cuadro, seg, prompt)
    ("V1_barre", "V1_barre", None, 5.0, "Vertical animated shot: the cartoon worker in a white hard hat and blue safety vest sweeps the concrete rooftop with a broom, a little dust rises, smooth side dolly. Keep the same character. No text. Audio: soft sweeping sound, no speech."),
    ("V2_cubetas", "V2_cubetas", None, 5.0, "Vertical animated shot: the cartoon worker crouches and points to the two white buckets beside him, then looks at the camera, slow push-in. Keep the same character and the bucket labels. Audio: soft ambient, no speech."),
    ("V3_mezcla", "V3_mezcla", None, 5.0, "Vertical animated shot: the cartoon worker mixes the reddish-brown primer in the white bucket with a red power drill mixer, the liquid swirls, slow push-in. Keep the same character. Audio: soft drill whirring, no speech."),
    ("V4_primario", "V4_primario", None, 5.0, "Vertical animated shot: the cartoon worker rolls reddish-brown primer across the grey slab with a big roller, the coated area grows, slow lateral dolly. Keep the same character. No text. Audio: soft roller sound, no speech."),
    ("V5_poliuretano", "V5_poliuretano", None, 5.0, "Vertical animated shot: the cartoon worker rolls glossy white polyurethane coating across the slab, the white area grows, slow lateral dolly. Keep the same character. No text. Audio: soft roller sound, no speech."),
    ("V6_terminada", "V6_terminada", None, 4.0, "Vertical animated shot: the cartoon worker stands proudly with hands on his hips on the finished white slab and nods, slow camera orbit. Keep the same character. No text. Audio: soft ambient, no speech."),
    ("V7_lluvia", "V7_lluvia", None, 4.0, "Vertical animated shot: rain falls on the fully white waterproofed slab, drops bead up and roll off, the cartoon worker opens his arms happily under the rain, slow camera pull-back. Keep the same character. No text. Audio: soft rain, no speech."),
    ("V8_cierre", "V8_cierre", None, 5.0, "Vertical animated shot: the cartoon worker smiles and waves to the camera, the two labeled buckets at his feet, slow push-in. Keep the same character. Audio: soft ambient, no speech."),
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
        im = pipe(image=[imgs[u] for u in usar], prompt=p, negative_prompt="camión, vehículo, subtítulos, cemento, costales, manguera, cara distinta, deforme, borroso, manos extra, rascacielos, ciudad, Nueva York",
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
    refs = {"obrero": (AQUI / "ref_obrero.png").read_bytes(), "cubetas": (AQUI / "ref_cubetas.png").read_bytes(), "mezcla": (AQUI / "ref_mezcla.png").read_bytes()}
    out = AQUI / "salida"; out.mkdir(exist_ok=True)
    for n, v in todo.remote(refs, semilla).items():
        (out / n).write_bytes(v); print("guardado", n)
