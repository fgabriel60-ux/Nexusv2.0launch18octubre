"""Veneers Dental (Dra. Ángeles) · reel de IMPLANTES con el lenguaje visual del reel dental de referencia
(dentista sentado a cámara en consultorio azul oscuro, modelos 3D de dientes/hueso/implante, subtítulos con palabra clave en color).

Paso `cuadros`: Qwen-Image-Edit-2511 (720×1280, cfg 4, 40 pasos) a partir de SUS fotos reales → la doctora sentada en un consultorio azul;
               y modelos 3D (dientes sanos, hueco, hueso que se pierde, implante en el hueso, implante con corona, anestesia) sobre fondo liso oscuro.
Paso `clips`:  MiniMax H3 fl2va fp8 + LoRA turbo 8 pasos (576×1024) con MiniMaxH3AddGuide = labios guiados por la voz Fish de cada idea.
Una sola GPU A100-80GB por paso, sin starmap.
Uso:  MODAL_PROFILE=fabelagabriel645 modal run implantes_ref_modal.py --paso cuadros [--solo P1a,M3] [--semilla 7]
      MODAL_PROFILE=fabelagabriel645 modal run implantes_ref_modal.py --paso clips [--solo S2] [--version r1]"""
import io, json, pathlib, sys
import modal
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/XV")
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/Mariano/flyers_animados")
from flyers_modal import imagen, datos, qwen
from xv_modal import _flujo, _largo, ANCHO, ALTO, CARPETA

app = modal.App("alberto-implantes-ref", image=imagen.add_local_python_source("flyers_modal", "xv_modal"))
AQUI = pathlib.Path(__file__).resolve().parent
FOTOS = AQUI.parent / "whatsapp" / "del_cliente"
CUADROS = AQUI / "implantes_ref" / "cuadros"

IDENT = ("Conserva EXACTAMENTE la identidad de esta mujer de la foto: la misma cara, la misma forma de ojos, nariz, boca y mentón, el mismo tono de piel, "
         "la misma edad, sus lentes negros de pasta cuadrados, su cabello rubio lacio con raya en medio a la altura de los hombros, labios rojos, "
         "collar negro corto y uniforme quirúrgico negro de manga larga. ")
ESCENA = ("Cambia el fondo: ahora está en un consultorio dental moderno y oscuro, paredes azul marino con luz LED azul intensa, "
          "detrás de ella la lámpara dental redonda con focos y el brazo blanco del sillón dental, luz suave de estudio en su cara, ambiente cinematográfico azul. ")
FIN = "Foto vertical 9:16 hiperrealista, nítida, manos con cinco dedos naturales, sin texto, sin letras, sin logotipos."
NEG_P = "cara distinta, otra persona, más joven, sin lentes, manos deformes, dedos extra, texto, letras, logotipo, borroso, caricatura"
PERSONA = {   # nombre: (fotos de referencia, prompt)
    "P1": (["doctora_1"], IDENT + ESCENA + "Está sentada de frente a la cámara en un banquito, plano medio de la cabeza a las rodillas, con las manos relajadas juntas sobre las piernas, "
           "sonrisa cálida, mirando a la cámara. Su cabeza queda en el tercio superior de la imagen y hay espacio libre de pared azul arriba de su cabeza. " + FIN),
    "P2": (["doctora_1"], IDENT + ESCENA + "Plano medio corto: de la cabeza a la cintura, sentada de frente a la cámara, explicando con una mano abierta a la altura del pecho, "
           "expresión amable y segura, mirando a la cámara. Hay espacio libre de pared azul arriba de su cabeza. " + FIN),
}
ESTILO = ("Render 3D médico hiperrealista estilo ilustración de clínica dental premium (como los modelos dentales de redes sociales), "
          "materiales brillantes, iluminación de estudio suave, fondo liso degradado gris azulado oscuro, objeto centrado y completo, sin texto, sin letras, sin marcas de agua.")
NEG_M = "texto, letras, marca de agua, personas, manos, boca humana, labios, cara, deforme, dientes amarillos podridos, sangre"
MODELOS = {   # nombre: (ancho, alto, prompt)
    "M1": (1024, 1024, "Vista frontal de una arcada de dientes blancos sanos y alineados con encía rosa sana y completa, sin huecos. " + ESTILO),
    "M2": (1024, 1024, "Vista frontal de cerca de una dentadura en mordida cerrada, dientes blancos y encía rosa; en la arcada superior FALTA UN SOLO DIENTE "
           "(el primer premolar del lado derecho): hay un espacio vacío oscuro entre dos dientes donde solo se ve la encía lisa. Todos los demás dientes completos. " + ESTILO),
    "M3": (1152, 768, "Corte transversal lateral de la mandíbula: dos dientes naturales con sus raíces dentro del hueso esponjoso color marfil y la encía rosa encima; "
           "en medio FALTA un diente y el hueso de ese hueco está hundido en forma de U, más bajo y delgado (hueso que se pierde), y los dos dientes de los lados "
           "están ligeramente inclinados hacia el hueco. La encía rosa cubre el hueso. " + ESTILO),
    "M4": (1152, 768, "Corte transversal lateral de la mandíbula: a la izquierda y a la derecha un diente natural blanco completo con su corona y su raíz dentro del hueso; "
           "en medio, UN SOLO implante dental de titanio plateado (tornillo con roscas) enterrado verticalmente dentro del hueso esponjoso color marfil, como una raíz nueva; "
           "la encía rosa cubre el hueso y solo asoma la cabeza del implante, todavía sin corona. " + ESTILO),
    "M5": (1024, 1024, "Un implante dental completo flotando: tornillo de titanio plateado con roscas abajo, pilar metálico en medio y una corona de diente blanca y brillante arriba, vista lateral. " + ESTILO),
    "M6": (1024, 1024, "Una jeringa dental de anestesia de acero inoxidable con su cartucho de vidrio, elegante y limpia, en diagonal. " + ESTILO),
}
H3_FIN = (" She speaks directly to the camera with natural lip movement exactly matching the speech, small natural head movements, calm hand gestures, warm professional expression. "
          "Keep her face, glasses, blonde hair, red lips, black scrubs and the dark blue dental clinic exactly as in the first frame. Static camera. Realistic. No text. "
          "Audio: clear female voice speaking Spanish.")
TOMAS = {   # toma: (cuadro inicial, voz, prompt)
    "S1": ("P1", "ref_S1", "Vertical medium shot of a female dentist seated in a dark blue dental clinic, she raises one index finger while asking a question to the camera." + H3_FIN),
    "S2": ("P2", "ref_S2", "Vertical medium close shot of a female dentist explaining something serious to the camera with one open hand." + H3_FIN),
    "S3": ("P1", "ref_S3", "Vertical medium shot of a female dentist seated in a dark blue dental clinic, explaining with both hands to the camera." + H3_FIN),
    "S4": ("P2", "ref_S4", "Vertical medium close shot of a female dentist reassuring the viewer with a calm smile." + H3_FIN),
    "S5": ("P1", "ref_S5", "Vertical medium shot of a female dentist seated in a dark blue dental clinic, inviting the viewer with a warm smile and an open hand." + H3_FIN),
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


def _png(ruta, caja=None):
    from PIL import Image, ImageOps
    im = ImageOps.exif_transpose(Image.open(ruta)).convert("RGB")
    if caja: im = ImageOps.fit(im, caja, Image.LANCZOS, centering=(.5, .4))
    b = io.BytesIO(); im.save(b, "PNG"); return b.getvalue()


@app.local_entrypoint()
def main(paso: str = "cuadros", solo: str = "", semilla: int = 3, version: str = "r1", base: str = ""):
    sel = [x for x in solo.split(",") if x]
    CUADROS.mkdir(parents=True, exist_ok=True)
    if paso == "retoque":
        # ronda 2: misma imagen ya aprobada (identidad), solo la luz de la lámpara pasa de roja a blanca y se quita el reflejo rosa del pelo
        RET = ("Conserva EXACTAMENTE esta foto: la misma mujer, misma cara, misma pose, mismas manos, mismo encuadre y mismo consultorio azul. "
               "Solo cambia la luz de la lámpara dental: ahora es una lámpara dental blanca con luz blanca fría, sin luz roja; "
               "quita el reflejo rosa o rojo de la parte de arriba de su cabello, que se vea rubio natural parejo. Foto realista nítida, sin texto.")
        tr = [(f"{n}w", [_png(CUADROS / f"{n}a_r1.png")], RET, NEG_P, 720, 1280, semilla) for n in ("P1", "P2")]
        for n, v in cuadros.remote(tr).items():
            (CUADROS / f"{n}_{version}.png").write_bytes(v); print("guardado", n)
        return
    if paso == "cuadros":
        tr = []
        for n, (fotos, p) in PERSONA.items():
            for k, s in (("a", semilla), ("b", semilla + 10)):
                if sel and n not in sel and f"{n}{k}" not in sel: continue
                tr.append((f"{n}{k}", [_png(FOTOS / f"{f}.jpg") for f in fotos], p, NEG_P, 720, 1280, s))
        lisa = io.BytesIO()
        from PIL import Image
        Image.new("RGB", (1024, 1024), (38, 44, 58)).save(lisa, "PNG")
        for n, (w, h, p) in MODELOS.items():
            if sel and n not in sel: continue
            for k, s in ((("a", semilla), ("b", semilla + 10)) if sel else (("", semilla),)):
                tr.append((f"{n}{k}", [lisa.getvalue()], p, NEG_M, w, h, s))
        for n, v in cuadros.remote(tr).items():
            (CUADROS / f"{n}_{version}.png").write_bytes(v); print("guardado", n)
    else:
        # base: «S1=P1a_r1,S2=P2b_r1,...» cuadro elegido por toma (por defecto P1a_r1 / P2a_r1)
        elegido = dict(x.split("=") for x in base.split(",") if x)
        fotos, voces, tomas = {}, {}, []
        for n, (cuadro, voz, prompt) in TOMAS.items():
            if sel and n not in sel: continue
            c = elegido.get(n, f"{cuadro}a_r1")
            fotos[c] = _png(CUADROS / f"{c}.png", (ANCHO, ALTO))
            voces[voz] = (AQUI / "voz" / f"{voz}.wav").read_bytes()
            seg = len(voces[voz]) / 32000
            tomas.append((f"{n}_{version}", c, voz, prompt, seg))
        out = AQUI / "implantes_ref" / "tomas"; out.mkdir(parents=True, exist_ok=True)
        for n, v in clips.remote(fotos, voces, tomas, semilla).items():
            (out / f"{n}.mp4").write_bytes(v); print("guardado", n)
