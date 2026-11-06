"""Descarga black-forest-labs/FLUX.1-schnell (Apache 2.0, sin token de HF) a un volumen de Modal."""
import modal

app = modal.App("bajar-flux", image=modal.Image.debian_slim(python_version="3.12").pip_install("huggingface_hub[hf_transfer]"))
vol = modal.Volume.from_name("flux1-schnell", create_if_missing=True)


@app.function(volumes={"/m": vol}, timeout=7200, cpu=8, memory=32768)
def bajar():
    import os
    os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
    from huggingface_hub import snapshot_download
    snapshot_download("black-forest-labs/FLUX.1-schnell", local_dir="/m/FLUX.1-schnell")
    vol.commit()
    return sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk("/m/FLUX.1-schnell") for f in fs) / 1e9


@app.local_entrypoint()
def main():
    print("GB descargados:", round(bajar.remote(), 1))
