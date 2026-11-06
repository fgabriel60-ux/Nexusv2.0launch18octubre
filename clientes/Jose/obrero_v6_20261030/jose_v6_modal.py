"""José · Grupo JR · v6 (30 oct): errores que vio Carlos en la v4/v5 → se rehacen 5 escenas; V1, V2 y V5 se quedan.
- V3/V4: el líquido salía ROJO (primario café-rojizo) → gris claro.  - V6/V7: el obrero movía la boca sin voz (sin lipsync) → boca cerrada.
- V7: volcán echando lava y humo → volcán tranquilo.  - V8: letreros de cubetas mal escritos («OPLURETANO», «PRIMARO») → cubetas solo con el logo JR.
- V3: la cara cambiaba → mismo obrero de V1.
Uso: GASTO_PERFIL=charlyfavela666 python3 gasto_modal.py run clientes/Jose/obrero_v6_20261030/jose_v6_modal.py"""
import pathlib, sys
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/_productor")
from escenas_modal import app, escenas

AQUI = pathlib.Path(__file__).resolve().parent
V4 = AQUI.parent / "obrero_v4_20261030" / "salida"
GRIS = "un líquido GRIS CLARO lechoso (nada rojo, nada café, nada naranja)"
IGUAL = "Conserva EXACTAMENTE el mismo personaje animado estilo Pixar (misma cara, casco blanco GRUPO JR, chaleco azul), el mismo lugar con el volcán nevado y la misma composición. Sin texto nuevo, sin subtítulos. "
CUADROS = {
    "N3_mezcla": (["v1", "v3"], "Mismo personaje animado de la primera imagen (misma cara joven, casco blanco GRUPO JR, chaleco azul). Composición y lugar de la segunda imagen: en cuclillas mezcla con un taladro mezclador " + GRIS + " dentro de una cubeta blanca, sobre la losa gris con el volcán nevado tranquilo al fondo. Estilo Pixar, vertical, sin texto, sin subtítulos."),
    "N4_primario": (["v4"], IGUAL + "Cambia SOLO el color del líquido que aplica con el rodillo y de la parte ya pintada de la losa: ahora es " + GRIS + "."),
    "N6_terminada": (["v6"], IGUAL + "Su boca está CERRADA en una sonrisa tranquila."),
    "N7_lluvia": (["v7"], IGUAL + "El volcán está TRANQUILO: sin humo, sin ceniza, sin lava, sin fuego, con nieve en la cima y cielo con nubes de lluvia. Su boca está CERRADA en una sonrisa."),
    "N8_cierre": (["v8"], IGUAL + "Las dos cubetas blancas a sus pies son lisas y llevan SOLO el logo JR, sin ninguna otra palabra ni letra. Su boca está CERRADA en una sonrisa."),
}
CALLADO = " His mouth stays CLOSED in a gentle smile the whole time; he never talks or moves his lips. Keep the same character. No text. Audio: soft ambient, no speech."
TOMAS = [
    ("V3_mezcla", "N3_mezcla", "Vertical animated shot: the cartoon worker mixes light grey liquid in the white bucket with a red power drill mixer, the grey liquid swirls, slow push-in." + CALLADO, 5.0),
    ("V4_primario", "N4_primario", "Vertical animated shot: the cartoon worker rolls light grey primer across the grey slab with a big roller, the coated area grows, slow lateral dolly." + CALLADO, 5.0),
    ("V6_terminada", "N6_terminada", "Vertical animated shot: the cartoon worker stands proudly with hands on his hips on the finished white slab and nods slowly, slow camera orbit." + CALLADO, 4.0),
    ("V7_lluvia", "N7_lluvia", "Vertical animated shot: gentle rain falls on the white waterproofed slab, drops bead up and roll off, the cartoon worker opens his arms happily, the snowy volcano stays calm with no smoke, slow camera pull-back." + CALLADO, 4.0),
    ("V8_cierre", "N8_cierre", "Vertical animated shot: the cartoon worker smiles and waves to the camera, the two plain white buckets with the JR logo at his feet, slow push-in." + CALLADO, 5.0),
]


@app.local_entrypoint()
def main(semilla: int = 21):
    refs = {k: (V4 / f"{n}.png").read_bytes() for k, n in
            {"v1": "V1_barre", "v3": "V3_mezcla", "v4": "V4_primario", "v6": "V6_terminada", "v7": "V7_lluvia", "v8": "V8_cierre"}.items()}
    out = AQUI / "salida"; out.mkdir(exist_ok=True)
    for n, v in escenas.remote("jose_v6_20261030", refs, CUADROS, TOMAS, semilla).items():
        (out / n).write_bytes(v); print("guardado", n)
