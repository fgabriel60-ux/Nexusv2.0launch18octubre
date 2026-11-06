"""Book nook Sanctum Sanctorum v2 · imagen realista: Qwen-Image-Edit-2511 convierte las vistas del diseño en una foto de la pieza ya cortada, pintada y armada en un librero.
Uso: MODAL_PROFILE=fabelagabriel645 modal run foto_realista_modal.py"""
import io, pathlib
import modal

AQUI = pathlib.Path(__file__).resolve().parent
imagen = (modal.Image.debian_slim(python_version="3.12").apt_install("git")
          .pip_install("torch", "torchvision", "git+https://github.com/huggingface/diffusers", "transformers", "accelerate", "pillow"))
app = modal.App("booknook-foto", image=imagen)
qwen = modal.Volume.from_name("qwen-image-edit-2511")
PROMPT = ("Fotografía realista y nítida de un book nook (diorama para librero) del Sanctum Sanctorum de Doctor Strange, hecho con cortes láser de MDF de 3 mm en capas, "
          "ya armado, entre libros de tapa dura sobre un librero de madera oscura. Mismo diseño de las imágenes de referencia: portal frontal con arco, ladrillo grabado, cornisa con dentículos, "
          "baranda con barrotes finos, escalones, y al fondo la gran ventana circular del Sanctum con radios y barras curvas, iluminada por dentro con luz LED cálida ámbar. "
          "Bordes del MDF con el tono café natural quemado del corte láser, algunas partes pintadas a mano en gris piedra, ocre y detalles dorados. Se ve la profundidad de las capas. "
          "Luz ambiente cálida de habitación, profundidad de campo suave, fotografía de producto de artesanía, alta calidad.")


@app.function(gpu="A100-80GB", volumes={"/qwen": qwen}, timeout=1800)
def generar(frontal: bytes, completa: bytes, semillas: list) -> list:
    import torch
    from PIL import Image
    from diffusers import QwenImageEditPlusPipeline
    pipe = QwenImageEditPlusPipeline.from_pretrained("/qwen/Qwen-Image-Edit-2511", torch_dtype=torch.bfloat16).to("cuda")
    imgs = [Image.open(io.BytesIO(b)).convert("RGB") for b in (frontal, completa)]
    out = []
    for s in semillas:
        im = pipe(image=imgs, prompt=PROMPT, negative_prompt="dibujo, render 3d plano, ilustración, texto, marca de agua, deforme, borroso",
                  true_cfg_scale=4.0, guidance_scale=1.0, num_inference_steps=40, height=1024, width=768,
                  generator=torch.Generator("cuda").manual_seed(s)).images[0]
        b = io.BytesIO(); im.save(b, "PNG"); out.append(b.getvalue())
    return out


@app.local_entrypoint()
def main(semillas: str = "3,11"):
    ss = [int(x) for x in semillas.split(",")]
    for s, b in zip(ss, generar.remote((AQUI / "vista_frontal.png").read_bytes(), (AQUI / "vista_completa.png").read_bytes(), ss)):
        (AQUI / f"foto_realista_s{s}.png").write_bytes(b); print("guardado", s)
