"""Escenas de clientes hechas a mano (30 oct): reemplaza al productor automático, que Carlos rechazó por mala calidad.
Paso 1 «cuadros»: Qwen-Image-Edit-2511 a 720x1280 con las fotos de referencia RECORTADAS (no estiradas) → PNGs para revisar contra la referencia del cliente.
Paso 2 «animar»: MiniMax H3 a 704x1280 solo con los cuadros aprobados (recortados, no estirados); voz opcional para lipsync.
spec JSON: {"carpeta", "salida", "semilla", "refs": {n: ruta}, "cuadros": {n: [[refs], prompt, negativo_extra]}, "tomas": [[n, png, prompt, seg, voz|null]], "voces": {n: ruta}}
  GASTO_PERFIL=charlyfavela666 python3 gasto_modal.py run clientes/_escenas_carlos/escenas_carlos_modal.py::cuadros --spec X.json
  GASTO_PERFIL=charlyfavela666 python3 gasto_modal.py run clientes/_escenas_carlos/escenas_carlos_modal.py::animar --spec X.json"""
import io, json, os, pathlib, sys
import modal

sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/XV")
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/Mariano/flyers_animados")
from flyers_modal import imagen, datos, qwen
import xv_modal

app = modal.App("escenas-carlos", image=imagen.add_local_python_source("flyers_modal", "xv_modal"))
RAIZ = pathlib.Path("/workspaces/Nexusv2.0launch18octubre")
NEG = "texto, letras, subtítulos, logotipos inventados, marca de agua, cara distinta, deforme, borroso, manos extra, dedos extra, caricatura, ilustración, render 3D, imagen estirada"


def _fit(b, w, h):
    from PIL import Image, ImageOps
    return ImageOps.fit(Image.open(io.BytesIO(b)).convert("RGB"), (w, h), Image.LANCZOS, centering=(0.5, 0.45))


@app.function(gpu="A100-80GB", volumes={"/qwen": qwen}, timeout=3600)
def gen_cuadros(refs: dict, cuadros: dict, semilla: int, ancho: int = 720, alto: int = 1280, pasos: int = 28) -> dict:
    import torch
    from diffusers import QwenImageEditPlusPipeline
    imgs = {k: _fit(v, ancho, alto) for k, v in refs.items()}
    pipe = QwenImageEditPlusPipeline.from_pretrained("/qwen/Qwen-Image-Edit-2511", torch_dtype=torch.bfloat16).to("cuda")
    out = {}
    for n, (usar, p, *neg) in cuadros.items():
        im = pipe(image=[imgs[u] for u in usar], prompt=p, negative_prompt=NEG + (", " + neg[0] if neg else ""), true_cfg_scale=4.0, guidance_scale=1.0,
                  num_inference_steps=pasos, height=alto, width=ancho, generator=torch.Generator("cuda").manual_seed(semilla)).images[0]
        b = io.BytesIO(); im.save(b, "PNG"); out[f"{n}.png"] = b.getvalue(); print("cuadro", n, flush=True)
    return out


@app.cls(gpu="A100-80GB", volumes={"/qwen": qwen}, timeout=3600,
         scaledown_window=240, max_containers=8)
class Cuadros:
    """Un cuadro por llamada, con Qwen YA CARGADO (3 nov 2026).

    Antes `gen_cuadros` cargaba el modelo (1-2 min de A100) y luego hacía los
    cuadros uno tras otro en el mismo contenedor. Aquí `@modal.enter()` carga el
    modelo una sola vez por contenedor y `cuadros_par` reparte los cuadros entre
    varios con `.map()`, así que salen en paralelo.

    El canje: en paralelo se paga una carga por contenedor, no una sola. Gana
    tiempo, no dinero, salvo que un mismo contenedor alcance a hacer varios
    cuadros (por eso scaledown_window=240: se queda caliente un rato).
    """

    @modal.enter()
    def cargar(self):
        import torch
        from diffusers import QwenImageEditPlusPipeline
        self.torch = torch
        self.pipe = QwenImageEditPlusPipeline.from_pretrained(
            "/qwen/Qwen-Image-Edit-2511", torch_dtype=torch.bfloat16).to("cuda")
        print("modelo cargado", flush=True)

    @modal.method()
    def uno(self, trabajo: tuple) -> tuple:
        n, refs, usar, p, neg, semilla, ancho, alto, pasos = trabajo
        imgs = {k: _fit(v, ancho, alto) for k, v in refs.items()}
        im = self.pipe(image=[imgs[u] for u in usar], prompt=p,
                       negative_prompt=NEG + (", " + neg if neg else ""),
                       true_cfg_scale=4.0, guidance_scale=1.0, num_inference_steps=pasos,
                       height=alto, width=ancho,
                       generator=self.torch.Generator("cuda").manual_seed(semilla)).images[0]
        b = io.BytesIO(); im.save(b, "PNG"); print("cuadro", n, flush=True)
        return f"{n}.png", b.getvalue()


@app.function(gpu=os.environ.get("GPU_H3", "L40S"), volumes={"/datos": datos}, timeout=7200)  # GPU_H3=L40S para ahorrar
def gen_tomas(carpeta: str, pngs: dict, tomas: list, voces: dict, semilla: int) -> dict:
    import glob, os, subprocess, time, requests
    xv_modal.CARPETA = carpeta; xv_modal.ANCHO, xv_modal.ALTO = 704, 1280
    base = f"/datos/siena/{carpeta}"; os.makedirs(base, exist_ok=True)
    for n, b in pngs.items(): _fit(b, 704, 1280).save(f"{base}/{n}.png")
    for n, b in (voces or {}).items(): open(f"{base}/{n}.wav", "wb").write(b)
    open("/opt/ComfyUI/extra_model_paths.yaml", "w").write("datos:\n  base_path: /datos/models\n  diffusion_models: diffusion_models\n  loras: loras\n  text_encoders: text_encoders\n  vae: vae\n")
    log = open(f"/tmp/comfy.log", "w")
    subprocess.Popen(["python", "main.py", "--listen", "127.0.0.1", "--port", "8188", "--input-directory", "/datos/siena", "--output-directory", "/datos/siena/out"], cwd="/opt/ComfyUI", stdout=log, stderr=subprocess.STDOUT)
    for _ in range(300):
        try: requests.get("http://127.0.0.1:8188/system_stats", timeout=2); break
        except Exception: time.sleep(2)
    out = {}
    for t in tomas:   # [nombre, png inicial, prompt, seg, voz|None, png final opcional]
        n, png, prompt, seg, voz = t[:5]; fin = t[5] if len(t) > 5 else None
        r = requests.post("http://127.0.0.1:8188/prompt", json={"prompt": xv_modal._flujo(png, fin, voz, prompt, n, semilla, _largo_corto(seg))}).json()
        if "prompt_id" not in r: raise RuntimeError(json.dumps(r)[:3000])
        pid = r["prompt_id"]
        while True:
            h = requests.get(f"http://127.0.0.1:8188/history/{pid}").json()
            if pid in h:
                if h[pid].get("status", {}).get("status_str") == "error": raise RuntimeError(json.dumps(h[pid]["status"])[:3000])
                break
            time.sleep(5)
        out[f"{n}.mp4"] = open(sorted(glob.glob(f"/datos/siena/out/{carpeta}/{n}_*.mp4"), key=os.path.getmtime)[-1], "rb").read(); print("toma", n, flush=True)
    datos.commit()
    return out


def _largo_corto(seg):  # ahorro (31 oct): largo real de la toma, mínimo 73 cuadros (~3 s) en vez de 124
    import math
    n = max(73, math.ceil(seg * 24)); return min(362, n + (5 - n % 17) % 17)


def _leer(p): return (pathlib.Path(p) if p.startswith("/") else RAIZ / p).read_bytes()


def _salida(s):
    o = pathlib.Path(s["salida"]) if s["salida"].startswith("/") else RAIZ / s["salida"]; o.mkdir(parents=True, exist_ok=True); return o


@app.local_entrypoint()
def cuadros(spec: str):
    s = json.load(open(spec)); o = _salida(s)
    for n, v in gen_cuadros.remote({k: _leer(v) for k, v in s["refs"].items()}, s["cuadros"], s.get("semilla", 21), s.get("ancho", 720), s.get("alto", 1280), s.get("pasos", 28)).items():
        (o / n).write_bytes(v); print("guardado", n)


@app.local_entrypoint()
def cuadros_par(spec: str):
    """Igual que `cuadros`, pero los reparte en contenedores a la vez.

      GASTO_PERFIL=charlyfavela666 python3 gasto_modal.py run \\
        clientes/_escenas_carlos/escenas_carlos_modal.py::cuadros_par --spec X.json
    """
    import time
    s = json.load(open(spec)); o = _salida(s)
    refs = {k: _leer(v) for k, v in s["refs"].items()}
    semilla = s.get("semilla", 21); ancho = s.get("ancho", 720)
    alto = s.get("alto", 1280); pasos = s.get("pasos", 28)
    trabajos = [(n, refs, usar, p, (neg[0] if neg else ""), semilla, ancho, alto, pasos)
                for n, (usar, p, *neg) in s["cuadros"].items()]
    t0 = time.time()
    for nombre, b in Cuadros().uno.map(trabajos):
        (o / nombre).write_bytes(b); print("guardado", nombre)
    print(f"\n{len(trabajos)} cuadros en paralelo · {time.time() - t0:.0f} s de reloj")


@app.local_entrypoint()
def animar(spec: str):
    s = json.load(open(spec)); o = _salida(s)
    pngs = {p: (o / f"{p}.png").read_bytes() for t in s["tomas"] for p in ([t[1]] + ([t[5]] if len(t) > 5 and t[5] else []))}
    voces = {k: _leer(v) for k, v in s.get("voces", {}).items()}
    for n, v in gen_tomas.remote(s["carpeta"], pngs, [list(t) for t in s["tomas"]], voces, s.get("semilla", 21)).items():
        (o / n).write_bytes(v); print("guardado", n)
