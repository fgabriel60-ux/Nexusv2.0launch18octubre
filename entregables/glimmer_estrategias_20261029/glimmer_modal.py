"""Consulta Muse-Glimmer-30B (texto + imágenes) en Modal. Uso: modal run glimmer_modal.py --prompt "..." [--fotos a.jpg,b.png]
Varias consultas con una sola carga del modelo: modal run glimmer_modal.py --lote lote.json   (lista de {"nombre", "prompt", "fotos": [rutas]})"""
import io, json, pathlib
import modal

imagen = (modal.Image.debian_slim(python_version="3.12").apt_install("git")
          .pip_install("torch", "torchvision", "accelerate", "pillow", "sentencepiece", "protobuf")
          .pip_install("git+https://github.com/huggingface/transformers.git"))
app = modal.App("glimmer", image=imagen)
vol = modal.Volume.from_name("muse-glimmer-30b", create_if_missing=True)


def _responder(proc, modelo, prompt, fotos, tokens, directo=True):
    """4 nov 2026: `directo` añade « to=user» al final del prompt, igual que glimmer_chat_web.py.

    Sin eso, Glimmer escribe primero cientos de tokens de razonamiento interno («We need output in
    Spanish… Let's produce.») y luego la respuesta: se tardaba 5 min por video y a veces se quedaba
    sin tokens a media respuesta (le pasó a la estrategia de Rafael el 4 nov). Con el canal directo
    sale solo la respuesta, en la mitad del tiempo y sin cortarse.
    """
    from PIL import Image
    ims = [Image.open(io.BytesIO(b)).convert("RGB") for b in fotos]
    contenido = [{"type": "image", "image": im} for im in ims]
    contenido.append({"type": "text", "text": prompt})
    texto = proc.apply_chat_template([{"role": "user", "content": contenido}], add_generation_prompt=True, tokenize=False)
    if directo:
        texto += " to=user"
    entrada = proc(text=texto, images=ims or None, return_tensors="pt").to("cuda")
    salida = modelo.generate(**entrada, max_new_tokens=tokens, do_sample=False)
    return proc.decode(salida[0][entrada["input_ids"].shape[1]:], skip_special_tokens=True)


def _cargar():
    import torch
    from transformers import AutoModelForImageTextToText, AutoProcessor
    ruta = "/m/Muse-Glimmer-30B"
    return AutoProcessor.from_pretrained(ruta), AutoModelForImageTextToText.from_pretrained(ruta, torch_dtype=torch.bfloat16, device_map="cuda")


@app.cls(gpu="A100-80GB", volumes={"/m": vol}, timeout=3600,
         scaledown_window=600, max_containers=2, retries=2)
class Calidad:
    """Glimmer como juez de calidad, con el modelo YA CARGADO (3 nov 2026).

    El 80-90% de los 6 minutos que tardaba una calificación era cargar los 30B
    en la A100. Con `@modal.enter()` el modelo se carga una vez por contenedor y
    `scaledown_window=600` lo deja caliente 10 min: la segunda calificación y las
    siguientes salen en segundos, que es lo que hace viable corregir y volver a
    calificar en la misma sesión.

    `retries=2`: si la GPU se cae a medias, Modal lo reintenta solo.

    Cuidado con el tiempo en caliente: una A100 ociosa cuesta igual que trabajando
    (~$4 la hora). El 5 nov 2026 Carlos pidió subirlo de 5 a 10 min: en una tarde de
    correcciones seguidas, cada vez que se enfriaba había que volver a pagar ~1 min de
    carga del modelo de 30B, y eso costaba más que dejarlo caliente. 10 min ocioso son
    unos $0.66; recargar el modelo son ~$0.07 pero además 1 minuto de espera cada vez.
    Si se deja de calificar por un rato largo, el contenedor se apaga solo igual.
    """

    @modal.enter()
    def cargar(self):
        self.proc, self.modelo = _cargar()
        print("Glimmer cargado y caliente", flush=True)

    @modal.method()
    def preguntar(self, prompt: str, fotos: list, tokens: int = 1024) -> str:
        return _responder(self.proc, self.modelo, prompt, fotos, tokens)

    @modal.method()
    def lote(self, trabajos: list, tokens: int = 1024) -> list:
        return [_responder(self.proc, self.modelo, t["prompt"], t["fotos"], tokens)
                for t in trabajos]


@app.function(gpu="A100-80GB", volumes={"/m": vol}, timeout=3600)
def consultar(prompt: str, fotos: list, tokens: int = 1024):
    return _responder(*_cargar(), prompt, fotos, tokens)


@app.function(gpu="A100-80GB", volumes={"/m": vol}, timeout=3600 * 3)
def consultar_lote(trabajos: list, tokens: int = 1024) -> list:
    proc, modelo = _cargar()
    return [_responder(proc, modelo, t["prompt"], t["fotos"], tokens) for t in trabajos]


@app.local_entrypoint()
def main(prompt: str = "", fotos: str = "", tokens: int = 1024, lote: str = ""):
    if lote:
        trabajos = json.loads(pathlib.Path(lote).read_text())
        for t in trabajos:
            t["fotos"] = [pathlib.Path(f).read_bytes() for f in t["fotos"]]
        for t, r in zip(trabajos, consultar_lote.remote(trabajos, tokens)):
            print(f"\n######## {t['nombre']}\n{r}")
        return
    bs = [pathlib.Path(f).read_bytes() for f in fotos.split(",") if f]
    print(consultar.remote(prompt, bs, tokens))
