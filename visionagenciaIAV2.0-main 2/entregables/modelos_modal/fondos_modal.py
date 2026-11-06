"""Fondos premium para estáticos con Qwen-Image (Apache 2.0) en Modal: solo fondo, sin personas ni texto."""
import io, json, pathlib
import modal

imagen = (modal.Image.debian_slim(python_version="3.12").apt_install("git")
          .pip_install("torch", "torchvision", "git+https://github.com/huggingface/diffusers", "transformers", "accelerate", "pillow"))
app = modal.App("fondos-qwen-image", image=imagen)
vol = modal.Volume.from_name("qwen-image")

BASE = ("Vertical 4:5 photograph of an empty environment, wide and open, photographed with shallow depth of field so the "
        "background is softly blurred. No people, no products, no text, no letters, no logos, no numbers, no signs, no posters, "
        "no picture frames, no blank boards, no screens, no billboards. Cinematic lighting, high-end commercial photography. ")
FONDOS = {
    "servilin": BASE + "Huge bright industrial warehouse interior with spotless glossy floor and high ceiling, teal accent lights, clean.",
    "rar": BASE + "Elegant dark emerald green studio backdrop with golden bokeh light particles and soft golden rim light, natural luxury wellness mood.",
    "ortega": BASE + "Modern bright office interior with navy blue walls, wooden accents and plants, warm golden ambient light, trustworthy.",
    "omar": BASE + "Modern corporate open office with royal blue accents, white desks and green plants, bright daylight, optimistic.",
    "mariano": BASE + "New hillside residential development in Baja California with modern white houses, dry hills and the ocean in the far distance at golden hour, summer.",
    "lisbeth": BASE + "Wild coastal hills with dry and green vegetation, a dirt road and the Pacific ocean in the distance at golden sunset, Oaxaca coast.",
    "carlos": BASE + "Dark graphite modern studio corridor with neon green light lines on the walls and floor reflections, premium tech mood.",
}


@app.function(gpu="A100-80GB", volumes={"/m": vol}, timeout=3600)
def generar(semilla: int = 11):
    import torch
    from diffusers import QwenImagePipeline
    pipe = QwenImagePipeline.from_pretrained("/m/Qwen-Image", torch_dtype=torch.bfloat16).to("cuda")
    salida = {}
    for n, p in FONDOS.items():
        img = pipe(prompt=p, negative_prompt="text, letters, words, numbers, logo, watermark, people, person, signage, poster, frame, blank board, screen, billboard, canvas",
                   width=1104, height=1376, num_inference_steps=40, true_cfg_scale=4.0,
                   generator=torch.Generator("cuda").manual_seed(semilla)).images[0]
        b = io.BytesIO(); img.save(b, "PNG"); salida[n] = b.getvalue(); print("fondo", n, flush=True)
    return salida


@app.local_entrypoint()
def main(semilla: int = 11):
    aqui = pathlib.Path(__file__).resolve().parent
    (aqui / "fondos").mkdir(exist_ok=True)
    for n, b in generar.remote(semilla).items():
        (aqui / "fondos" / f"{n}.png").write_bytes(b); print("guardado", n)
