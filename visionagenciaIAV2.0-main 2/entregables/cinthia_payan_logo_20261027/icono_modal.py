"""Cinthia Payán (terapeuta TDAH): icono compacto cerebro + corazón + peonía con Qwen-Image-Edit-2511 en Modal. Sin texto: el nombre se compone aparte (armar_logo.py).
Uso: modal run icono_modal.py"""
import io, pathlib
import modal

imagen = (modal.Image.debian_slim(python_version="3.12").apt_install("git")
          .pip_install("torch", "torchvision", "git+https://github.com/huggingface/diffusers", "transformers", "accelerate", "pillow"))
app = modal.App("cinthia-logo", image=imagen)
qwen = modal.Volume.from_name("qwen-image-edit-2511")
AQUI = pathlib.Path(__file__).resolve().parent

BASE = ("Logo icon on a plain pure white background, centered, compact and square, thin elegant line-art in soft watercolor gradient "
        "(lilac, pink and teal) like the style of image 1. NO text, NO letters, NO numbers, no frame, no shadow. ")
PROMPTS = {
    "a": BASE + "A small anatomical human heart at the bottom; a slim stem rises from the heart and ends in a pink peony flower in full bloom (inspired by image 2); "
         "a small line-art brain rests on the stem beside the peony. Vertical, balanced, minimal.",
    "b": BASE + "A single compact emblem: a line-art heart whose top opens into a brain, and a pink peony blooming at the top of the brain, "
         "two small green leaves on the sides. Round compact composition that fits inside a circle.",
    "c": BASE + "Round emblem: a pink peony in full bloom (inspired by image 2) with a delicate line-art brain and heart intertwined in its center, "
         "thin gradient outline, very compact and symmetric.",
}


@app.function(gpu="A100-80GB", volumes={"/qwen": qwen}, timeout=3600)
def generar(refs: list):
    import torch
    from PIL import Image
    from diffusers import QwenImageEditPlusPipeline
    pipe = QwenImageEditPlusPipeline.from_pretrained("/qwen/Qwen-Image-Edit-2511", torch_dtype=torch.bfloat16).to("cuda")
    imgs = [Image.open(io.BytesIO(b)).convert("RGB") for b in refs]
    out = {}
    for k, p in PROMPTS.items():
        for s in (1, 2):
            r = pipe(image=imgs, prompt=p, negative_prompt="text, letters, watermark, photo, blurry, ugly", true_cfg_scale=4.0,
                     num_inference_steps=40, width=1024, height=1024, generator=torch.Generator("cuda").manual_seed(s)).images[0]
            b = io.BytesIO(); r.save(b, "PNG"); out[f"{k}{s}"] = b.getvalue()
    return out


@app.local_entrypoint()
def main():
    refs = [(AQUI / "refs" / n).read_bytes() for n in ("corazon_cerebro_recorte.png", "peonia_recorte.png")]
    (AQUI / "iconos").mkdir(exist_ok=True)
    for n, b in generar.remote(refs).items():
        (AQUI / "iconos" / f"icono_{n}.png").write_bytes(b); print("ok", n)
