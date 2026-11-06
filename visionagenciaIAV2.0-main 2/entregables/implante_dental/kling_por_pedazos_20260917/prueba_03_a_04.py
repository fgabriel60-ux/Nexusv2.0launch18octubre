"""Prueba de Kling por pedazos (Carlos, 17 sep 2026: «si haz una prueba de 5 segundos»).

Clip difícil del video de Alberto: 03 anestesia → 04 el rostro se despega como sticker y revela el maxilar.
kwaivgi/kling-v2.6-pro/image-to-video con image + end_image, 5 s, sin sonido. Mide el saldo de WaveSpeed
antes y después, porque en las pruebas del 16 sep el costo real salió hasta 11 veces el de lista.
Uso: python3 prueba_03_a_04.py"""
import json, os, sys, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
DENTAL = os.path.dirname(AQUI)
sys.path.insert(0, os.path.join(DENTAL, "kling_transicion"))
sys.path.insert(0, os.path.join(DENTAL, "..", "catania_mariano_montaje_20260914"))
import gancho_kling_habla_giro as g
from kling_transicion import cuadro_916

INICIO = os.path.join(AQUI, "03_anestesia.png")
FIN = os.path.join(AQUI, "04_sticker_revela.png")
SALIDA = os.path.join(AQUI, "PRUEBA_KLING_03_A_04.mp4")

PROMPT = (
    "Extreme macro close-up of the same woman's smile with one missing upper front tooth. The slim dental syringe "
    "slowly pulls back and leaves the frame. Then her face and lips peel away from the right side like a glossy "
    "photographic sticker: the skin curls smoothly toward the left, showing its pale paper-like back and a thin warm "
    "glowing edge, revealing behind it a clean front cross-section of the UPPER jaw: porous cream bone, glowing "
    "translucent pink gum, the upper front teeth hanging down with their long roots going up, and a titanium implant "
    "inside the bone above the gap. The camera eases slightly back to the final framing and ends exactly at the "
    "final image. One smooth continuous motion. Dark background with teal and warm orange bokeh, soft teal rim "
    "light. Clean medical visualisation, calm and elegant."
)
NEG = ("blood, gore, wound, open flesh, extra teeth, duplicated teeth, teeth changing count, lower jaw, molars, "
       "deformed mouth, face identity change, melting skin, morphing, flicker, jump cut, crossfade dissolve, "
       "text, labels, watermark, camera shake, low quality")


def saldo():
    req = urllib.request.Request(g.WAVESPEED + "/balance", headers=g.CAB)
    try:
        return json.loads(urllib.request.urlopen(req, timeout=60).read()).get("data", {}).get("balance")
    except Exception as e:
        return "sin dato (%s)" % e


if __name__ == "__main__":
    g.ESTADO = os.path.join(AQUI, "estado_prueba.json")
    antes = saldo()
    print("saldo antes:", antes, flush=True)
    g.paso("clip_03_04", "kwaivgi/kling-v2.6-pro/image-to-video",
           lambda: dict(image=cuadro_916(INICIO), end_image=cuadro_916(FIN), prompt=PROMPT, negative_prompt=NEG,
                        duration=5, sound=False),
           SALIDA)
    despues = saldo()
    print("saldo despues:", despues, flush=True)
    g.guarda("saldo", {"antes": antes, "despues": despues})
