"""Fotos reales de Servilin mejoradas en Modal con Qwen-Image-Edit-2511 (mismas personas y lugar) para los flyers.

Uso:  modal run flyers_modal.py
"""
import io
import pathlib
import modal

imagen = (modal.Image.debian_slim(python_version="3.12").apt_install("git")
          .pip_install("torch", "torchvision", "git+https://github.com/huggingface/diffusers", "transformers", "accelerate", "pillow"))
app = modal.App("servilin-flyers", image=imagen)
qwen = modal.Volume.from_name("qwen-image-edit-2511")

MEJORA = ("Mejora esta foto real a calidad de fotografía profesional publicitaria: más nitidez, mejor exposición, colores "
          "limpios y vivos, piso y superficies más brillantes. NO cambies a las personas, sus caras, uniformes, poses ni el "
          "lugar; no agregues ni quites personas ni objetos; sin texto.")
FLYERS = {"F1": ("020_image.jpg", MEJORA), "F2": ("019_image.jpg", MEJORA), "F3": ("026_image.jpg", MEJORA)}


@app.function(gpu="A100-80GB", volumes={"/qwen": qwen}, timeout=3600)
def disenar(fotos: dict, estilo: bytes, logo: bytes, semilla: int = 3):
    import torch
    from PIL import Image
    from diffusers import QwenImageEditPlusPipeline
    pipe = QwenImageEditPlusPipeline.from_pretrained("/qwen/Qwen-Image-Edit-2511", torch_dtype=torch.bfloat16).to("cuda")
    ab = lambda b: Image.open(io.BytesIO(b)).convert("RGB")
    salida = {}
    for nombre, (foto, prompt) in FLYERS.items():
        base = ab(fotos[foto])
        img = pipe(image=[base], prompt=prompt,
                   negative_prompt="faltas de ortografía, letras deformes, texto ilegible, personas falsas, caras de plástico",
                   true_cfg_scale=4.0, guidance_scale=1.0, num_inference_steps=40, width=960, height=1280,
                   generator=torch.Generator("cuda").manual_seed(semilla)).images[0]
        b = io.BytesIO(); img.save(b, "PNG"); salida[nombre] = b.getvalue()
        print("flyer", nombre, flush=True)
    return salida


@app.local_entrypoint()
def main(semilla: int = 3):
    aqui = pathlib.Path(__file__).resolve().parent
    r = aqui / "reenviados"
    fotos = {f: (r / f).read_bytes() for f, _ in FLYERS.values()}
    res = disenar.remote(fotos, (r / "009_image.jpg").read_bytes(), (r / "017_image.jpg").read_bytes(), semilla)
    destino = aqui / "flyers_modal"; destino.mkdir(exist_ok=True)
    for n, b in res.items():
        (destino / f"foto_mejorada_{n}.png").write_bytes(b)
        print("guardado", n)
