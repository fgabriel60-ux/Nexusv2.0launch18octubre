"""Muestra para SERTEC (reparación y mantenimiento de línea blanca a domicilio, CDMX).
Datos reales tomados de SUS flyers: servicio a domicilio, diagnóstico y reparación, mantenimiento
preventivo, línea blanca y microondas, WhatsApp 55 3421-5685, Javier Candiani.
Imágenes base generadas con Codex; el texto va en capa aparte. No se promete garantía ni precios:
eso lo tiene que confirmar él.
"""
import pathlib, sys
sys.path.insert(0, "/workspaces/Nexusv2.0launch18octubre/entregables/anuncios_imagen_20261104")
from armar_anuncios import anuncio, _encaja, guardar
import armar_anuncios as A

AQUI = pathlib.Path(__file__).resolve().parent
A.SALIDA = AQUI

guardar(anuncio(_encaja(AQUI / "base_tecnico_refri.png"),
                "¿Tu refri no enfría?",
                "Vamos a tu casa el mismo día",
                boton="Pedir visita",
                etiqueta="SERTEC · CDMX",
                sombra=0.5,
                bullets=("Diagnóstico y reparación a domicilio",
                         "Refrigeradores, lavadoras y microondas",
                         "Mantenimiento preventivo"),
                sello="WhatsApp 55 3421-5685 · Javier Candiani"),
        "SERTEC_muestra_refri.jpg")

guardar(anuncio(_encaja(AQUI / "base_lavadora.png"),
                "Tu lavadora tiene arreglo",
                "Técnico a domicilio en CDMX",
                boton="Pedir visita",
                etiqueta="SERTEC · LÍNEA BLANCA",
                sombra=0.5,
                bullets=("Lavadoras, lavasecadoras y secadoras",
                         "Diagnóstico y reparación el mismo día",
                         "También línea blanca y electrónica"),
                sello="WhatsApp 55 3421-5685 · Javier Candiani"),
        "SERTEC_muestra_lavadora.jpg")
