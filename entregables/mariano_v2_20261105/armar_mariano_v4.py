#!/usr/bin/env python3
"""Mariano v4: lo que Glimmer marco en la v3 (6/10 -> proyectado 8.5).

 - Tarjeta fija BUGAMBILIA + 2 pisos + precio mientras el asesor habla y se ve la fachada
   (la v3 dejaba 5.9-8.6s sin nada en pantalla que confirmara modelo y precio).
 - El cierre nombra BUGAMBILIA, no "la unica": la voz decia el nombre y el texto no.
 - Lower third con su nombre, puesto y WhatsApp en el cierre, para subir Confianza.
"""
import subprocess, sys
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

FF = imageio_ffmpeg.get_ffmpeg_exe()
RAIZ = "/workspaces/Nexusv2.0launch18octubre"
BASE = f"{RAIZ}/entregables/mariano_v2_20261105"
OUT = f"{BASE}/armado"
V2 = f"{BASE}/Mariano_Vizcaino_v2.mp4"
VOZ_CIERRE = f"{RAIZ}/clientes/Mariano/gancho_rapel/voz/cierre_t0.wav"
TTF = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
CORTE = 31.72
CONGELA_EN = 30.60
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
    """lineas: (texto, y, px, color_letra, color_caja, alpha)."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for texto, y, px, letra, caja, al in lineas:
        f = ImageFont.truetype(TTF, px)
        x0, y0, x1, y1 = d.textbbox((0, 0), texto, font=f)
        an, alt = x1 - x0, y1 - y0
        x = (W - an) // 2
        px_, py_ = int(px * 0.45), int(px * 0.34)
        d.rounded_rectangle([x - px_, y - py_, x + an + px_, y + alt + py_ * 2],
                            radius=int(px * 0.3), fill=caja + (al,))
        d.text((x - x0, y - y0), texto, font=f, fill=letra + (255,))
    im.save(destino)
    return destino

print("1) cuerpo: filtro en el gancho + tarjeta fija de modelo y precio")
c_filtro = capa([
    ("ROSARITO Y TIJUANA", 104, 40, (255, 255, 255), AZUL, 217),
    ("Casas desde $2.45 MDP", 176, 36, ORO, AZUL, 217),
], f"{OUT}/v4_capa_filtro.png")
# Glimmer: 5.9-8.6s no habia nada que confirmara modelo ni precio. Esta tarjeta
# acompania todo el bloque en que habla y en que se ve la fachada.
c_ficha = capa([
    ("BUGAMBILIA · 2 PISOS", 104, 36, (255, 255, 255), AZUL, 222),
    ("Desde $2.45 MDP · Rosarito", 168, 30, ORO, AZUL, 222),
    ("Privada con acceso controlado", 1048, 29, (255, 255, 255), AZUL, 217),
], f"{OUT}/v4_capa_ficha.png")

cuerpo = f"{OUT}/v4_cuerpo.mp4"
corre(["-i", V2, "-i", c_filtro, "-i", c_ficha,
       "-filter_complex",
       "[1:v]format=rgba,fade=t=in:st=0.6:d=0.3:alpha=1,"
       "fade=t=out:st=5.0:d=0.3:alpha=1[cf];"
       "[2:v]format=rgba,fade=t=in:st=5.7:d=0.3:alpha=1,"
       "fade=t=out:st=12.6:d=0.4:alpha=1[cq];"
       "[0:v][cf]overlay=0:0:enable='between(t,0.6,5.3)'[v1];"
       "[v1][cq]overlay=0:0:enable='between(t,5.7,13.0)'[v]",
       "-map", "[v]", "-map", "0:a",
       "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
       "-t", f"{CORTE}", cuerpo], "cuerpo")

print("2) cierre: nombra BUGAMBILIA y lleva su credencial")
segv = dura(VOZ_CIERRE)
seg = segv + 1.4
fondo = f"{OUT}/v4_frame_cierre.png"
corre(["-ss", f"{CONGELA_EN}", "-i", V2, "-frames:v", "1", fondo], "frame del cierre")

# la voz dice "Bugambilia es la unica..."; el texto debe decir lo mismo
c_a = capa([
    ("BUGAMBILIA es la UNICA", 292, 36, ORO, AZUL, 238),
    ("con plaza comercial", 356, 36, ORO, AZUL, 238),
    ("y area de juegos", 420, 36, ORO, AZUL, 238),
], f"{OUT}/v4_capa_c1.png")
c_b = capa([
    ("Aceptamos INFONAVIT", 530, 35, (255, 255, 255), VERDE, 238),
    ("y credito hipotecario", 594, 35, (255, 255, 255), VERDE, 238),
], f"{OUT}/v4_capa_c2.png")
# Glimmer, Confianza 5->8: quien es y como lo contactan
c_c = capa([
    ("Mariano Herrera", 952, 32, (255, 255, 255), AZUL, 238),
    ("Asesor inmobiliario en Rosarito", 1010, 26, ORO, AZUL, 238),
    ("Recorrido GRATIS, sin compromiso", 1076, 27, (255, 255, 255), AZUL, 238),
    ("Escribe BUGAMBILIA · 664 233 4848", 1136, 27, ORO, VERDE, 238),
], f"{OUT}/v4_capa_c3.png")

cierre = f"{OUT}/v4_cierre.mp4"
corre(["-loop", "1", "-framerate", "30", "-t", f"{seg:.3f}", "-i", fondo,
       "-i", VOZ_CIERRE,
       "-loop", "1", "-i", c_a, "-loop", "1", "-i", c_b, "-loop", "1", "-i", c_c,
       "-filter_complex",
       f"[0:v]scale={W}:{H},setsar=1,fps=30[bg];"
       "[2:v]format=rgba,fade=t=in:st=0.25:d=0.3:alpha=1[ca];"
       "[3:v]format=rgba,fade=t=in:st=2.1:d=0.3:alpha=1[cb];"
       "[4:v]format=rgba,fade=t=in:st=3.3:d=0.3:alpha=1[cc];"
       "[bg][ca]overlay=0:0:enable='gte(t,0.25)'[v1];"
       "[v1][cb]overlay=0:0:enable='gte(t,2.1)'[v2];"
       "[v2][cc]overlay=0:0:enable='gte(t,3.3)'[v];"
       f"[1:a]adelay=300|300,apad,atrim=0:{seg:.3f},afade=t=out:st={seg-0.6:.2f}:d=0.6[a]",
       "-map", "[v]", "-map", "[a]", "-t", f"{seg:.3f}",
       "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2", cierre], "cierre")

print("3) pegado")
lista = f"{OUT}/lista_v4.txt"
with open(lista, "w") as f:
    f.write(f"file '{cuerpo}'\nfile '{cierre}'\n")
final = f"{BASE}/Mariano_Vizcaino_v4.mp4"
corre(["-f", "concat", "-safe", "0", "-i", lista,
       "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
       "-movflags", "+faststart", final], "final")
print(f"\nlisto: {final}  {dura(final):.2f}s")
