"""José v7 (30 oct): dos errores que la v6 no quitó → V7 con volcán echando humo/lava y V8 con cubetas mal escritas («OPLURETANO», «PRIMARO»).
V7 y V8 parten de N6_terminada (volcán tranquilo, ya revisado); V8 sin cubetas para que no haya letras inventadas. El resto de la v6 se queda."""
import pathlib, sys
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/clientes/_productor")
from escenas_modal import app, escenas

AQUI = pathlib.Path(__file__).resolve().parent
IGUAL = "Conserva EXACTAMENTE el mismo personaje animado estilo Pixar (misma cara, casco blanco GRUPO JR, chaleco azul), la misma losa blanca impermeabilizada y el mismo volcán nevado TRANQUILO, sin humo, sin ceniza, sin lava. Sin texto, sin cubetas, sin letreros. Su boca está CERRADA en una sonrisa. "
CUADROS = {"M7_lluvia": (["n6"], IGUAL + "Ahora cae una lluvia suave y el cielo está nublado; él abre los brazos contento."),
           "M8_cierre": (["n6"], IGUAL + "Ahora saluda a cámara con una mano levantada, contento.")}
CALLADO = " His mouth stays CLOSED in a gentle smile; he never talks. The snowy volcano stays calm: no smoke, no ash, no lava. No buckets, no text. Audio: soft ambient, no speech."
TOMAS = [("V7_lluvia", "M7_lluvia", "Vertical animated shot: gentle rain falls on the white waterproofed slab, drops bead up and roll off, the cartoon worker keeps his arms open happily, slow camera pull-back." + CALLADO, 4.0),
         ("V8_cierre", "M8_cierre", "Vertical animated shot: the cartoon worker smiles and waves to the camera, slow push-in." + CALLADO, 5.0)]


@app.local_entrypoint()
def main(semilla: int = 27):
    refs = {"n6": (AQUI / "salida/N6_terminada.png").read_bytes()}
    for n, v in escenas.remote("jose_v7_20261030", refs, CUADROS, TOMAS, semilla).items():
        (AQUI / "salida" / n).write_bytes(v); print("guardado", n)
