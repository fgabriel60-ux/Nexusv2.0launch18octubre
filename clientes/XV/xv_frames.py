"""XV Manuel: cuadros de la fiesta con el look de la referencia (luz de escenario fría con acentos magenta) usando Qwen-Image-Edit-2511.
Uso: MODAL_PROFILE=fabelagabriel645 modal run xv_frames.py"""
import io, pathlib
import modal

imagen = (modal.Image.debian_slim(python_version="3.12").apt_install("git").pip_install("torch", "torchvision")
          .pip_install("git+https://github.com/huggingface/diffusers", "transformers", "accelerate", "pillow"))
app = modal.App("xv-frames", image=imagen)
qwen = modal.Volume.from_name("qwen-image-edit-2511")
LOOK = ("Look de película de cine: luz de escenario azul y aqua con acentos rosa magenta, humo ligero, destellos y confeti en el aire, colores vivos, piel natural, "
        "alta nitidez, el vestido verde esmeralda sigue siendo el protagonista.")
TRABAJOS = {
    'salon': "El mismo salón de fiestas vacío y elegante, ahora con la pista brillante con reflejos, luces de escenario azules y rosas, candiles encendidos y el letrero XV iluminado. " + LOOK,
    'baile': "La misma quinceañera con su corona y su vestido verde esmeralda, bailando con el vestido en movimiento, mirada alegre. Mismo rostro, mismo peinado, mismo vestido. " + LOOK,
    'robot': "El mismo robot LED gigante en el salón de fiestas con la pista llena de invitados festejando con las manos arriba. Mismo robot, misma sala con candiles. " + LOOK,
    'corona': "La misma quinceañera con su corona recibiendo un abrazo, momento emotivo, la misma persona y el mismo vestido verde. " + LOOK,
}
NEG = "borroso, deforme, manos extra, dedos extra, cara distinta, texto nuevo, marca de agua, quemado, sobreexpuesto"


@app.function(gpu="A100-80GB", volumes={"/qwen": qwen}, timeout=3600)
def generar(bases: dict, semillas: list) -> dict:
    import torch
    from PIL import Image
    from diffusers import QwenImageEditPlusPipeline
    pipe = QwenImageEditPlusPipeline.from_pretrained("/qwen/Qwen-Image-Edit-2511", torch_dtype=torch.bfloat16).to("cuda")
    salida = {}
    for nombre, datos in bases.items():
        img = Image.open(io.BytesIO(datos)).convert("RGB")
        for s in semillas:
            out = pipe(image=[img], prompt=TRABAJOS[nombre], negative_prompt=NEG, true_cfg_scale=4.0, guidance_scale=1.0, num_inference_steps=40,
                       height=1280, width=720, generator=torch.Generator("cuda").manual_seed(s)).images[0]
            b = io.BytesIO(); out.save(b, "PNG"); salida[f'{nombre}_s{s}'] = b.getvalue()
    return salida


@app.local_entrypoint()
def main():
    aqui = pathlib.Path(__file__).resolve().parent / 'modal_frames'
    bases = {n: (aqui / f'base_{n}.png').read_bytes() for n in TRABAJOS}
    for k, v in generar.remote(bases, [11, 22]).items():
        (aqui / f'gen_{k}.png').write_bytes(v); print('guardado', k)
