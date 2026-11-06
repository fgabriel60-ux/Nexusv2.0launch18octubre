"""Tiempos por palabra de la voz (faster-whisper) -> voz/palabras.json."""
import json, subprocess
from pathlib import Path
import imageio_ffmpeg, numpy as np
from faster_whisper import WhisperModel

AQUI = Path(__file__).resolve().parent
raw = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-v', 'error', '-i', str(AQUI / 'voz' / 'guion2.mp3'), '-f', 'f32le', '-ac', '1', '-ar', '16000', '-'], capture_output=True).stdout
segs, _ = WhisperModel('base', device='cpu', compute_type='int8').transcribe(np.frombuffer(raw, dtype=np.float32), language='es', word_timestamps=True)
P = [(w.word.strip(), round(float(w.start), 2), round(float(w.end), 2)) for s in segs for w in s.words]
(AQUI / 'voz' / 'palabras2.json').write_text(json.dumps(P, ensure_ascii=False))
print([(w, s) for w, s, e in P])
