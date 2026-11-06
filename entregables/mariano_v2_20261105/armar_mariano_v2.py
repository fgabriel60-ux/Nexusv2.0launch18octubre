#!/usr/bin/env python3
"""Mariano Vizcaino v2: gancho de rapel (cara del character sheet) + cuerpo Bugambilia.

Reglas aplicadas:
 - MiniMax H3 NO deja voces: a las 3 tomas de ambiente se les QUITA el audio con -map
   explicito y se les pone sonido sintetico propio de la escena.
 - A la toma que habla se le re-pega el WAV original de Fish (H3 altera la voz).
 - El cuerpo entra sin su gancho viejo, para no repetir el "buscas casa en Rosarito".
"""
import json, os, subprocess, sys
import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
RAIZ = "/workspaces/Nexusv2.0launch18octubre"
CU = f"{RAIZ}/entregables/mariano_v2_20261105/cuadros"
OUT = f"{RAIZ}/entregables/mariano_v2_20261105/armado"
VOZ = f"{RAIZ}/clientes/Mariano/gancho_rapel/voz/gancho_t1.wav"
CUERPO = f"{RAIZ}/clientes/Mariano/video/Vizcaino_Mariano_v8_cuerda.mp4"
CUERPO_DESDE = 6.05          # justo antes de "mira esta casa de dos pisos"
W, H = 720, 1280

def corre(args, etiqueta):
    r = subprocess.run([FF, "-y", "-v", "error", *args], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"FALLO {etiqueta}:\n{r.stderr[-1500:]}")
        sys.exit(1)
    print(f"  ok {etiqueta}")

def dura(ruta):
    r = subprocess.run([FF, "-i", ruta], capture_output=True, text=True)
    for t in r.stderr.split("Duration: ")[1:2]:
        hh, mm, ss = t.split(",")[0].split(":")
        return int(hh) * 3600 + int(mm) * 60 + float(ss)
    return 0.0

# ---------- sonidos de la escena (sin voces, sintetizados) ----------
def viento(dest, seg, fuerza=0.22):
    """Aire de altura: ruido rosa filtrado, con rachas lentas."""
    corre(["-f", "lavfi", "-i", f"anoisesrc=color=pink:r=44100:amplitude=0.9:d={seg}",
           "-af", (f"lowpass=f=620,highpass=f=70,"
                   f"tremolo=f=0.45:d=0.6,volume={fuerza},"
                   f"afade=t=in:d=0.3,afade=t=out:st={max(0,seg-0.4):.2f}:d=0.4"),
           "-ac", "2", "-ar", "44100", dest], f"viento {os.path.basename(dest)}")

def roce_cuerda(dest, seg, fuerza=0.16):
    """Roce de la cuerda en el guante: ruido marron en banda media, pulsado."""
    corre(["-f", "lavfi", "-i", f"anoisesrc=color=brown:r=44100:amplitude=0.9:d={seg}",
           "-af", (f"bandpass=f=900:width_type=h:width=700,"
                   f"tremolo=f=2.6:d=0.75,volume={fuerza},"
                   f"afade=t=in:d=0.2,afade=t=out:st={max(0,seg-0.3):.2f}:d=0.3"),
           "-ac", "2", "-ar", "44100", dest], f"cuerda {os.path.basename(dest)}")

def chasquido(dest, seg, en=0.35):
    """Hebilla metalica que se zafa + la correa al caer."""
    corre(["-f", "lavfi", "-i", f"anoisesrc=color=white:r=44100:amplitude=0.9:d={seg}",
           "-af", (f"bandpass=f=2600:width_type=h:width=1800,"
                   f"volume='if(between(t,{en},{en+0.045}),2.4,"
                   f"if(between(t,{en+0.33},{en+0.42}),1.1,0.02))':eval=frame,"
                   f"highpass=f=300"),
           "-ac", "2", "-ar", "44100", dest], f"hebilla {os.path.basename(dest)}")

def mezcla(dest, pistas):
    args = []
    for p in pistas:
        args += ["-i", p]
    n = len(pistas)
    args += ["-filter_complex", f"amix=inputs={n}:duration=longest:normalize=0[a]",
             "-map", "[a]", "-ac", "2", "-ar", "44100", dest]
    corre(args, f"mezcla {os.path.basename(dest)}")

# ---------- tomas ----------
# (clip, velocidad, constructor de audio)
TOMAS = [
    ("M1_rapel", 1.50, "viento_fuerte"),
    ("M2_cerca", 1.75, "viento_cuerda"),
    ("M3_arnes", 1.55, "hebilla"),
    ("M4_habla", 1.00, "voz_fish"),
]

print("1) tomas del gancho")
piezas = []
for nombre, vel, audio in TOMAS:
    src = f"{CU}/{nombre}.mp4"
    seg = dura(src) / vel
    dest = f"{OUT}/t_{nombre}.mp4"

    if audio == "voz_fish":
        # video de H3 + el WAV original de Fish. -map explicito: el audio de H3 se tira.
        corre(["-i", src, "-i", VOZ,
               "-filter_complex",
               f"[0:v]scale={W}:-2,crop={W}:{H},setsar=1,fps=30[v]",
               "-map", "[v]", "-map", "1:a",
               "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-pix_fmt", "yuv420p",
               "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
               "-shortest", dest], nombre)
    else:
        fx = f"{OUT}/fx_{nombre}.wav"
        if audio == "viento_fuerte":
            viento(fx, seg, 0.26)
        elif audio == "viento_cuerda":
            a, b = f"{OUT}/fx_{nombre}_a.wav", f"{OUT}/fx_{nombre}_b.wav"
            viento(a, seg, 0.20); roce_cuerda(b, seg, 0.18); mezcla(fx, [a, b])
        else:
            a, b = f"{OUT}/fx_{nombre}_a.wav", f"{OUT}/fx_{nombre}_b.wav"
            chasquido(a, seg, 0.30); viento(b, seg, 0.10); mezcla(fx, [a, b])
        # -map explicito: el audio que H3 metio (con voces) NO entra
        corre(["-i", src, "-i", fx,
               "-filter_complex",
               f"[0:v]setpts=PTS/{vel},scale={W}:-2,crop={W}:{H},setsar=1,fps=30[v]",
               "-map", "[v]", "-map", "1:a",
               "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-pix_fmt", "yuv420p",
               "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
               "-t", f"{seg:.3f}", dest], nombre)
    piezas.append(dest)

print("2) cuerpo sin su gancho viejo")
cuerpo = f"{OUT}/t_cuerpo.mp4"
corre(["-ss", f"{CUERPO_DESDE}", "-i", CUERPO,
       "-vf", f"scale={W}:{H},setsar=1,fps=30",
       "-af", "afade=t=in:d=0.25",
       "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2", cuerpo], "cuerpo")
piezas.append(cuerpo)

print("3) pegado")
lista = f"{OUT}/lista.txt"
with open(lista, "w") as f:
    for p in piezas:
        f.write(f"file '{p}'\n")
final = f"{RAIZ}/entregables/mariano_v2_20261105/Mariano_Vizcaino_v2.mp4"
corre(["-f", "concat", "-safe", "0", "-i", lista,
       "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
       "-movflags", "+faststart", final], "final")

print("\nlisto:", final, f"{dura(final):.2f}s")
for p in piezas:
    print(f"  {os.path.basename(p):22s} {dura(p):5.2f}s")
