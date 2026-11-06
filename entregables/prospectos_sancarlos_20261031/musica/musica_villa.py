"""Música original para reels de rentas vacacionales (MusicGen medium, GPU L4 barata). modal run musica_villa.py --semilla N"""
import io, pathlib
import modal
imagen = modal.Image.debian_slim(python_version="3.12").pip_install("torch", "transformers", "scipy", "accelerate")
app = modal.App("musica-villa", image=imagen)
PROMPT = ("chill tropical deep house, warm relaxed summer vibe, soft plucked guitar and marimba, smooth groove, 115 bpm, "
          "luxury resort lounge, sunny beach villa, steady beat for fast video cuts, no vocals")

@app.function(gpu="L4", timeout=1800)
def generar(seg: int = 16, semillas: list = [3]) -> dict:
    import torch, scipy.io.wavfile as wav, numpy as np
    from transformers import AutoProcessor, MusicgenForConditionalGeneration
    proc = AutoProcessor.from_pretrained("facebook/musicgen-medium")
    modelo = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-medium", torch_dtype=torch.float16).to("cuda")
    out = {}
    for s in semillas:
        torch.manual_seed(s)
        ent = proc(text=[PROMPT], padding=True, return_tensors="pt").to("cuda")
        audio = modelo.generate(**ent, do_sample=True, guidance_scale=3.0, max_new_tokens=int(seg * 50))
        b = io.BytesIO(); wav.write(b, modelo.config.audio_encoder.sampling_rate, audio[0, 0].float().cpu().numpy()); out[s] = b.getvalue()
    return out

@app.local_entrypoint()
def main(seg: int = 16):
    aqui = pathlib.Path(__file__).resolve().parent
    for s, b in generar.remote(seg, [3, 11]).items():
        (aqui / f"villa_s{s}.wav").write_bytes(b); print("guardado", s)
