#!/usr/bin/env python3
"""Mariano v3: arregla lo que marco Glimmer en la v2 (6/10).

 - CORTA la cola que decia "¿QUE HAY DE NUEVO EN SAN MARINO?" (desarrollo VIEJO, error de marca).
 - Texto de filtro en el gancho: Rosarito/Tijuana + precio, para abaratar el mensaje.
 - Cierre nuevo con voz clonada: Bugambilia es la unica con plaza comercial y area de juegos,
   y aceptamos Infonavit y credito hipotecario.
El texto va en capas PNG hechas con PIL: este ffmpeg no trae drawtext.
"""
import os, subprocess, sys
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

FF = imageio_ffmpeg.get_ffmpeg_exe()
RAIZ = "/workspaces/Nexusv2.0launch18octubre"
BASE = f"{RAIZ}/entregables/mariano_v2_20261105"
OUT = f"{BASE}/armado"
V2 = f"{BASE}/Mariano_Vizcaino_v2.mp4"
VOZ_CIERRE = f"{RAIZ}/clientes/Mariano/gancho_rapel/voz/cierre_t0.wav"
TTF = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
CORTE = 31.72          # justo antes de que entre "EN SAN MARINO?"
CONGELA_EN = 30.60     # frame de la tarjeta final, limpio
W, H = 720, 1280
AZUL = (11, 31, 58)
ORO = (255, 201, 77)
VERDE = (30, 122, 70)

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

def capa(lineas, destino):
    """lineas: lista de (texto, y, px, color_letra, color_caja, alpha_caja)."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for texto, y, px, letra, caja, al in lineas:
        f = ImageFont.truetype(TTF, px)
        x0, y0, x1, y1 = d.textbbox((0, 0), texto, font=f)
        an, al_t = x1 - x0, y1 - y0
        x = (W - an) // 2
        pad_x, pad_y = int(px * 0.45), int(px * 0.34)
        d.rounded_rectangle([x - pad_x, y - pad_y, x + an + pad_x, y + al_t + pad_y * 2],
                            radius=int(px * 0.3), fill=caja + (al,))
        d.text((x - x0, y - y0), texto, font=f, fill=letra + (255,))
    im.save(destino)
    return destino

print("1) cuerpo sin la cola de San Marino, con texto de filtro en el gancho")
# el filtro de publico vive entre 0.6s y 5.4s (mientras baja en rapel)
c_filtro = capa([
    ("ROSARITO Y TIJUANA", 104, 40, (255, 255, 255), AZUL, 217),
    ("Casas desde $2.45 MDP", 176, 36, ORO, AZUL, 217),
    ("Privada con acceso controlado", 1040, 31, (255, 255, 255), AZUL, 217),
], f"{OUT}/v3_capa_filtro.png")

cuerpo = f"{OUT}/v3_cuerpo.mp4"
corre(["-i", V2, "-i", c_filtro,
       "-filter_complex",
       "[1:v]format=rgba,fade=t=in:st=0.6:d=0.3:alpha=1,"
       "fade=t=out:st=5.1:d=0.3:alpha=1[cap];"
       "[0:v][cap]overlay=0:0:enable='between(t,0.6,5.4)'[v]",
       "-map", "[v]", "-map", "0:a",
       "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
       "-t", f"{CORTE}", cuerpo], "cuerpo")

print("2) cierre con la voz nueva (Infonavit + lo unico de Bugambilia)")
segv = dura(VOZ_CIERRE)
seg = segv + 1.4
fondo = f"{OUT}/v3_frame_cierre.png"
corre(["-ss", f"{CONGELA_EN}", "-i", V2, "-frames:v", "1", fondo], "frame del cierre")

c_a = capa([
    ("La UNICA con plaza comercial", 296, 38, ORO, AZUL, 235),
    ("y area de juegos", 364, 38, ORO, AZUL, 235),
], f"{OUT}/v3_capa_c1.png")
c_b = capa([
    ("Aceptamos INFONAVIT", 474, 36, (255, 255, 255), VERDE, 235),
    ("y credito hipotecario", 540, 36, (255, 255, 255), VERDE, 235),
], f"{OUT}/v3_capa_c2.png")
c_c = capa([
    ("Recorrido GRATIS, sin compromiso", 1024, 30, (255, 255, 255), AZUL, 235),
    ("Escribe BUGAMBILIA por WhatsApp", 1086, 30, ORO, AZUL, 235),
], f"{OUT}/v3_capa_c3.png")

cierre = f"{OUT}/v3_cierre.mp4"
corre(["-loop", "1", "-framerate", "30", "-t", f"{seg:.3f}", "-i", fondo,
       "-i", VOZ_CIERRE,
       "-loop", "1", "-i", c_a, "-loop", "1", "-i", c_b, "-loop", "1", "-i", c_c,
       "-filter_complex",
       f"[0:v]scale={W}:{H},setsar=1,fps=30[bg];"
       "[2:v]format=rgba,fade=t=in:st=0.25:d=0.3:alpha=1[ca];"
       "[3:v]format=rgba,fade=t=in:st=1.9:d=0.3:alpha=1[cb];"
       "[4:v]format=rgba,fade=t=in:st=3.1:d=0.3:alpha=1[cc];"
       "[bg][ca]overlay=0:0:enable='gte(t,0.25)'[v1];"
       "[v1][cb]overlay=0:0:enable='gte(t,1.9)'[v2];"
       "[v2][cc]overlay=0:0:enable='gte(t,3.1)'[v];"
       f"[1:a]adelay=300|300,apad,atrim=0:{seg:.3f},afade=t=out:st={seg-0.6:.2f}:d=0.6[a]",
       "-map", "[v]", "-map", "[a]", "-t", f"{seg:.3f}",
       "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2", cierre], "cierre")

print("3) pegado")
lista = f"{OUT}/lista_v3.txt"
with open(lista, "w") as f:
    f.write(f"file '{cuerpo}'\nfile '{cierre}'\n")
final = f"{BASE}/Mariano_Vizcaino_v3.mp4"
corre(["-f", "concat", "-safe", "0", "-i", lista,
       "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
       "-movflags", "+faststart", final], "final")

print(f"\nlisto: {final}  {dura(final):.2f}s")
print(f"  cuerpo {dura(cuerpo):.2f}s + cierre {dura(cierre):.2f}s")
