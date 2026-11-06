"""Corrige la toma 6 (T6_gui_mensaje) del Pixar v2: Guillermo salía con sombrero de ala ancha; ahora el mismo personaje de GUI2 (gorra gris y careta) bajo la pérgola negra."""
import json, pathlib, sys
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/_productor")
from escenas_modal import app, escenas

AQUI = pathlib.Path(__file__).resolve().parent
G = AQUI.parent


@app.local_entrypoint()
def main(semilla: int = 33):
    t = [x for x in json.load(open(AQUI / "plan.json"))["tomas"] if x[0] == "T6_gui_mensaje"][0]
    cuadros = {"GUI3": (["gui", "perg"], "Conserva EXACTAMENTE al mismo personaje animado de la primera imagen (misma cara, bigote, gorra gris de trabajo con la careta de soldar levantada encima, camisa azul, guantes de cuero). NO lleva sombrero. Ahora está de pie bajo una pérgola metálica negra (usa la segunda imagen como fondo), sosteniendo un celular con una pantalla verde de chat sin texto legible, sonriendo esperanzado a cámara. Plano medio de cabeza a cintura. Estilo Pixar, vertical, sin texto.")}
    refs = {"gui": (AQUI / "salida/GUI2.png").read_bytes(), "perg": (G / "obrero_20261029/ref_pergola_negra.jpg").read_bytes()}
    voces = {"g_mensaje": (G / "obrero_20261029/voz/g_mensaje.wav").read_bytes()}
    for n, v in escenas.remote("guillermo_pixar_v2_20261030", refs, cuadros, [tuple(t)], semilla, None, voces, (704, 1280)).items():
        (AQUI / "salida" / n).write_bytes(v); print("guardado", n)
