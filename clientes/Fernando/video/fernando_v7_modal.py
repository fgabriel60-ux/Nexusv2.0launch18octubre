"""Fernando (Anegocios) v7: escenas de Fernando generadas en Modal (formato del reel DasdFyGlBeq: dueño a cámara en su mostrador).
Paso `cuadros`: Qwen-Image-Edit-2511 (720x1280, cfg 4, 40 pasos) desde SUS fotos reales (fotograma del taller + foto del escritorio + fotos del kit) -> 4 cuadros.
Paso `clips`: MiniMax H3 fl2va (576x1024) con lip-sync por la voz clonada de Fernando (Fish 6e856af2...). Una sola GPU por paso.
Uso: MODAL_PROFILE=fabelagabriel645 modal run fernando_v7_modal.py --paso cuadros [--solo F1] [--version r1]
     MODAL_PROFILE=fabelagabriel645 modal run fernando_v7_modal.py --paso clips [--base F1=F1_r1,...] [--version r1]"""
import io, json, pathlib, sys
import modal
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/XV")
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/Mariano/flyers_animados")
from flyers_modal import imagen, datos, qwen
from xv_modal import _flujo, _largo, ANCHO, ALTO, CARPETA

app = modal.App("fernando-v7", image=imagen.add_local_python_source("flyers_modal", "xv_modal"))
AQUI = pathlib.Path(__file__).resolve().parent / "v7_modal"
CL = pathlib.Path(__file__).resolve().parent.parent / "whatsapp" / "del_cliente"

IDENT = ("Conserva EXACTAMENTE la identidad del hombre de la primera foto: la misma cara, mismos lentes de armazón, barba corta canosa, cabello canoso corto, "
         "tono de piel, edad y complexión. Viste una playera blanca lisa. ")
FIN = "Foto vertical 9:16 hiperrealista tipo vlog, nítida, manos con cinco dedos naturales, sin texto, sin letras, sin logotipos."
LUGAR = ("Cambia el fondo: ahora está de pie DETRÁS del mostrador de una tienda de abarrotes mexicana pequeña y luminosa, anaqueles con productos borrosos al fondo, "
         "luz cálida de tienda. En el mostrador hay una computadora con pantalla encendida, una impresora térmica de tickets negra con azul y un lector de códigos de barras. ")
NEG = "cara distinta, otra persona, sin lentes, manos deformes, dedos extra, texto, letras, logotipo, borroso, caricatura, pantalla con texto legible"
# nombre: (fotos de referencia [primera = Fernando], prompt)
CUADROS = {
    "F1": (["ref_taller.png", "image_07_10-20_1842.jpg"], IDENT + LUGAR + "Sostiene el lector de códigos de barras de la segunda foto y lo acerca a un producto sobre el mostrador, como escaneándolo, mirando a la cámara con sonrisa amable. Plano medio de cabeza a cintura. " + FIN),
    "F2": (["ref_taller.png", "doc_06.png"], IDENT + LUGAR + "Con una mano señala la pantalla de la computadora del mostrador, que está a su lado, mientras mira a la cámara. Plano medio de cabeza a cintura. " + FIN),
    "F3": (["ref_taller.png", "image_03_10-20_1842.jpg"], IDENT + LUGAR + "Está de frente a la cámara detrás del mostrador, con la impresora térmica de la segunda foto junto a él imprimiendo un ticket de papel blanco, con una mano abierta explicando. Plano medio de cabeza a cintura. " + FIN),
    "F4": (["ref_taller.png"], IDENT + LUGAR + "Habla de frente a la cámara con las manos relajadas, plano medio tipo vlog, expresión segura y amable. " + FIN),
}
H3_FIN = (" He speaks directly to the camera with natural lip movement exactly matching the speech, small natural head movements, calm hand gestures, friendly expression. "
          "Keep his face, glasses, beard, white t-shirt and the shop exactly as in the first frame. Very slow gentle push-in. Realistic. No text. Audio: clear male voice speaking Spanish.")
TOMAS = {
    "T1": ("F1", "v7_1", "Vertical medium shot of a man behind a small Mexican grocery store counter holding a barcode scanner, talking to the camera." + H3_FIN),
    "T2": ("F2", "v7_2", "Vertical medium shot of a man behind a store counter pointing at the computer screen beside him while talking to the camera." + H3_FIN),
    "T3": ("F3", "v7_3", "Vertical medium shot of a man behind a store counter next to a thermal ticket printer, explaining to the camera with one open hand." + H3_FIN),
    "T4": ("F4", "v7_4", "Vertical medium shot of a man behind a store counter talking to the camera like a vlog, reassuring and friendly." + H3_FIN),
}


@app.function(gpu="A100-80GB", volumes={"/qwen": qwen}, timeout=3600)
def cuadros(trabajos: list) -> dict:
    """trabajos: [(nombre, [png de referencia], prompt, negativo, ancho, alto, semilla)]"""
    import torch
    from PIL import Image
    from diffusers import QwenImageEditPlusPipeline
    pipe = QwenImageEditPlusPipeline.from_pretrained("/qwen/Qwen-Image-Edit-2511", torch_dtype=torch.bfloat16).to("cuda")
    out = {}
    for n, refs, p, neg, w, h, s in trabajos:
        ims = [Image.open(io.BytesIO(r)).convert("RGB") for r in refs]
        im = pipe(image=ims, prompt=p, negative_prompt=neg, true_cfg_scale=4.0, guidance_scale=1.0, num_inference_steps=40,
                  height=h, width=w, generator=torch.Generator("cuda").manual_seed(s)).images[0]
        b = io.BytesIO(); im.save(b, "PNG"); out[n] = b.getvalue(); print("cuadro", n, flush=True)
    return out


@app.function(gpu="A100-80GB", volumes={"/datos": datos}, timeout=7200)
def clips(fotos: dict, voces: dict, tomas: list, semilla: int = 2) -> dict:
    """tomas: [(nombre, cuadro, voz, prompt, segundos)]"""
    import glob, os, subprocess, time, requests
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
    for n, cuadro, voz, prompt, seg in tomas:
        r = requests.post("http://127.0.0.1:8188/prompt", json={"prompt": _flujo(cuadro, None, voz, prompt, n, semilla, _largo(seg))}).json()
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


def _png(ruta):
    from PIL import Image, ImageOps
    im = ImageOps.exif_transpose(Image.open(ruta)).convert("RGB")
    b = io.BytesIO(); im.save(b, "PNG"); return b.getvalue()


def _png_fit(ruta, caja):
    from PIL import Image, ImageOps
    im = ImageOps.fit(ImageOps.exif_transpose(Image.open(ruta)).convert("RGB"), caja, Image.LANCZOS, centering=(.5, .4))
    b = io.BytesIO(); im.save(b, "PNG"); return b.getvalue()


def _ruta(n):
    return AQUI / "cuadros" / n if (AQUI / "cuadros" / n).exists() else CL / n


@app.local_entrypoint()
def main(paso: str = "cuadros", solo: str = "", semilla: int = 5, version: str = "r1", base: str = ""):
    sel = [x for x in solo.split(",") if x]
    if paso == "cuadros":
        tr = [(n, [_png(_ruta(f)) for f in fotos], p, NEG, 720, 1280, semilla + i) for i, (n, (fotos, p)) in enumerate(CUADROS.items()) if not sel or n in sel]
        for n, v in cuadros.remote(tr).items():
            (AQUI / "cuadros" / f"{n}_{version}.png").write_bytes(v); print("guardado", n)
    else:
        elegido = dict(x.split("=") for x in base.split(",") if x)
        fotos, voces, tomas = {}, {}, []
        for n, (cuadro, voz, prompt) in TOMAS.items():
            if sel and n not in sel: continue
            c = elegido.get(cuadro, f"{cuadro}_r1"); c_id = "fer_" + c
            fotos[c_id] = _png_fit(AQUI / "cuadros" / f"{c}.png", (ANCHO, ALTO))
            voces["fer_" + voz] = (AQUI / "voz" / f"{voz}.wav").read_bytes()
            tomas.append((f"fer_{n}_{version}", c_id, "fer_" + voz, prompt, len(voces["fer_" + voz]) / 32000))
        for n, v in clips.remote(fotos, voces, tomas, 2).items():
            (AQUI / "tomas" / f"{n}.mp4").write_bytes(v); print("guardado", n)
