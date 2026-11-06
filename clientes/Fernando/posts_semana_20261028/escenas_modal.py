"""Escenas premium de Anegocios (Fernando) con Qwen-Image-Edit-2511 en Modal. Uso: MODAL_PROFILE=fgabriel60 modal run escenas_modal.py"""
import io, pathlib, modal
imagen = (modal.Image.debian_slim(python_version="3.12").apt_install("git")
          .pip_install("torch", "torchvision", "git+https://github.com/huggingface/diffusers", "transformers", "accelerate", "pillow"))
app = modal.App("anegocios-escenas", image=imagen)
qwen = modal.Volume.from_name("qwen-image-edit-2511")
AQUI = pathlib.Path(__file__).resolve().parent
NT = "Photorealistic commercial advertising photo, warm professional studio lighting, shallow depth of field, premium look, sharp details. Absolutely no text, no letters, no logos, no signs with writing. "
ESC = {
 "lunes_1": (864, 1080, ["cara_gafas", "impresora_frente", "lector"],
   NT + "The man from image 1 (same face, gray hair, glasses, gray goatee, dark t-shirt) stands behind the counter of a well-stocked neighborhood grocery store in Mexico City, smiling at the camera, shelves full of products blurred behind him. On the counter in front of him: a computer monitor with a point-of-sale screen, the black and blue thermal receipt printer from image 2 and the black and orange barcode scanner from image 3. Waist-up, vertical composition with empty space at the bottom."),
 "lunes_2": (864, 1080, ["lector_mano", "lector"],
   NT + "Close-up of a hand scanning a grocery product with the black and orange barcode scanner (like images 1 and 2), red laser line on the barcode, warm golden light, blurred grocery store shelves in the background with bokeh. Natural hand with five fingers. Empty space at the bottom."),
 "lunes_3": (864, 1080, ["impresora_ticket"],
   NT + "A modern computer monitor on a grocery store counter, front view, the monitor screen is filled with a flat solid pure green color (#00FF00) with nothing on it, neat black bezel. Beside it the black and blue thermal receipt printer from image 1 with a paper receipt coming out of it. Blurred warm store background. Empty space at the bottom."),
 "lunes_4": (864, 1080, ["cara_gafas"],
   NT + "The man from image 1 (same face, gray hair, glasses, gray goatee, dark t-shirt) sits at a desk in a small shop, patiently explaining a computer point-of-sale screen to a friendly Mexican woman shop owner in her 40s, both looking at the monitor, he points at the screen with his hand. Warm cozy shop interior. Empty space at the bottom."),
 "martes": (720, 1280, ["impresora_frente"],
   NT + "Completely replace the scene with an elegant premium abstract background: a softly blurred warm grocery store interior with golden bokeh lights, deep navy blue and violet tones, nothing in the foreground, large empty central area, vertical. No objects, no people."),
 "miercoles": (720, 1280, ["cara_gafas", "cara_blanca"],
   NT + "The man from the images (same face, gray hair, glasses, gray goatee, dark t-shirt) stands in a bright, colorful ice cream shop (nevería) behind a glass display case full of colorful ice cream tubs, cups stacked beside him, smiling at the camera, holding up a tablet whose screen faces the camera and is filled with a flat solid pure green color (#00FF00). Vertical, empty space at the bottom."),
 "jueves": (720, 1280, ["cara_blanca", "cara_gafas"],
   NT + "The man from the images (same face, gray hair, gray goatee, light casual shirt) arrives at the entrance of a small business in Mexico City carrying a plain brown cardboard box with both hands, smiling friendly at the camera, street and shop front blurred behind him, warm afternoon light. Plain box with no printing. Vertical, empty space at the bottom."),
 "viernes": (864, 1080, ["impresora_ticket", "lector", "rollos"],
   NT + "Premium product still-life hero shot: the black and blue thermal receipt printer from image 1 with a paper receipt coming out, the black and orange barcode scanner from image 2 lying beside it and white thermal paper rolls like image 3 stacked next to them, on an elegant dark polished surface with soft reflections, dramatic warm studio lighting, dark navy background. Blank receipt, no writing. Empty space at the bottom."),
}
NEG = "text, letters, words, numbers, watermark, logo, blurry, deformed hands, extra fingers, ugly, cartoon, illustration"

@app.function(gpu="A100-80GB", volumes={"/qwen": qwen}, timeout=7200)
def generar(refs: dict, escenas: dict):
    import torch
    from PIL import Image
    from diffusers import QwenImageEditPlusPipeline
    pipe = QwenImageEditPlusPipeline.from_pretrained("/qwen/Qwen-Image-Edit-2511", torch_dtype=torch.bfloat16).to("cuda")
    for k, (w, h, rs, p) in escenas.items():
        imgs = [Image.open(io.BytesIO(refs[r])).convert("RGB") for r in rs]
        for s in (1, 2):
            r = pipe(image=imgs, prompt=p, negative_prompt=NEG, true_cfg_scale=4.0, num_inference_steps=40, width=w, height=h,
                     generator=torch.Generator("cuda").manual_seed(s)).images[0]
            b = io.BytesIO(); r.save(b, "PNG"); print("ok", k, s, flush=True); yield f"{k}_s{s}", b.getvalue()

@app.local_entrypoint()
def main():
    refs = {p.stem: p.read_bytes() for p in (AQUI / "refs").glob("*.jpg")}
    for n, b in generar.remote_gen(refs, ESC):
        (AQUI / "escenas" / f"{n}.png").write_bytes(b); print("guardado", n)
