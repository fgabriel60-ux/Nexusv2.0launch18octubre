"""Transición en Kling (Carlos: «la transición de la cara de la mujer del video final con las otras personas,
el close up al agujero, cómo se divide la pantalla, y luego la encía y dientes solos»).

Tres clips start→end de 5 s con kwaivgi/kling-v2.6-pro/image-to-video (image + end_image):
  1  último cuadro de video_grupo_edit_diente.mp4 → close-up del hueco (GPT2_CUADRO_150_CLOSEUP)
  2  close-up del hueco → pantalla dividida con línea cian (GPT2_TRANSICION_CUADRO_749_v3)
  3  pantalla dividida → solo dientes y encía (GPT2_SOLO_DIENTES_ENCIAS_v4)
Kling necesita inicio y fin del mismo tamaño: cada cuadro se recorta al centro a 9:16 y se lleva a 720×1280.
Uso: python3 kling_transicion.py 1 | 2 | 3"""
import base64, os, sys
from io import BytesIO
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
DENTAL = os.path.dirname(AQUI)
sys.path.insert(0, os.path.join(DENTAL, "..", "catania_mariano_montaje_20260914"))
import gancho_kling_habla_giro as g

ULTIMO = os.path.join(AQUI, "ultimo_cuadro_video_final.png")
CLOSEUP = os.path.join(DENTAL, "gpt_estilo_hoja", "GPT2_CUADRO_150_CLOSEUP.png")
DIVIDIDA = os.path.join(DENTAL, "gpt_transicion", "GPT2_TRANSICION_CUADRO_749_v3.png")
SOLO = os.path.join(DENTAL, "gpt_transicion", "GPT2_SOLO_DIENTES_ENCIAS_v4.png")
W, H = 720, 1280

NEG = ("extra teeth, duplicated teeth, deformed mouth, changing face identity, morphing skin, flicker, jump cut, "
       "crossfade dissolve, text, labels, watermark, gore, blood, camera shake, low quality")
CLIPS = {
    "1": (ULTIMO, CLOSEUP, "CLIP1_CARA_A_CLOSEUP.mp4",
          "One continuous smooth cinematic push-in. The smiling young woman at the party holds her smile while the "
          "camera glides slowly and steadily toward her mouth, the warm party background falling into darkness, "
          "until an extreme macro close-up of her lips and the gap of the missing upper front tooth fills the frame, "
          "ending exactly at the final image. Her face stays the same person, teeth and gap unchanged, only the "
          "camera moves. Lighting shifts gently from warm party light to dark studio light with a soft teal rim."),
    "2": (CLOSEUP, DIVIDIDA, "CLIP2_CLOSEUP_A_PANTALLA_DIVIDIDA.mp4",
          "Macro close-up of the woman's smile with the missing upper front tooth. A thin luminous cyan line appears "
          "and sweeps diagonally across the frame like a precise scanner; everything on the right of the line "
          "smoothly reveals a clean anatomical cross-section of the upper jaw: ivory porous bone, pink gum, the "
          "roots of the neighbouring teeth and a titanium implant inside the bone above the gap. The left side stays "
          "her real skin and lips. The camera eases slightly to the final framing and ends exactly at the final "
          "image. Smooth, elegant medical visualisation, dark teal background with warm rim light."),
    "3": (DIVIDIDA, SOLO, "CLIP3_PANTALLA_DIVIDIDA_A_SOLO_DIENTES.mp4",
          "Split screen with the woman's lips on the left and the anatomical jaw section on the right, divided by a "
          "thin luminous cyan line. The cyan line slides smoothly to the left edge and fades out, the photographic "
          "face side dissolves into darkness, while the anatomical section of teeth, gum, bone and implant glides "
          "to the centre and settles, ending exactly at the final image with only the teeth and gums section on a "
          "dark teal background. Only four upper teeth with their roots and the implant in the gap. Smooth, "
          "continuous, elegant."),
}


def cuadro_916(ruta):
    im = Image.open(ruta).convert("RGB")
    w, h = im.size
    if w / h > W / H:
        nw = int(h * W / H); im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:
        nh = int(w * H / W); im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    im = im.resize((W, H), Image.Resampling.LANCZOS)
    b = BytesIO(); im.save(b, "PNG")
    return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()


if __name__ == "__main__":
    clave = sys.argv[1]
    inicio, fin, salida, prompt = CLIPS[clave]
    g.ESTADO = os.path.join(AQUI, "estado_clip%s.json" % clave)
    g.paso("clip%s" % clave, "kwaivgi/kling-v2.6-pro/image-to-video",
           lambda: dict(image=cuadro_916(inicio), end_image=cuadro_916(fin), prompt=prompt, negative_prompt=NEG,
                        duration=5, sound=False),
           os.path.join(AQUI, salida))
