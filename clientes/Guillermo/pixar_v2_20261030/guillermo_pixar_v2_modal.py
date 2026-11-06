"""Guillermo · Pixar v2 (30 oct): su audio de las 00:46 pide que el discurso sea de zaguanes, cortinas, puertas y pérgolas, «no tan voluminoso»
→ sin la nave grande; fondos = sus trabajos residenciales (video/tomas_v3/N1_cortina, N2_puerta, N3_zaguan) y la casa con pérgola.
Nueva frase c_1 con la voz de Carlos (Fish); el resto de voces igual que obrero_20261029. Cuadros y tomas en plan.json.
Uso: GASTO_PERFIL=charlyfavela666 python3 gasto_modal.py run clientes/Guillermo/pixar_v2_20261030/guillermo_pixar_v2_modal.py"""
import json, pathlib, sys
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/_productor")
from escenas_modal import app, escenas

AQUI = pathlib.Path(__file__).resolve().parent
G = AQUI.parent
REFS = {"carlos": "obrero_20261029/ref_carlos_pixar.png", "casa": "obrero_20261029/ref_casa_pergola.jpg", "perg": "obrero_20261029/ref_pergola_negra.jpg",
        "cortina": "video/tomas_v3/N1_cortina.png", "puerta": "video/tomas_v3/N2_puerta.png", "zaguan": "video/tomas_v3/N3_zaguan.png"}


@app.local_entrypoint()
def main(semilla: int = 21):
    plan = json.load(open(AQUI / "plan.json"))
    refs = {k: (G / v).read_bytes() for k, v in REFS.items()}
    voces = {t[5]: ((AQUI / "voz" / f"{t[5]}.wav") if t[5] == "c_1" else (G / "obrero_20261029/voz" / f"{t[5]}.wav")).read_bytes() for t in plan["tomas"]}
    out = AQUI / "salida"; out.mkdir(exist_ok=True)
    tomas = [tuple(t) for t in plan["tomas"]]
    for n, v in escenas.remote("guillermo_pixar_v2_20261030", refs, plan["cuadros"], tomas, semilla, None, voces, (704, 1280)).items():
        (out / n).write_bytes(v); print("guardado", n)
