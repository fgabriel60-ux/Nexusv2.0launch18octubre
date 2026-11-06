"""Guillermo · techo de placa teja sobre las 2 columnas de la señora: imagen final + video del proceso (columnas → travesaños → techo). Una sola GPU.
Audio de Guillermo (29 oct): de la barda hacia las columnas van 6 travesaños (incluido columna a columna) y hacia el fondo 3; referencia = techo de placa teja roja sobre estructura negra.
Para otra foto: cambiar SITIO/--sitio. Uso: python3 gasto_modal.py run clientes/Guillermo/techo_20261029/techo_modal.py [--sitio otra.jpg]"""
import io, json, pathlib, sys
import modal
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/XV")
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/Mariano/flyers_animados")
from flyers_modal import imagen, datos, qwen
from xv_modal import _flujo, _largo, ANCHO, ALTO, CARPETA

app = modal.App("guillermo-techo-v4", image=imagen.add_local_python_source("flyers_modal", "xv_modal"))
AQUI = pathlib.Path(__file__).resolve().parent
SIN = " Foto vertical 9:16, realista, nítida, luz de día, sin texto, sin letras, sin personas, sin logotipos."
MISMO = ("Misma cámara y MISMO encuadre que la primera foto: las dos columnas de concreto con varillas en el MISMO lugar y del MISMO tamaño, la barda de block al fondo, el cielo azul y el piso. "
         "El techo queda ENTRE la línea de las dos columnas y la barda del fondo. ")
ESTR = ("Estructura de acero NEGRO: una viga de columna a columna al frente (apoyada en las dos columnas), 6 travesaños (vigas) paralelos y parejos que van desde esa viga HACIA LA BARDA del fondo "
        "(alejándose de la cámara, perpendiculares a la barda, no hacia la cámara), y 3 vigas transversales a lo ancho hacia el fondo. TECHO DE UNA SOLA CAÍDA (una sola agua, NO a dos aguas, sin cumbrera ni caballete): el lado pegado a la barda queda más ALTO y el techo baja en una sola pendiente suave hacia el borde de las columnas, que queda más BAJO. ")
BASE = ("La primera foto muestra una estructura de acero NEGRO sobre dos columnas de concreto. NO muevas ni cambies NADA: misma cámara, mismas columnas, misma barda, mismo cielo, mismo piso y la estructura EXACTAMENTE en el mismo lugar, del mismo tamaño y a la misma altura. ")
PROMPTS = {
    "A": BASE + "Solo coloca láminas de placa teja ondulada color ROJO TEJA (como la de la segunda foto) APOYADAS DIRECTAMENTE sobre las vigas de esa estructura, cubriéndola con la misma forma y el mismo tamaño que ella, a ras, sin elevarla, sin separación, sin voladizo y sin nada de lámina por encima ni por detrás de la estructura. El techo queda a la altura de la barda." + SIN,
    "B": BASE + "Cubre la estructura con láminas de placa teja ondulada color ROJO TEJA (como la de la segunda foto) de modo que de frente SOLO se ve la lámina roja ocupando exactamente el lugar y el tamaño de la estructura, a ras de la barda, sin que se vea la estructura negra, sin voladizo y sin lámina por encima ni por detrás." + SIN,
}
NEG = "lámina por encima de la estructura, lámina elevada, lámina separada de las vigas, techo flotando, voladizo, techo a dos aguas, cumbrera, estructura visible debajo con la lámina más arriba, estructura movida, columnas distintas, otra barda, zoom, texto, letras, personas, deforme, borroso"


@app.function(gpu="A100-80GB", volumes={"/qwen": qwen}, timeout=3600)
def cuadros(refs: dict, semillas: list) -> dict:
    import io, torch
    from PIL import Image
    from diffusers import QwenImageEditPlusPipeline
    imgs = {k: Image.open(io.BytesIO(v)).convert("RGB") for k, v in refs.items()}
    pipe = QwenImageEditPlusPipeline.from_pretrained("/qwen/Qwen-Image-Edit-2511", torch_dtype=torch.bfloat16).to("cuda")
    salida = {}
    for k, p in PROMPTS.items():
        for sem in semillas:
            im = pipe(image=[imgs["T1_estructura"], imgs["ref"]], prompt=p, negative_prompt=NEG, true_cfg_scale=4.0, guidance_scale=1.0,
                      num_inference_steps=40, height=1280, width=720, generator=torch.Generator("cuda").manual_seed(sem)).images[0]
            b = io.BytesIO(); im.save(b, "PNG"); salida[f"cand_{k}_{sem}.png"] = b.getvalue(); print("cand", k, sem, flush=True)
    return salida


@app.local_entrypoint()
def main(semillas: str = "11,12"):
    refs = {"T1_estructura": (AQUI / "salida_v2" / "T1_estructura_limpio.png").read_bytes(), "ref": (AQUI / "ref_placateja.jpg").read_bytes()}
    out = AQUI / "salida_v4"; out.mkdir(exist_ok=True)
    for n, v in cuadros.remote(refs, [int(x) for x in semillas.split(",")]).items():
        (out / n).write_bytes(v); print("guardado", n)
