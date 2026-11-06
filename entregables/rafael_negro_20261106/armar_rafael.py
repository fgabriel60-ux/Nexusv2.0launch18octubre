#!/usr/bin/env python3
"""Rafael BYD, camisa negra: gancho de 3 tomas con el movimiento del reel de referencia.

H3 metió audio inventado en las dos tomas de calle (Whisper le oyó "¡Suscríbete!"),
así que se les quita con -map explícito y se les pone ambiente urbano propio.
A la toma que habla se le vuelve a pegar el WAV de Fish, porque H3 altera la voz.
"""
import os, subprocess, sys
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/entregables/mariano_v2_20261105")
import imageio_ffmpeg
import efectos as fx

FF = imageio_ffmpeg.get_ffmpeg_exe()
RAIZ = "/workspaces/Nexusv2.0launch18octubre"
BASE = f"{RAIZ}/entregables/rafael_negro_20261106"
CU, OUT = f"{BASE}/cuadros", f"{BASE}/armado"
VOZ = f"{RAIZ}/clientes/Rafael_BYD/voz_gancho/gancho_t2.wav"
W, H = 720, 1280
os.makedirs(OUT, exist_ok=True)

def corre(a, e):
    r = subprocess.run([FF, "-y", "-v", "error", *a], capture_output=True, text=True)
    if r.returncode: print(f"FALLO {e}:\n{r.stderr[-1500:]}"); sys.exit(1)
    print(f"  ok {e}")

def dura(p):
    r = subprocess.run([FF, "-i", p], capture_output=True, text=True)
    for t in r.stderr.split("Duration: ")[1:2]:
        hh, mm, ss = t.split(",")[0].split(":")
        return int(hh)*3600 + int(mm)*60 + float(ss)
    return 0.0

PLAN = [("R1_lejos_A", 1.0, "calle_auto"), ("R2_lejos_B", 1.0, "calle"), ("R3_adentro", 1.0, "voz")]
piezas = []
for nombre, vel, tipo in PLAN:
    src, dest = f"{CU}/{nombre}.mp4", f"{OUT}/{nombre}_ok.mp4"
    seg = dura(src) / vel
    if tipo == "voz":
        corre(["-i", src, "-i", VOZ,
               "-filter_complex", f"[0:v]scale={W}:-2,crop={W}:{H},setsar=1,fps=30[v]",
               "-map", "[v]", "-map", "1:a",
               "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-pix_fmt", "yuv420p",
               "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2", "-shortest", dest], nombre)
    else:
        pistas = [fx.calle(seg, 0.28, pasa_auto=(seg * 0.55 if tipo == "calle_auto" else None),
                           semilla=13 if tipo == "calle_auto" else 29)]
        pista = fx.guarda(f"{OUT}/fx_{nombre}.wav", fx.mezcla_estereo(pistas, seg))
        corre(["-i", src, "-i", str(pista),
               "-filter_complex", f"[0:v]scale={W}:-2,crop={W}:{H},setsar=1,fps=30[v]",
               "-map", "[v]", "-map", "1:a",
               "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-pix_fmt", "yuv420p",
               "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
               "-t", f"{seg:.3f}", dest], nombre)
    piezas.append(dest)

lista = f"{OUT}/lista.txt"
open(lista, "w").write("".join(f"file '{p}'\n" for p in piezas))
final = f"{BASE}/Rafael_BYD_gancho_negro.mp4"
corre(["-f", "concat", "-safe", "0", "-i", lista,
       "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
       "-movflags", "+faststart", final], "final")
print(f"\nlisto: {final}  {dura(final):.2f}s")
