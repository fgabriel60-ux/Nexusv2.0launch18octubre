#!/usr/bin/env python3
"""Sustituye dos tramos de voz de Adrián por frases nuevas de Fish y rehace las palabras.

Glimmer (v22, 8.5/10) pidió, para llegar a 9.5:
  - gancho que nombre los estilos, en lugar de "¿Buscas un tatuaje en Cancún Centro?"
  - oferta que diga qué recibe al escribir CITA, en lugar de "asegura tu lugar"
Los huecos se respetan al milímetro para no mover ni un cuadro del video.
"""
import json, pathlib, subprocess, sys
import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
AQUI = pathlib.Path(__file__).resolve().parent
BASE = AQUI.parent / "del_cliente_1104/tatu_b.mp4"
PAL = AQUI.parent / "del_cliente_1104/palabras.json"
VOZ = AQUI.parent / "voz_v22"
SALIDA_VID = AQUI.parent / "del_cliente_1104/tatu_b_v23.mp4"
SALIDA_PAL = AQUI.parent / "del_cliente_1104/palabras_v23.json"
TMP = AQUI / "tmp_v23"; TMP.mkdir(exist_ok=True)

# (archivo de voz, inicio del hueco, fin del hueco) medidos sobre el audio actual
TRAMOS = [
    (VOZ / "gancho_t0.wav", 0.20, 3.00),    # antes: "¿Buscas un tatuaje en Cancún Centro?"
    (VOZ / "oferta_t0.wav", 8.58, 14.15),   # antes: "Escríbeme ahora y asegura tu lugar..."
]

def ff(a):
    r = subprocess.run([FF, "-y", "-v", "error", *a], capture_output=True, text=True)
    if r.returncode: print(r.stderr[-1500:]); sys.exit(1)

def dur(p):
    r = subprocess.run([FF, "-i", str(p)], capture_output=True, text=True)
    for t in r.stderr.split("Duration: ")[1:2]:
        hh, mm, ss = t.split(",")[0].split(":")
        return int(hh)*3600 + int(mm)*60 + float(ss)
    return 0.0

print("1) audio base a wav")
base_wav = TMP / "base.wav"
ff(["-i", str(BASE), "-vn", "-ac", "2", "-ar", "44100", str(base_wav)])
total = dur(base_wav)
print(f"   audio base {total:.2f}s")

print("2) cada frase nueva, ajustada EXACTO a su hueco")
piezas = []     # (ruta, inicio, fin) de las frases nuevas ya ajustadas
for i, (wav, t0, t1) in enumerate(TRAMOS):
    hueco = t1 - t0
    d = dur(wav)
    tempo = d / hueco
    dest = TMP / f"frase{i}.wav"
    # atempo acepta 0.5-2.0; aquí siempre caemos dentro
    ff(["-i", str(wav), "-filter:a", f"atempo={tempo:.5f},aresample=44100",
        "-ac", "2", "-ar", "44100", "-t", f"{hueco:.4f}", str(dest)])
    print(f"   {wav.name}: {d:.2f}s -> {hueco:.2f}s (atempo {tempo:.3f})")
    piezas.append((dest, t0, t1))

print("3) armado del audio nuevo")
# el original se silencia en los huecos y las frases nuevas se mezclan encima
ent, filtros, mezclar = ["-i", str(base_wav)], [], []
sil = "+".join(f"between(t,{t0},{t1})" for _, t0, t1 in piezas)
filtros.append(f"[0:a]volume='if({sil},0,1)':eval=frame[orig]")
mezclar.append("[orig]")
for i, (p, t0, t1) in enumerate(piezas):
    ent += ["-i", str(p)]
    filtros.append(f"[{i+1}:a]adelay={int(t0*1000)}|{int(t0*1000)},"
                   f"apad=whole_dur={total:.3f}[f{i}]")
    mezclar.append(f"[f{i}]")
filtros.append("".join(mezclar) + f"amix=inputs={len(mezclar)}:duration=first:normalize=0[out]")
nuevo_wav = TMP / "nuevo.wav"
ff(ent + ["-filter_complex", ";".join(filtros), "-map", "[out]",
          "-ac", "2", "-ar", "44100", str(nuevo_wav)])

print("4) video con el audio nuevo")
ff(["-i", str(BASE), "-i", str(nuevo_wav), "-map", "0:v", "-map", "1:a",
    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
    str(SALIDA_VID)])

print("5) palabras nuevas para los subtítulos")
from faster_whisper import WhisperModel
m = WhisperModel("medium", device="cpu", compute_type="int8")
pal = json.loads(PAL.read_text())
# se quedan las palabras que NO caen en un hueco
fuera = [p for p in pal if not any(t0 - 0.05 <= p["t"] < t1 for _, t0, t1 in piezas)]
nuevas = []
for p, t0, t1 in piezas:
    seg, _ = m.transcribe(str(p), language="es", word_timestamps=True)
    for s in seg:
        for w in s.words:
            nuevas.append({"p": w.word.strip(), "t": round(t0 + w.start, 2),
                           "f": round(min(t0 + w.end, t1), 2)})
todas = sorted(fuera + nuevas, key=lambda x: x["t"])
SALIDA_PAL.write_text(json.dumps(todas, ensure_ascii=False))
print(f"   {len(fuera)} palabras del original + {len(nuevas)} nuevas = {len(todas)}")
print("\nlisto:", SALIDA_VID, "\n      ", SALIDA_PAL)
