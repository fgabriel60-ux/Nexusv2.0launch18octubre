"""Veneers Dental (Dra. Ángeles) · 4 videos de referencia (carillas, ortodoncia, tomografía, placas) con el mismo pipeline que implantes.
Paso `cuadros`: Qwen-Image-Edit-2511 (720x1280 para la doctora, cfg 4, 40 pasos) → modelos 3D (burbujas y recuadros) de los 4 servicios + doctora cálida (placas).
                UNA sola GPU, UNA función, en serie.
Paso `clips`:   MiniMax H3 fl2va fp8 + LoRA turbo 8 pasos (576x1024) con guía de labios de la voz Fish; UNA sola GPU, todas las tomas en serie.
Uso:  MODAL_PROFILE=fabelagabriel645 modal run servicios_ref_modal.py --paso cuadros [--solo carillas]
      MODAL_PROFILE=fabelagabriel645 modal run servicios_ref_modal.py --paso clips [--solo carillas,placas] [--version r1]"""
import io, json, pathlib, sys
import modal
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/XV")
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/Mariano/flyers_animados")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from flyers_modal import imagen, datos, qwen
from xv_modal import _flujo, _largo, ANCHO, ALTO, CARPETA
from servicios_ref_cfg import SERVICIOS

app = modal.App("alberto-servicios-ref", image=imagen.add_local_python_source("flyers_modal", "xv_modal", "servicios_ref_cfg"))
AQUI = pathlib.Path(__file__).resolve().parent
CUADROS = AQUI / "servicios_ref" / "cuadros"
ESTILO = ("Render 3D médico hiperrealista estilo ilustración de clínica dental premium (como los modelos dentales de redes sociales), "
          "materiales brillantes, iluminación de estudio suave, fondo liso degradado gris azulado oscuro, objeto centrado y completo, sin texto, sin letras, sin marcas de agua.")
NEG_M = "texto, letras, marca de agua, personas, manos, boca humana, labios, cara, deforme, sangre"
NEG_P = "cara distinta, otra persona, más joven, sin lentes, manos deformes, dedos extra, texto, letras, logotipo, borroso, caricatura"
CALIDO = ("Conserva EXACTAMENTE esta foto: la misma mujer, misma cara, mismo cabello, lentes, ropa, pose, manos y encuadre. Solo cambia el ambiente del consultorio: "
          "ahora es cálido y acogedor, paredes color crema y beige claro con luz ámbar cálida, la lámpara dental es blanca con luz cálida suave, "
          "iluminación dorada suave en su cara, sin luces azules ni rojas. Foto realista nítida, manos naturales, sin texto.")
H3_FIN = (" She speaks directly to the camera with natural lip movement exactly matching the speech, small natural head movements, calm hand gestures, warm professional expression. "
          "Keep her face, glasses, blonde hair, red lips, black scrubs and the clinic exactly as in the first frame. Static camera. Realistic. No text, no question marks, no symbols, no stickers, no emoji, nothing floating around her. "
          "Audio: clear female voice speaking Spanish.")
GESTOS = ["she greets the viewer with a warm smile and a small friendly nod.", "she explains with one open hand at chest height.",
          "she explains with both hands, calm and clear.", "she reassures the viewer with a calm smile and a small nod.",
          "she invites the viewer with a warm smile and an open hand."]


@app.function(gpu="A100-80GB", volumes={"/qwen": qwen}, timeout=7200)
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


def _png(ruta, caja=None):
    from PIL import Image, ImageOps
    im = Image.open(ruta).convert("RGB")
    if caja: im = ImageOps.fit(im, caja, Image.LANCZOS, centering=(.5, .4))
    b = io.BytesIO(); im.save(b, "PNG"); return b.getvalue()


@app.local_entrypoint()
def main(paso: str = "cuadros", solo: str = "", semilla: int = 3, version: str = "r1", tomas_solo: str = "", sem_clip: int = 2):
    ts = [x for x in tomas_solo.split(",") if x]
    sel = [x for x in solo.split(",") if x]
    CUADROS.mkdir(parents=True, exist_ok=True)
    if paso == "cuadros":
        from PIL import Image
        lisa = io.BytesIO(); Image.new("RGB", (1024, 1024), (38, 44, 58)).save(lisa, "PNG")
        tr = []
        for srv, c in SERVICIOS.items():
            if sel and srv not in sel: continue
            for n, (w, h, p) in c["modelos"].items():
                tr.append((f"{srv}_{n}", [lisa.getvalue()], p + " " + ESTILO, NEG_M, w, h, semilla))
            if srv == "placas":
                for n in ("P1", "P2"):
                    tr.append((f"{n}w", [_png(CUADROS / f"{n}a_r1.png")], CALIDO, NEG_P, 720, 1280, semilla))
        for n, v in cuadros.remote(tr).items():
            (CUADROS / f"{n}_{version}.png").write_bytes(v); print("guardado", n)
    else:
        fotos, voces, tomas = {}, {}, []
        for srv, c in SERVICIOS.items():
            if sel and srv not in sel: continue
            calido = srv == "placas"
            for i, (n, (_, _, _, cuadro)) in enumerate(c["tomas"].items()):
                if ts and n not in ts: continue
                if calido: cuadro = cuadro.replace("a_r1", "w_r1")
                fotos[cuadro] = _png(CUADROS / f"{cuadro}.png", (ANCHO, ALTO))
                voces[n] = (AQUI / "voz" / f"{n}.wav").read_bytes()
                seg = len(voces[n]) / 32000
                pr = ("Vertical medium shot of a female dentist seated in a " + ("warm cream-colored dental clinic, " if calido else "dark blue dental clinic, ")
                      + GESTOS[i % len(GESTOS)] + H3_FIN)
                tomas.append((f"{n}_{version}", cuadro, n, pr, seg))
        out = AQUI / "servicios_ref" / "tomas"; out.mkdir(parents=True, exist_ok=True)
        for n, v in clips.remote(fotos, voces, tomas, sem_clip).items():
            (out / f"{n}.mp4").write_bytes(v); print("guardado", n)
