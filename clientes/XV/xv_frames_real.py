"""XV Manuel: cuadros de la fiesta REALES con el look de la referencia. Qwen-Image-Edit-2511 solo cambia luz y color; personas, caras, poses y salón se conservan.
Uso: MODAL_PROFILE=fabelagabriel645 modal run xv_frames_real.py"""
import io, pathlib
import modal

imagen = (modal.Image.debian_slim(python_version="3.12").apt_install("git").pip_install("torch", "torchvision")
          .pip_install("git+https://github.com/huggingface/diffusers", "transformers", "accelerate", "pillow"))
app = modal.App("xv-frames-real", image=imagen)
qwen = modal.Volume.from_name("qwen-image-edit-2511")
PROMPT = ("Edita SOLO la iluminación y el color de esta foto real de una fiesta de XV años, como una película profesional de eventos: "
          "negros profundos, piel natural y limpia, luces de escenario azul y aqua con acentos rosa magenta en el fondo, haces de luz suaves y humo muy ligero en el aire, "
          "brillo suave en las luces, nitidez de cámara de cine. Conserva EXACTAMENTE las mismas personas, los mismos rostros y expresiones, las mismas poses, la misma ropa, "
          "el mismo vestido verde esmeralda, la misma corona, el mismo salón y el mismo encuadre. No agregues ni quites personas ni objetos.")
NEG = "persona nueva, cara distinta, rostro cambiado, manos deformes, dedos extra, objetos nuevos, texto, marca de agua, caricatura, render 3d, piel de plástico, sobreexpuesto, borroso"


@app.function(gpu="A100-80GB", volumes={"/qwen": qwen}, timeout=3600)
def generar(bases: dict) -> dict:
    import torch
    from PIL import Image
    from diffusers import QwenImageEditPlusPipeline
    pipe = QwenImageEditPlusPipeline.from_pretrained("/qwen/Qwen-Image-Edit-2511", torch_dtype=torch.bfloat16).to("cuda")
    salida = {}
    for nombre, datos in bases.items():
        img = Image.open(io.BytesIO(datos)).convert("RGB")
        out = pipe(image=[img], prompt=PROMPT, negative_prompt=NEG, true_cfg_scale=4.0, num_inference_steps=40,
                   height=1280, width=720, generator=torch.Generator("cuda").manual_seed(7)).images[0]
        b = io.BytesIO(); out.save(b, "PNG"); salida[nombre] = b.getvalue()
    return salida


@app.local_entrypoint()
def main():
    aqui = pathlib.Path(__file__).resolve().parent / 'frames_real'
    bases = {p.stem.removeprefix('base_'): p.read_bytes() for p in sorted(aqui.glob('base_*.png'))}
    for k, v in generar.remote(bases).items():
        (aqui / f'qwen_{k}.png').write_bytes(v); print('guardado', k)
