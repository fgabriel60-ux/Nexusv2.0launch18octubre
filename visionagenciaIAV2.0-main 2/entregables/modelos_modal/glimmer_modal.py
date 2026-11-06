"""Consulta Muse-Glimmer-30B (texto + imágenes) en Modal. Uso: modal run glimmer_modal.py --prompt "..." [--fotos a.jpg,b.png]
Varias consultas con una sola carga del modelo: modal run glimmer_modal.py --lote lote.json   (lista de {"nombre", "prompt", "fotos": [rutas]})"""
import io, json, pathlib
import modal

imagen = (modal.Image.debian_slim(python_version="3.12").apt_install("git")
          .pip_install("torch", "torchvision", "accelerate", "pillow", "sentencepiece", "protobuf")
          .pip_install("git+https://github.com/huggingface/transformers.git"))
app = modal.App("glimmer", image=imagen)
vol = modal.Volume.from_name("muse-glimmer-30b", create_if_missing=True)


def _responder(proc, modelo, prompt, fotos, tokens):
    from PIL import Image
    contenido = [{"type": "image", "image": Image.open(io.BytesIO(b)).convert("RGB")} for b in fotos]
    contenido.append({"type": "text", "text": prompt})
    entrada = proc.apply_chat_template([{"role": "user", "content": contenido}], add_generation_prompt=True,
                                       tokenize=True, return_dict=True, return_tensors="pt").to("cuda")
    salida = modelo.generate(**entrada, max_new_tokens=tokens, do_sample=False)
    return proc.decode(salida[0][entrada["input_ids"].shape[1]:], skip_special_tokens=True)


def _cargar():
    import torch
    from transformers import AutoModelForImageTextToText, AutoProcessor
    ruta = "/m/Muse-Glimmer-30B"
    return AutoProcessor.from_pretrained(ruta), AutoModelForImageTextToText.from_pretrained(ruta, torch_dtype=torch.bfloat16, device_map="cuda")


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
