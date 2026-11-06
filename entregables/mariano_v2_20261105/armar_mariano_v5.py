#!/usr/bin/env python3
"""Mariano v5. Lo que pidió Carlos el 6 nov 2026:

  - fuera la primera escena del rapel (M1): el gancho arranca ya cerca
  - fuera la escena de Mariano del video original (él sentado en la mesa):
    el único Mariano que sale es el del gancho nuevo
  - efectos de sonido hechos a mano, porque los de H3 no servían
"""
import subprocess, sys
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/entregables/mariano_v2_20261105")
import imageio_ffmpeg
import efectos as fx
from PIL import Image, ImageDraw, ImageFont

FF = imageio_ffmpeg.get_ffmpeg_exe()
RAIZ = "/workspaces/Nexusv2.0launch18octubre"
BASE = f"{RAIZ}/entregables/mariano_v2_20261105"
CU = f"{BASE}/cuadros"
OUT = f"{BASE}/armado5"
VOZ_GANCHO = f"{RAIZ}/clientes/Mariano/gancho_rapel/voz/gancho_t1.wav"
VOZ_CIERRE = f"{RAIZ}/clientes/Mariano/gancho_rapel/voz/cierre_t0.wav"
CUERPO = f"{RAIZ}/clientes/Mariano/video/Vizcaino_Mariano_v8_cuerda.mp4"
TTF = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
# del video original se toma solo la parte de las casas:
CUERPO_DESDE = 6.05     # justo antes de "mira esta casa de dos pisos"
CUERPO_HASTA = 24.00    # antes de que entre la tarjeta final con él sentado a la mesa
FONDO_CIERRE = 21.40    # frame de la sala, para el cierre: ahí no sale él
W, H = 720, 1280
AZUL, ORO, VERDE = (11, 31, 58), (255, 201, 77), (30, 122, 70)

import os
os.makedirs(OUT, exist_ok=True)

def corre(args, etiqueta):
    r = subprocess.run([FF, "-y", "-v", "error", *args], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"FALLO {etiqueta}:\n{r.stderr[-1800:]}"); sys.exit(1)
    print(f"  ok {etiqueta}")

def dura(ruta):
    r = subprocess.run([FF, "-i", ruta], capture_output=True, text=True)
    for t in r.stderr.split("Duration: ")[1:2]:
        hh, mm, ss = t.split(",")[0].split(":")
        return int(hh)*3600 + int(mm)*60 + float(ss)
    return 0.0

def capa(lineas, destino, panel=None):
    """panel=(y0,y1): franja opaca que tapa el texto que ya trae el frame de fondo."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if panel:
        y0p, y1p = panel
        d.rectangle([0, y0p, W, y1p], fill=AZUL + (248,))
    for texto, y, px, letra, caja, al in lineas:
        f = ImageFont.truetype(TTF, px)
        x0, y0, x1, y1 = d.textbbox((0, 0), texto, font=f)
        an, alt = x1 - x0, y1 - y0
        x = (W - an) // 2
        ex, ey = int(px * .45), int(px * .34)
        # con alfa 0 NO se dibuja la caja: PIL reemplaza el píxel en vez de mezclarlo,
        # así que una caja transparente abriría un agujero en el panel de abajo
        if al > 0:
            d.rounded_rectangle([x-ex, y-ey, x+an+ex, y+alt+ey*2], radius=int(px*.3),
                                fill=caja+(al,))
        d.text((x - x0, y - y0), texto, font=f, fill=letra + (255,))
    im.save(destino); return destino

# ---------------- gancho: M2 + M3 + M4 (sin M1) ----------------
print("1) gancho sin la primera escena, con efectos propios")
# (clip, velocidad, constructor de la pista de sonido)
PLAN = [("M2_cerca", 1.70, "aire"), ("M3_arnes", 1.50, "suelo"), ("M4_habla", 1.00, "voz")]
piezas = []
for nombre, vel, tipo in PLAN:
    src = f"{CU}/{nombre}.mp4"
    seg = dura(src) / vel
    dest = f"{OUT}/g_{nombre}.mp4"
    if tipo == "voz":
        corre(["-i", src, "-i", VOZ_GANCHO,
               "-filter_complex", f"[0:v]scale={W}:-2,crop={W}:{H},setsar=1,fps=30[v]",
               "-map", "[v]", "-map", "1:a",
               "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-pix_fmt", "yuv420p",
               "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
               "-shortest", dest], nombre)
    else:
        if tipo == "aire":
            # sigue descendiendo: aire fuerte y la cuerda corriendo por el guante
            pistas = [fx.viento(seg, 0.34, altura=1.25, semilla=7),
                      fx.roce_cuerda(seg, 0.26, semilla=11)]
        else:
            # ya en el suelo: el aire baja, entran los pies y la hebilla
            pistas = [fx.viento(seg, 0.13, altura=0.7, semilla=19),
                      fx.pisada(seg, en=0.05, fuerza=0.50),
                      fx.hebilla(seg, en=0.42, fuerza=0.80)]
        pista = fx.guarda(f"{OUT}/fx_{nombre}.wav", fx.mezcla_estereo(pistas, seg))
        # -map explícito: el audio que H3 inventó (con voces) no entra
        corre(["-i", src, "-i", str(pista),
               "-filter_complex",
               f"[0:v]setpts=PTS/{vel},scale={W}:-2,crop={W}:{H},setsar=1,fps=30[v]",
               "-map", "[v]", "-map", "1:a",
               "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-pix_fmt", "yuv420p",
               "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
               "-t", f"{seg:.3f}", dest], nombre)
    piezas.append(dest)

# ---------------- cuerpo: solo las casas ----------------
print("2) cuerpo: solo casas, sin la escena de él")
cuerpo = f"{OUT}/cuerpo.mp4"
corre(["-ss", f"{CUERPO_DESDE}", "-to", f"{CUERPO_HASTA}", "-i", CUERPO,
       "-vf", f"scale={W}:{H},setsar=1,fps=30",
       "-af", "afade=t=in:d=0.25,afade=t=out:st="
              f"{CUERPO_HASTA - CUERPO_DESDE - 0.35:.2f}:d=0.35",
       "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2", cuerpo], "cuerpo")
piezas.append(cuerpo)

# ---------------- cierre: sobre la sala, no sobre él ----------------
print("3) cierre")
segv = dura(VOZ_CIERRE); seg = segv + 1.6
fondo = f"{OUT}/frame_cierre.png"
corre(["-ss", f"{FONDO_CIERRE}", "-i", CUERPO, "-frames:v", "1",
       "-vf", f"scale={W}:{H}", fondo], "frame del cierre")

c1 = capa([("BUGAMBILIA es la UNICA", 180, 36, ORO, AZUL, 240),
           ("con plaza comercial", 244, 36, ORO, AZUL, 240),
           ("y area de juegos", 308, 36, ORO, AZUL, 240)], f"{OUT}/c1.png", panel=(0, 130))
c2 = capa([("Aceptamos INFONAVIT", 420, 35, (255,255,255), VERDE, 240),
           ("y credito hipotecario", 484, 35, (255,255,255), VERDE, 240)], f"{OUT}/c2.png")
c3 = capa([("CASA BUGAMBILIA · 2 PISOS", 892, 32, (255,255,255), AZUL, 0),
           ("Desde $2.45 MDP · Rosarito", 952, 28, ORO, AZUL, 0),
           ("Mariano Herrera · Asesor inmobiliario", 1012, 25, (255,255,255), AZUL, 0),
           ("Recorrido GRATIS, sin compromiso", 1070, 26, (255,255,255), AZUL, 0),
           ("Escribe BUGAMBILIA · 664 233 4848", 1134, 26, ORO, VERDE, 242)],
          f"{OUT}/c3.png", panel=(856, H))

cierre = f"{OUT}/cierre.mp4"
corre(["-loop", "1", "-framerate", "30", "-t", f"{seg:.3f}", "-i", fondo,
       "-i", VOZ_CIERRE, "-loop", "1", "-i", c1, "-loop", "1", "-i", c2, "-loop", "1", "-i", c3,
       "-filter_complex",
       f"[0:v]scale={W}:{H},setsar=1,eq=brightness=-0.06,fps=30[bg];"
       "[2:v]format=rgba,fade=t=in:st=0.20:d=0.3:alpha=1[ca];"
       "[3:v]format=rgba,fade=t=in:st=2.0:d=0.3:alpha=1[cb];"
       "[4:v]format=rgba,fade=t=in:st=0.45:d=0.3:alpha=1[cc];"
       "[bg][ca]overlay=0:0:enable='gte(t,0.20)'[v1];"
       "[v1][cb]overlay=0:0:enable='gte(t,2.0)'[v2];"
       "[v2][cc]overlay=0:0:enable='gte(t,0.45)'[v];"
       f"[1:a]adelay=300|300,apad,atrim=0:{seg:.3f},afade=t=out:st={seg-0.6:.2f}:d=0.6[a]",
       "-map", "[v]", "-map", "[a]", "-t", f"{seg:.3f}",
       "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2", cierre], "cierre")
piezas.append(cierre)

print("4) pegado")
lista = f"{OUT}/lista.txt"
open(lista, "w").write("".join(f"file '{p}'\n" for p in piezas))
final = f"{BASE}/Mariano_Vizcaino_v5.mp4"
corre(["-f", "concat", "-safe", "0", "-i", lista,
       "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
       "-movflags", "+faststart", final], "final")
print(f"\nlisto: {final}  {dura(final):.2f}s")
for p in piezas: print(f"  {p.split('/')[-1]:20s} {dura(p):5.2f}s")
