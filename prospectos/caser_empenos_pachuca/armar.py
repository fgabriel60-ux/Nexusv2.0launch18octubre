"""Muestra para CASER Empeños (Pachuca). Datos reales tomados de SUS propios flyers.
Imagen base generada con Codex (regla de Carlos: todas las imágenes se generan con Codex).
El texto va en capa aparte. No se inventan tasas, montos ni plazos: eso lo tiene que confirmar el cliente.
"""
import pathlib, sys
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/entregables/anuncios_imagen_20261104")
from armar_anuncios import anuncio, _encaja, guardar
import armar_anuncios as A

AQUI = pathlib.Path(__file__).resolve().parent
A.SALIDA = AQUI

im = anuncio(_encaja(AQUI / "base_codex.png"),
             "Empeña tu auto o moto",
             "Te resolvemos en 15 minutos",
             boton="Cotizar por WhatsApp",
             etiqueta="CASER EMPEÑOS · PACHUCA",
             sombra=0.5,
             bullets=("Aceptamos cualquier modelo",
                      "También herramienta, línea blanca y electrónica",
                      "Linda Vista, frente a Matilde"),
             sello="WhatsApp 771 151 2703 · Tel. 771 119 7188",
             pie="Con certeza jurídica · consulta condiciones en sucursal")
guardar(im, "CASER_muestra_v1.jpg")
