"""Descarga MiniMax H3 (Comfy-Org/MiniMax-H3) al volumen h3-comprimido-gastro en /models, con la estructura que usan los scripts de clientes."""
import modal

app = modal.App("bajar-h3", image=modal.Image.debian_slim(python_version="3.12").pip_install("huggingface_hub[hf_transfer]"))
vol = modal.Volume.from_name("h3-comprimido-gastro", create_if_missing=True)

ARCHIVOS = [
    "diffusion_models/minimax_h3_fl2va_pruned_fp8_scaled.safetensors",
    "loras/minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors",
    "text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors",
    "vae/minimax_h3_video_vae_fp16.safetensors",
    "vae/minimax_h3_audio_vae_fp32.safetensors",
]


@app.function(volumes={"/datos": vol}, timeout=7200, cpu=4, memory=16384)
def bajar():
    import os
    os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
    from huggingface_hub import hf_hub_download
    for a in ARCHIVOS:
        hf_hub_download("Comfy-Org/MiniMax-H3", a, local_dir="/datos/models")
        vol.commit()
    return sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk("/datos/models") for f in fs) / 1e9


@app.local_entrypoint()
def main():
    print("GB descargados:", round(bajar.remote(), 1))
