"""Logo de Mariano Herrera (Carlos: «crea el logo de mariano»).

Contexto de marca (clientes/Mariano/estado.json, anuncios y DOCUMENTO_PARA_GPT6_ASTRA.md):
- Mariano Herrera, asesor inmobiliario en San Marino Residencial, costa Tijuana–Rosarito, vista al mar.
- Página de Facebook «Mariano asesor Inmobiliario»; Business Manager «Baja Homes by Mariano».
- Sus anuncios usan azul marino oscuro con dorado y serif elegante. No tiene logo propio (el escudo «SM»
  con olas de los anuncios es del desarrollo San Marino, no suyo: no se copia).

Propuestas (una por proceso):
  A  «Baja Homes by Mariano»            → openai/gpt-image-2/text-to-image
  B  «Mariano Herrera · Asesor Inmobiliario» → openai/gpt-image-2/text-to-image
  C  versión vectorial de A             → recraft-ai/recraft-v4.1/text-to-vector (SVG)
Uso: python3 generar_logo.py A | B | C"""
import os, sys
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "catania_mariano_montaje_20260914"))
import gancho_kling_habla_giro as g

PALETA = ("deep navy blue #0F1C2E and warm metallic gold #C9A45C only, generous white space, "
          "clean flat vector logo design, perfectly legible, centered, no mockup, no photo, no gradient "
          "background, no extra text, no watermark")
PROPUESTAS = {
    "A": ("openai/gpt-image-2/text-to-image",
          lambda: dict(prompt=("Professional real estate brand logo on a plain white background. Icon: a minimal "
                               "house roofline drawn in a single elegant gold line that flows into a gentle ocean "
                               "wave underneath, suggesting a home by the sea in Baja California. Wordmark below the "
                               "icon: the words 'BAJA HOMES' in a refined high-contrast serif typeface with wide "
                               "letter spacing in navy, and underneath in smaller gold italic serif 'by Mariano'. "
                               "Spelling must be exactly: BAJA HOMES / by Mariano. Luxury, trustworthy, coastal. "
                               + PALETA),
                       aspect_ratio="1:1", output_format="png"),
          "LOGO_A_BAJA_HOMES_BY_MARIANO.png"),
    "B": ("openai/gpt-image-2/text-to-image",
          lambda: dict(prompt=("Professional personal brand logo for a real estate agent on a plain white background. "
                               "Icon: an elegant monogram of the letters M and H interlocked, where the peak of the M "
                               "forms a subtle house roof, inside a thin gold circular outline. To the right of the "
                               "icon, a two-line wordmark: 'MARIANO HERRERA' in a refined serif typeface in navy with "
                               "wide letter spacing, and below it 'ASESOR INMOBILIARIO' in small gold sans-serif "
                               "capitals. Spelling must be exactly: MARIANO HERRERA / ASESOR INMOBILIARIO. "
                               "Horizontal layout, premium, trustworthy. " + PALETA),
                       aspect_ratio="16:9", output_format="png"),
          "LOGO_B_MARIANO_HERRERA_ASESOR.png"),
    "C": ("recraft-ai/recraft-v4.1/text-to-vector",
          lambda: dict(prompt=("Minimal vector logo for 'BAJA HOMES by Mariano', a coastal real estate agent in Baja "
                               "California. Single-line gold house roofline flowing into an ocean wave, wordmark "
                               "'BAJA HOMES' in navy elegant serif with wide spacing and 'by Mariano' in small gold "
                               "italic serif below. Flat, two colors (navy #0F1C2E, gold #C9A45C), white background, "
                               "centered, no mockup."),
                       image_size="1:1"),
          "LOGO_C_BAJA_HOMES_VECTOR.svg"),
}

if __name__ == "__main__":
    clave = sys.argv[1]
    modelo, cuerpo, salida = PROPUESTAS[clave]
    g.ESTADO = os.path.join(AQUI, "estado_%s.json" % clave)
    g.paso(clave, modelo, cuerpo, os.path.join(AQUI, salida))
