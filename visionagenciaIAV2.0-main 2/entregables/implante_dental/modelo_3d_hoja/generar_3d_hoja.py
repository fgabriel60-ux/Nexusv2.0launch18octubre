"""Modelo 3D a partir de la hoja de Alberto (Carlos: «crea modelo 3d a partir de esa hoja si necesitas»).
Entrada: panel PASO 5 (f6_corona.png): corte de maxilar con dientes juntos, implante con pilar, encía con
borde luminoso y hueso marfil, sobre fondo oscuro. Se piden dos modelos para comparar:
  hunyuan  → wavespeed-ai/hunyuan3d-v3/image-to-3d (PBR)
  trellis  → wavespeed-ai/trellis-2/image-to-3d
Salida: GLB en esta carpeta. Uso: python3 generar_3d_hoja.py hunyuan | trellis"""
import base64, json, os, sys
from io import BytesIO
from PIL import Image
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "..", "catania_mariano_montaje_20260914"))
import gancho_kling_habla_giro as g

PANEL = ("/workspaces/visionagenciaIAV2.0/visionagenciaIAv2.0-cripto-sim-y-corte-catania/VisionagenciaIAv2.0-main/"
         "clientes/Vision Agencia/veneers_dental/hoja_proceso_implante/f6_corona.png")


def uri_jpg(ruta, lado=1600):
    im = Image.open(ruta).convert("RGB"); im.thumbnail((lado, lado))
    b = BytesIO(); im.save(b, "JPEG", quality=95)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()


MODELOS = {
    "hunyuan": ("wavespeed-ai/hunyuan3d-v3/image-to-3d",
                lambda: dict(image=uri_jpg(PANEL), enable_pbr=True, face_count=500000), "HOJA_PASO5_hunyuan.glb"),
    "trellis": ("wavespeed-ai/trellis-2/image-to-3d",
                lambda: dict(image=uri_jpg(PANEL), remove_background=True, resolution="1024"), "HOJA_PASO5_trellis.glb"),
}

if __name__ == "__main__":
    clave = sys.argv[1]
    modelo, cuerpo, salida = MODELOS[clave]
    g.ESTADO = os.path.join(AQUI, "estado_%s.json" % clave)
    g.paso(clave, modelo, cuerpo, os.path.join(AQUI, salida))
