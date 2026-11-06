"""Prueba GLM-Image (MIT, especialista en texto) en Modal: estáticos con foto real + texto en español en un solo paso."""
import io, json, pathlib
import modal

imagen = (modal.Image.debian_slim(python_version="3.12").apt_install("git")
          .pip_install("torch", "torchvision", "accelerate", "pillow", "huggingface_hub[hf_transfer]", "sentencepiece", "protobuf")
          .pip_install("git+https://github.com/huggingface/transformers.git", "git+https://github.com/huggingface/diffusers.git"))
app = modal.App("glm-image", image=imagen)
vol = modal.Volume.from_name("glm-image", create_if_missing=True)


@app.function(gpu="A100-80GB", volumes={"/m": vol}, timeout=5400)
def probar(trabajos: list, semilla: int = 7):
    import os, torch
    os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
    from huggingface_hub import snapshot_download
    from PIL import Image
    from diffusers.pipelines.glm_image import GlmImagePipeline
    ruta = "/m/GLM-Image"
    if not os.path.exists(ruta + "/model_index.json"):
        snapshot_download("zai-org/GLM-Image", local_dir=ruta); vol.commit()
    pipe = GlmImagePipeline.from_pretrained(ruta, torch_dtype=torch.bfloat16, device_map="cuda")
    salida = {}
    for t in trabajos:
        kw = dict(prompt=t["prompt"], height=40 * 32, width=32 * 32, num_inference_steps=50, guidance_scale=1.5,
                  generator=torch.Generator("cuda").manual_seed(semilla))
        if t.get("foto"):
            im = Image.open(io.BytesIO(t["foto"])).convert("RGB")
            esc = max(1024 / im.width, 1280 / im.height)
            im = im.resize((round(im.width * esc), round(im.height * esc)), Image.LANCZOS)
            x = (im.width - 1024) // 2; y = (im.height - 1280) // 2
            kw["image"] = [im.crop((x, y, x + 1024, y + 1280))]
        img = pipe(**kw).images[0]
        b = io.BytesIO(); img.save(b, "PNG"); salida[t["nombre"]] = b.getvalue(); print("glm", t["nombre"], flush=True)
    return salida


@app.local_entrypoint()
def main(lote: str = "lote_glm.json"):
    aqui = pathlib.Path(__file__).resolve().parent
    trabajos = json.loads((aqui / lote).read_text())
    for t in trabajos:
        if t.get("foto"): t["foto"] = pathlib.Path(t["foto"]).read_bytes()
    (aqui / "glm").mkdir(exist_ok=True)
    for n, b in probar.remote(trabajos).items():
        (aqui / "glm" / f"{n}.png").write_bytes(b); print("guardado", n)
