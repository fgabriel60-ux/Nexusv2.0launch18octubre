"""XV Manuel: limpia un cuadro del salón (quita a las personas) con Qwen-Image-Edit-2511. Uso: modal run xv_cuadro.py --base modal_tomas/S2_base.png --salida modal_tomas/S2_salon.png"""
import io, pathlib
import modal

imagen = (modal.Image.debian_slim(python_version="3.12").apt_install("git").pip_install("torch", "torchvision")
          .pip_install("git+https://github.com/huggingface/diffusers", "transformers", "accelerate", "pillow"))
app = modal.App("xv-cuadro", image=imagen)
qwen = modal.Volume.from_name("qwen-image-edit-2511")
PROMPT = ("Quita a TODAS las personas de la imagen y deja el salón de fiestas completamente vacío: mismo arco de flores blancas con luces verdes, mismas letras XV iluminadas, "
          "mismo piso de madera brillante con confeti dorado, mismas paredes y luces cálidas. Mismo encuadre vertical y misma iluminación. Sin personas, sin texto nuevo.")


@app.function(gpu="A100-80GB", volumes={"/qwen": qwen}, timeout=3600)
def limpiar(base: bytes, semilla: int = 3) -> bytes:
    import torch
    from PIL import Image
    from diffusers import QwenImageEditPlusPipeline
    pipe = QwenImageEditPlusPipeline.from_pretrained("/qwen/Qwen-Image-Edit-2511", torch_dtype=torch.bfloat16).to("cuda")
    img = Image.open(io.BytesIO(base)).convert("RGB")
    out = pipe(image=[img], prompt=PROMPT, negative_prompt="personas, gente, rostros, texto, letras nuevas, borroso, deforme", true_cfg_scale=4.0, guidance_scale=1.0,
               num_inference_steps=40, height=1024, width=576, generator=torch.Generator("cuda").manual_seed(semilla)).images[0]
    b = io.BytesIO(); out.save(b, "PNG"); return b.getvalue()


@app.local_entrypoint()
def main(base: str = "modal_tomas/S2_base.png", salida: str = "modal_tomas/S2_salon.png", semilla: int = 3):
    aqui = pathlib.Path(__file__).resolve().parent
    (aqui / salida).write_bytes(limpiar.remote((aqui / base).read_bytes(), semilla))
    print("guardado", aqui / salida)
