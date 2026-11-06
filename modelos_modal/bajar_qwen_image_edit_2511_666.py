"""Descarga Qwen/Qwen-Image (Apache 2.0, mejor texto en imagen de los modelos abiertos con licencia comercial) a un volumen de Modal."""
import modal

app = modal.App("bajar-qwen-image-edit-2511", image=modal.Image.debian_slim(python_version="3.12").pip_install("huggingface_hub[hf_transfer]"))
vol = modal.Volume.from_name("qwen-image-edit-2511", create_if_missing=True)


@app.function(volumes={"/m": vol}, timeout=7200, cpu=4, memory=16384)
def bajar():
    import os
    os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
    from huggingface_hub import snapshot_download
    snapshot_download("Qwen/Qwen-Image-Edit-2511", local_dir="/m/Qwen-Image-Edit-2511")
    vol.commit()
    return sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk("/m/Qwen-Image-Edit-2511") for f in fs) / 1e9


@app.local_entrypoint()
def main():
    print("GB descargados:", round(bajar.remote(), 1))
