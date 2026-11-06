"""Rubén (quiropráctico) · cuadros mejorados con Qwen-Image-Edit a partir de cuadros de SUS TikToks (576x1024 con banner/texto) → 720x1280 limpios, sin texto.
Uso: python3 gasto_modal.py run clientes/Ruben_Quiropraxia/video/ruben_cuadros_modal.py   (guarda en video/cuadros_qwen/)"""
import io, pathlib, sys
import modal
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/Mariano/flyers_animados")
from flyers_modal import imagen, datos, qwen

app = modal.App("ruben-cuadros", image=imagen.add_local_python_source("flyers_modal"))
AQUI = pathlib.Path(__file__).resolve().parent
CUA = AQUI.parent / "cuadros"
SIN = " Foto vertical 9:16, realista, nítida, alta calidad, sin texto, sin letras, sin subtítulos, sin banners, sin logotipos, sin marcas de agua."
CARA = "Conserva EXACTAMENTE la cara de este hombre: barba corta oscura, cabello corto oscuro, ojos, nariz, edad y tono de piel. "
CON = "Consultorio con pared turquesa, camilla morada, piso de madera oscura y aro de luz. "
REFS = {"r1": "113k_30", "r2": "113k_26", "r3": "46k_24", "r4": "46k_21", "p1": "46k_07", "p2": "46k_02", "p3": "46k_29", "c1": "113k_30"}
QWEN = {  # nombre: (referencias, prompt, semilla)
    "R1_habla_a": (["r1", "r3", "r4"], CARA + "Él, con polo negro, está de pie dentro de ESTE consultorio, de frente a cámara, plano medio de la cintura para arriba, mirando a la cámara con expresión "
                   "amable y segura, boca ligeramente abierta como hablando, manos sueltas al frente. " + CON + "Luz natural suave." + SIN, 4),
    "R1_habla_b": (["r1", "r3", "r4"], CARA + "Él, con polo negro, está de pie dentro de ESTE consultorio, de frente a cámara, plano medio de la cintura para arriba, mirando a la cámara con sonrisa "
                   "ligera, manos sueltas al frente. " + CON + "Luz natural suave." + SIN, 11),
    "R2_andadera": (["p1", "p2", "r4"], "Mejora la calidad de esta foto SIN cambiar nada: el mismo señor de suéter amarillo y pantalón blanco apoyado en su andadera, la misma pared turquesa, "
                    "la camilla morada y el piso. Quita el banner y todo el texto. Más nítida y con mejor luz." + SIN, 4),
    "R3_manos": (["r3", "r2"], "Mejora la calidad de esta foto SIN cambiar nada: el mismo terapeuta de barba y polo negro atendiendo a un paciente acostado en la camilla morada, la misma pared turquesa. "
                 "Quita el banner y todo el texto. Más nítida, rostro y manos naturales, mejor luz." + SIN, 4),
    "R4_camina": (["p3", "p1"], "Mejora la calidad de esta foto SIN cambiar nada: el mismo señor de suéter amarillo y pantalón blanco caminando con su andadera dentro del mismo consultorio de "
                  "pared turquesa. Quita el banner y todo el texto. Más nítida y con mejor luz." + SIN, 4),
    "R5_escritorio": (["r1", "r3", "r4"], CARA + "Él, con polo negro, está sentado de frente a cámara en el mismo consultorio, plano medio, mirada directa y amable, manos entrelazadas sobre las piernas. " + CON + SIN, 7),
}


@app.function(gpu="A100-80GB", volumes={"/qwen": qwen}, timeout=3600)
def cuadros(refs: dict) -> dict:
    import gc, torch
    from PIL import Image
    from diffusers import QwenImageEditPlusPipeline
    imgs = {k: Image.open(io.BytesIO(v)).convert("RGB") for k, v in refs.items()}
    pipe = QwenImageEditPlusPipeline.from_pretrained("/qwen/Qwen-Image-Edit-2511", torch_dtype=torch.bfloat16).to("cuda")
    salida = {}
    for n, (usar, p, sem) in QWEN.items():
        im = pipe(image=[imgs[u] for u in usar], prompt=p, negative_prompt="texto, letras, subtítulos, banner, logotipo, cara distinta, deforme, borroso, manos extra, dedos extra, celular",
                  true_cfg_scale=4.0, guidance_scale=1.0, num_inference_steps=40, height=1280, width=720, generator=torch.Generator("cuda").manual_seed(sem)).images[0]
        b = io.BytesIO(); im.save(b, "PNG"); salida[f"{n}.png"] = b.getvalue(); print("cuadro", n, flush=True)
    return salida


@app.local_entrypoint()
def main():
    refs = {k: (CUA / f"{v}.png").read_bytes() for k, v in REFS.items()}
    out = AQUI / "cuadros_qwen"; out.mkdir(exist_ok=True)
    for n, v in cuadros.remote(refs).items():
        (out / n).write_bytes(v); print("guardado", n)
