"""Descarga Qwen3-VL-30B-A3B-Instruct al volumen qwen3-vl-30b en /hf (cache HF que lee qwen_productor_modal.py con HF_HOME=/m/hf). Solo CPU."""
import modal

app = modal.App("bajar-qwen3-vl", image=modal.Image.debian_slim(python_version="3.12").pip_install("huggingface_hub[hf_transfer]"))
vol = modal.Volume.from_name("qwen3-vl-30b", create_if_missing=True)
MODELO = "Qwen/Qwen3-VL-30B-A3B-Instruct"


@app.function(volumes={"/m": vol}, timeout=7200, cpu=8, memory=32768)
def bajar():
    import os
    os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
    os.environ["HF_HOME"] = "/m/hf"
    from huggingface_hub import snapshot_download
    snapshot_download(MODELO)
    vol.commit()
    return sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk("/m/hf") for f in fs) / 1e9


@app.local_entrypoint()
def main():
    print("GB descargados:", round(bajar.remote(), 1))
