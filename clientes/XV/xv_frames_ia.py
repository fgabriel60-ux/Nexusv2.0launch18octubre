"""XV Manuel: cuadros de IA nivel referencia sobre los momentos reales. Imagen 1 = cuadro real (composición), imagen 2 = retrato de la quinceañera (identidad).
Uso: MODAL_PROFILE=fabelagabriel645 modal run xv_frames_ia.py"""
import io, pathlib
import modal

imagen = (modal.Image.debian_slim(python_version="3.12").apt_install("git").pip_install("torch", "torchvision")
          .pip_install("git+https://github.com/huggingface/diffusers", "transformers", "accelerate", "pillow"))
app = modal.App("xv-frames-ia", image=imagen)
qwen = modal.Volume.from_name("qwen-image-edit-2511")
LOOK = ("Fotograma de un video profesional de XV años grabado con cámara de cine: luces de escenario azul y aqua con acentos rosa magenta al fondo, haces de luz y humo ligero, "
        "confeti brillante en el aire, reflejos en la pista, rostros bien iluminados con luz suave y piel natural, negros profundos, alta nitidez, profundidad de campo. ")
CARA = "La quinceañera tiene EXACTAMENTE el rostro de la chica de la imagen 2 (misma cara, mismos ojos, misma sonrisa, mismo cabello castaño largo y rizado). "
TRABAJOS = {
    '1_heroe': LOOK + CARA + "Mantén la escena de la imagen 1: ella al frente sonriendo con su vestido verde esmeralda y su corona, invitados detrás. Misma pose y encuadre.",
    '2_pista': LOOK + CARA + "Mantén la escena de la imagen 1: ella en la pista con su vestido verde esmeralda y su corona, sus amigas alrededor. Misma pose y encuadre.",
    '3_xv': LOOK + CARA + "Mantén la escena de la imagen 1: ella con su vestido verde junto al arco de flores blancas y el letrero luminoso. Misma pose y encuadre.",
    '4_amigas': LOOK + "Mantén la escena de la imagen 1: la quinceañera de espaldas con su corona y vestido verde abrazando a su amiga del vestido dorado. Mismas personas, misma pose.",
    '5_robot': LOOK + "Mantén la escena de la imagen 1: el MISMO robot LED con sus luces azules, idéntico, bailando entre los invitados. Mismas personas, mismo encuadre.",
    '6_familia': LOOK + CARA + "Mantén la escena de la imagen 1: ella al centro con su familia brindando frente al arco de flores blancas. Mismas personas, misma pose, encuadre igual.",
    '7_retrato': LOOK + CARA + "Retrato cerrado de ella en el salón de fiesta de noche: corona, vestido verde esmeralda de pedrería, sonrisa a cámara, luces de escenario desenfocadas detrás.",
    '8_detalle': LOOK + CARA + "Acercamiento de detalle a su corona de cristales y la pedrería del vestido verde esmeralda, con destellos de luz, en la fiesta de noche.",
}
NEG = "cara distinta, rostro cambiado, persona inventada, manos deformes, dedos extra, texto, marca de agua, caricatura, render 3d, piel de plástico, oscuro, subexpuesto, borroso"


@app.function(gpu="A100-80GB", volumes={"/qwen": qwen}, timeout=3600)
def generar(bases: dict, cara: bytes, semillas: list) -> dict:
    import torch
    from PIL import Image
    from diffusers import QwenImageEditPlusPipeline
    pipe = QwenImageEditPlusPipeline.from_pretrained("/qwen/Qwen-Image-Edit-2511", torch_dtype=torch.bfloat16).to("cuda")
    ref = Image.open(io.BytesIO(cara)).convert("RGB")
    salida = {}
    for nombre, datos in bases.items():
        img = Image.open(io.BytesIO(datos)).convert("RGB")
        for s in semillas:
            out = pipe(image=[img, ref], prompt=TRABAJOS[nombre], negative_prompt=NEG, true_cfg_scale=4.0, num_inference_steps=40,
                       height=1280, width=720, generator=torch.Generator("cuda").manual_seed(s)).images[0]
            b = io.BytesIO(); out.save(b, "PNG"); salida[f'{nombre}_s{s}'] = b.getvalue()
    return salida


@app.local_entrypoint()
def main():
    aqui = pathlib.Path(__file__).resolve().parent / 'frames_real'
    bases = {n: (aqui / f'base_{n}.png').read_bytes() for n in TRABAJOS}
    for k, v in generar.remote(bases, (aqui / 'ref_cara.jpg').read_bytes(), [5, 9]).items():
        (aqui / f'ia_{k}.png').write_bytes(v); print('guardado', k)
