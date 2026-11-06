"""Ganchos en UNA sola GPU, sin teléfono volando: la persona habla frente a SU lugar real y la cámara sube como dron hasta la vista aérea.
(1) Lisbeth v3: a la orilla de la carretera frente a su terreno real (su foto de calle del 24 oct) → sube hasta SU foto aérea real → la construcción
aparece sobre ese mismo terreno (visualización, se rotula así en el armado). (2) Mariano: frente a las casas reales de Vizcaíno (su video del 22 oct) →
sube hasta la vista aérea del conjunto. Qwen primero, luego H3. Uso: modal run ganchos_lisbeth_mariano_modal.py"""
import io, json, pathlib, sys
import modal
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/XV")
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/Mariano/flyers_animados")
from flyers_modal import imagen, datos, qwen
from xv_modal import _flujo, _largo, ANCHO, ALTO, CARPETA

app = modal.App("ganchos-lisbeth-mariano", image=imagen.add_local_python_source("flyers_modal", "xv_modal"))
AQUI = pathlib.Path(__file__).resolve().parent
SIN = " Foto vertical 9:16, realista, nítida, sin texto, sin letras, sin celulares."
CARA = "Conserva EXACTAMENTE la cara de esta persona: mismos ojos, cejas, nariz, boca, edad, tono de piel y cabello. "
QWEN = {  # nombre: (referencias, prompt)
    "L3_calle": (["lisbeth", "calle"], CARA + "Ella está de pie a la orilla de ESTA misma carretera, frente a ESTE mismo terreno (el mismo asfalto con línea amarilla, el mismo pasto, "
                 "los mismos árboles secos y la misma loma al fondo, cielo azul), plano medio de la cintura para arriba, mirando a cámara con sonrisa segura, "
                 "blusa negra, cabello oscuro recogido, las manos sueltas, luz de día." + SIN),
    "L3_aereo": (["aereo"], "Convierte esta foto aérea de dron en vertical 9:16 completando arriba y abajo, SIN cambiar nada: el mismo terreno, la misma loma, "
                 "la misma carretera curva y la misma vegetación." + SIN),
    "L3_construido": (["aereo"], "La MISMA vista aérea de dron, mismo encuadre, misma loma y misma carretera curva, pero ahora sobre el terreno hay lotes trazados con "
                      "calles de terracería y varias casas modernas de una y dos plantas ya construidas, con árboles y jardines. Vertical 9:16 completando arriba y abajo." + SIN),
    "M2_calle": (["mariano", "vizcaino"], CARA + "Él está de pie en la calle frente a ESTAS mismas casas (la misma fila de casas de dos pisos color arena con ventanas "
                 "verticales, el mismo cielo nublado), plano medio de la cintura para arriba, mirando a cámara con sonrisa segura, saco azul claro y camisa blanca, "
                 "luz de día." + SIN),
    "M2_aereo": (["vizcaino"], "Vista aérea de dron desde arriba de ESTE mismo conjunto residencial: la misma fila de casas de dos pisos color arena con sus techos planos, "
                 "la misma calle amplia de concreto, el mismo cielo nublado, se ven las demás casas del fraccionamiento alrededor. Vertical 9:16." + SIN),
}
H3 = [  # (toma, primer cuadro, último cuadro, voz, segundos, prompt)
    ("LIS3_habla", "L3_calle", None, "L_gancho", 4.52, "Vertical shot: the woman stands by the roadside in front of the dry hillside land and speaks to the camera with natural lip movement "
     "matching the speech, warm confident smile, small natural hand gestures, a light breeze moves the trees. Camera is static, held at chest height. Keep her face exactly. "
     "No phone, no text. Audio: clear female voice speaking Spanish."),
    ("LIS3_sube", "L3_calle", "L3_aereo", None, 4.0, "Continuous single drone shot, no cut: the camera rises smoothly and fast from the roadside, tilting down, flying up and over "
     "the land until it settles into the stable top-down aerial view of the same hill, land and curving road. The woman stays on the ground and gets small below. "
     "No phone, no text. Audio: soft wind whoosh, no speech."),
    ("LIS3_construye", "L3_aereo", "L3_construido", None, 4.0, "Static aerial drone shot, time-lapse: on the same land, dirt streets get traced and modern houses rise "
     "one by one with gardens, smooth and realistic, the hill and the curving road stay exactly the same. No text. Audio: soft construction time-lapse ambience, no speech."),
    ("MAR2_habla", "M2_calle", None, "M_gancho", 7.68, "Vertical shot: the man stands on the street in front of the row of two-story houses and speaks to the camera with natural lip "
     "movement matching the speech, confident friendly smile, small natural hand gestures toward the houses. Camera is static, chest height. Keep his face exactly. "
     "No phone, no text. Audio: clear male voice speaking Spanish."),
    ("MAR2_sube", "M2_calle", "M2_aereo", None, 4.0, "Continuous single drone shot, no cut: the camera rises smoothly and fast from the street, tilting down, flying up over the "
     "row of houses until it settles into the stable aerial view of the whole residential complex. The man stays on the street and gets small below. "
     "No phone, no text. Audio: soft wind whoosh, no speech."),
]


@app.function(gpu="A100-80GB", volumes={"/datos": datos, "/qwen": qwen}, timeout=7200)
def todo(refs: dict, voces: dict, semilla: int = 4) -> dict:
    import gc, glob, os, subprocess, time, requests, torch
    from PIL import Image
    from diffusers import QwenImageEditPlusPipeline
    carpeta = f"/datos/siena/{CARPETA}"
    os.makedirs(carpeta, exist_ok=True)
    for n, v in voces.items():
        open(f"{carpeta}/{n}.wav", "wb").write(v)
    imgs = {k: Image.open(io.BytesIO(v)).convert("RGB") for k, v in refs.items()}
    pipe = QwenImageEditPlusPipeline.from_pretrained("/qwen/Qwen-Image-Edit-2511", torch_dtype=torch.bfloat16).to("cuda")
    salida = {}
    for n, (usar, p) in QWEN.items():
        im = pipe(image=[imgs[u] for u in usar], prompt=p, negative_prompt="texto, letras, subtítulos, celular, teléfono, cara distinta, deforme, borroso, manos extra, dedos extra",
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
    for n, ini, fin, voz, seg, prompt in H3:
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
def main(semilla: int = 4):
    nuevas = AQUI / "Lisbeth/whatsapp/nuevas_1024"
    refs = {"lisbeth": (AQUI / "Lisbeth/whatsapp/del_cliente/20261022_161302_image.jpg").read_bytes(),
            "calle": (nuevas / "24_130407_image.jpg").read_bytes(), "aereo": (nuevas / "24_130408_image.jpg").read_bytes(),
            "mariano": (AQUI / "Mariano/fotos/mariano_luz_final.png").read_bytes(), "vizcaino": (AQUI / "Mariano/video/gancho_v2/vizcaino_calle.jpg").read_bytes()}
    voces = {"L_gancho": (AQUI / "Lisbeth/video/voz/L_gancho.wav").read_bytes(), "M_gancho": (AQUI / "Mariano/video/gancho_v2/M_gancho.wav").read_bytes()}
    for n, v in todo.remote(refs, voces, semilla).items():
        destino = AQUI / ("Lisbeth/video/v3" if n.startswith("L") else "Mariano/video/gancho_v2"); destino.mkdir(parents=True, exist_ok=True)
        (destino / n).write_bytes(v); print("guardado", n)
