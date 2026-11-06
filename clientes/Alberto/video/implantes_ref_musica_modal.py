"""Música original de fondo (MusicGen medium en Modal) para el reel de implantes: pop corporativo ligero y positivo, como la de los reels dentales.
Uso: MODAL_PROFILE=fabelagabriel645 modal run implantes_ref_musica_modal.py"""
import io, pathlib
import modal

imagen = modal.Image.debian_slim(python_version="3.12").pip_install("torch", "transformers", "scipy", "accelerate")
app = modal.App("alberto-implantes-musica", image=imagen)
PROMPT = ("modern upbeat corporate pop background music for a social media reel, light plucked synths, soft claps and a gentle four on the floor beat, "
          "warm bass, positive and confident, clean, 105 bpm, no vocals")


@app.function(gpu="A10G", timeout=1800)
def generar(seg: int = 30, semilla: int = 4) -> bytes:
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
def main(seg: int = 30, semilla: int = 4):
    aqui = pathlib.Path(__file__).resolve().parent / "implantes_ref"
    aqui.mkdir(exist_ok=True)
    (aqui / "musica.wav").write_bytes(generar.remote(seg, semilla))
    print("guardado", aqui / "musica.wav")
