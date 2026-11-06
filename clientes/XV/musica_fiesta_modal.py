"""Música original para el reel XV (MusicGen en Modal): tema suave y emotivo para la parte de fotos/planos mágicos. Uso: modal run musica_modal.py"""
import io, pathlib
import modal

imagen = modal.Image.debian_slim(python_version="3.12").pip_install("torch", "transformers", "scipy", "accelerate")
app = modal.App("xv-musica-fiesta", image=imagen)
PROMPT = ("upbeat modern latin pop dance track for a quinceanera party, bright energetic beat around 112 bpm, punchy drums, bass, shiny synths and claps, festive and joyful, cinematic reel energy, "
          "no vocals, clean professional mix")


@app.function(gpu="A100-80GB", timeout=1800)
def generar(seg: int = 20, semilla: int = 7) -> bytes:
    import torch, scipy.io.wavfile as wav, numpy as np
    from transformers import AutoProcessor, MusicgenForConditionalGeneration
    torch.manual_seed(semilla)
    proc = AutoProcessor.from_pretrained("facebook/musicgen-medium")
    modelo = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-medium").to("cuda")
    ent = proc(text=[PROMPT], padding=True, return_tensors="pt").to("cuda")
    audio = modelo.generate(**ent, do_sample=True, guidance_scale=3.0, max_new_tokens=int(seg * 50))
    sr = modelo.config.audio_encoder.sampling_rate
    b = io.BytesIO(); wav.write(b, sr, audio[0, 0].cpu().numpy().astype(np.float32)); return b.getvalue()


@app.local_entrypoint()
def main(seg: int = 20, semilla: int = 7):
    aqui = pathlib.Path(__file__).resolve().parent
    (aqui / f"musica_fiesta_s{semilla}.wav").write_bytes(generar.remote(seg, semilla))
    print("guardado", aqui / f"musica_fiesta_s{semilla}.wav")
