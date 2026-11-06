"""Blanca (Hablar...Hablando): retrato profesional con Qwen-Image-Edit-2511 — SU cara de la selfie del auto + el consultorio del reel de referencia.
Uso: modal run blanca_imagen_modal.py"""
import io, pathlib, sys
import modal
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/Mariano/flyers_animados")
from flyers_modal import imagen, qwen

app = modal.App("blanca-imagen", image=imagen.add_local_python_source("flyers_modal"))
AQUI = pathlib.Path(__file__).resolve().parent
PROMPT = ("Conserva EXACTAMENTE a esta mujer: la misma cara, los mismos ojos, cejas, nariz, labios, edad, tono de piel y su cabello castaño largo con luces. "
          "Cámbiale el lugar: siéntala en un consultorio de terapia de lenguaje profesional: escritorio de mármol blanco, muro de piedra gris con luz cálida LED, "
          "sobre la mesa rompecabezas infantiles de colores sin personajes y una torre de bloques de madera de colores. Lleva una blusa negra elegante. "
          "Foto vertical 9:16, plano medio, sentada con las manos sobre el escritorio, mirando a la cámara con una sonrisa cálida y confiable, "
          "iluminación profesional suave, nítida, realista, alta resolución. Sin texto.")
NEG = "texto, letras, subtítulos, logotipo, personajes de caricatura, otra persona, cara distinta, deforme, borroso, manos extra"


@app.function(gpu="A100-80GB", volumes={"/qwen": qwen}, timeout=3600)
def retratos(cara: bytes, lugar: bytes, semillas: list) -> dict:
    import torch
    from PIL import Image
    from diffusers import QwenImageEditPlusPipeline
    pipe = QwenImageEditPlusPipeline.from_pretrained("/qwen/Qwen-Image-Edit-2511", torch_dtype=torch.bfloat16).to("cuda")
    imgs = [Image.open(io.BytesIO(cara)).convert("RGB")]  # solo su foto: con la referencia, Qwen copiaba la cara de la otra mujer
    out = {}
    for s in semillas:
        im = pipe(image=imgs, prompt=PROMPT, negative_prompt=NEG, true_cfg_scale=4.0, guidance_scale=1.0, num_inference_steps=40,
                  height=1280, width=720, generator=torch.Generator("cuda").manual_seed(s)).images[0]
        b = io.BytesIO(); im.save(b, "PNG"); out[f"blanca_consultorio_s{s}.png"] = b.getvalue(); print("listo", s, flush=True)
    return out


@app.local_entrypoint()
def main():
    cara = (AQUI.parent / "whatsapp" / "del_cliente" / "img_3.jpg").read_bytes()
    lugar = (AQUI / "referencia_consultorio.jpg").read_bytes()
    for n, v in retratos.remote(cara, lugar, [3, 11]).items():
        (AQUI / n).write_bytes(v); print("guardado", n)
