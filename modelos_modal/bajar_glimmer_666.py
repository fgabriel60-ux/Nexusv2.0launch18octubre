"""Descarga meta-models/Muse-Glimmer-30B (Apache 2.0, público) a un volumen de Modal para analizar referencias e imágenes."""
import modal

app = modal.App("bajar-muse-glimmer", image=modal.Image.debian_slim(python_version="3.12").pip_install("huggingface_hub[hf_transfer]"))
vol = modal.Volume.from_name("muse-glimmer-30b", create_if_missing=True)


@app.function(volumes={"/m": vol}, timeout=7200, cpu=4, memory=16384)
def bajar():
    import os
    os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
    from huggingface_hub import snapshot_download
    snapshot_download("meta-models/Muse-Glimmer-30B", local_dir="/m/Muse-Glimmer-30B")
    vol.commit()
    return sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk("/m/Muse-Glimmer-30B") for f in fs) / 1e9


@app.local_entrypoint()
def main():
    print("GB descargados:", round(bajar.remote(), 1))
