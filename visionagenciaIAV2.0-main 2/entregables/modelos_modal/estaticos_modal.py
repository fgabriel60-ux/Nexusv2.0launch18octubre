"""Estáticos publicitarios en Modal con Qwen-Image-Edit-2511 (Apache 2.0): UNA foto real del cliente + diseño y texto exacto.

Uso:  modal run estaticos_modal.py --lote prueba
"""
import io, json, pathlib
import modal

imagen = (modal.Image.debian_slim(python_version="3.12").apt_install("git")
          .pip_install("torch", "torchvision", "git+https://github.com/huggingface/diffusers", "transformers", "accelerate", "pillow"))
app = modal.App("estaticos-qwen", image=imagen)
qwen = modal.Volume.from_name("qwen-image-edit-2511")

REGLAS = ("Diseña la composición visual de un anuncio publicitario vertical 4:5 de nivel agencia para Facebook e Instagram, usando "
          "la FOTO de la imagen 1 como fotografía principal SIN cambiar a las personas, sus caras ni los productos. Fondo de "
          "diseño profesional con degradados, luces y formas modernas. IMPORTANTE: NO escribas NINGUNA letra, palabra, número "
          "ni logotipo; deja vacío y limpio el 30 % superior para el título y una franja vacía abajo para un botón. Estilo: ")


@app.function(gpu="A100-80GB", volumes={"/qwen": qwen}, timeout=3600)
def disenar(trabajos: list, semilla: int = 5):
    import torch
    from PIL import Image
    from diffusers import QwenImageEditPlusPipeline
    pipe = QwenImageEditPlusPipeline.from_pretrained("/qwen/Qwen-Image-Edit-2511", torch_dtype=torch.bfloat16).to("cuda")
    salida = {}
    for t in trabajos:
        img = pipe(image=[Image.open(io.BytesIO(t["foto"])).convert("RGB")], prompt=REGLAS + t["texto"],
                   negative_prompt="texto, letras, palabras, números, tipografía, logotipos, marcas de agua, caras deformes",
                   true_cfg_scale=4.5, guidance_scale=1.0, num_inference_steps=50, width=1024, height=1280,
                   generator=torch.Generator("cuda").manual_seed(semilla)).images[0]
        b = io.BytesIO(); img.save(b, "PNG"); salida[t["nombre"]] = b.getvalue()
        print("estático", t["nombre"], flush=True)
    return salida


@app.local_entrypoint()
def main(lote: str = "lote.json", semilla: int = 5):
    aqui = pathlib.Path(__file__).resolve().parent
    trabajos = json.loads((aqui / lote).read_text())
    for t in trabajos:
        t["foto"] = pathlib.Path(t["foto"]).read_bytes()
    res = disenar.remote(trabajos, semilla)
    (aqui / "salida").mkdir(exist_ok=True)
    for n, b in res.items():
        (aqui / "salida" / f"{n}.png").write_bytes(b); print("guardado", n)
