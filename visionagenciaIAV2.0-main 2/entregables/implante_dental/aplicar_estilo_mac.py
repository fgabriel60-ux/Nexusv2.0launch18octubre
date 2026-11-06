"""Aplica estilo_hoja.py en el Blender 3.3 VIVO de la Mac por el puente HTTP, guarda una COPIA nueva y
regresa dos renders Eevee de verificación (cuadros 150 y 620, 30 %).

Reglas de AGENTS.md: se guarda el estado (escena activa, cuadro, % de resolución, filepath del render) y
se restaura en finally. No se cambia el shading del viewport (queda SOLID). El archivo abierto no se
sobrescribe: save_as_mainfile(copy=True) a CHICA_IMPLANTE_ESTILO_HOJA.blend.
Para renderizar se activa temporalmente la escena objetivo en la ventana (si no, Eevee dibuja otro cuadro).
Uso: python3 aplicar_estilo_mac.py"""
import base64, json, os, urllib.error, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
ESTILO = open(os.path.join(AQUI, 'estilo_hoja.py'), encoding='utf8').read()
# Modelo 3D del panel PASO 5 (GLB ligero, ~2.6 MB): va en base64 dentro del script porque no hay archivos
# compartidos con la Mac. Se omite si no existe el GLB o si se corre con SIN_MODELO=1.
GLB = os.path.join(AQUI, 'modelo_3d_hoja', 'HOJA_PASO5_hunyuan_LIGERO.glb')
MODELO = ''
if os.path.exists(GLB) and not os.environ.get('SIN_MODELO'):
    MODELO = ("\nGLB_B64 = '%s'\n" % base64.b64encode(open(GLB, 'rb').read()).decode()
              + open(os.path.join(AQUI, 'integrar_modelo_hoja.py'), encoding='utf8').read()
              .replace("responder(resultado)", "_resultado_modelo = resultado"))
CUADROS = (150, 620, 780, 900) if MODELO else (150, 620)

CODIGO = ("CUADROS_MAC = %r\n" % (CUADROS,)) + ESTILO.replace("responder(resultado)", "_resultado_estilo = resultado") + MODELO + r'''

import os, tempfile, base64
win = bpy.context.window
escena_antes = win.scene
sc = bpy.data.scenes[ESCENA]
cuadro_antes = sc.frame_current
pct_antes = sc.render.resolution_percentage
ruta_antes = sc.render.filepath
salida = {"estilo": _resultado_estilo, "modelo": globals().get("_resultado_modelo"), "renders": {}}
try:
    destino = os.path.expanduser('~/Desktop/IMPLANTE_DENTAL/CHICA_IMPLANTE_ESTILO_HOJA.blend')
    bpy.ops.wm.save_as_mainfile(filepath=destino, copy=True, compress=True)
    salida["copia"] = destino
    win.scene = sc
    sc.render.resolution_percentage = 30
    for f in CUADROS_MAC:
        sc.frame_set(f)
        ruta = os.path.join(tempfile.gettempdir(), 'estilo_hoja_%d.png' % f)
        sc.render.filepath = ruta
        bpy.ops.render.render(write_still=True)
        salida["renders"][str(f)] = base64.b64encode(open(ruta, 'rb').read()).decode()
except Exception as e:
    import traceback
    salida["error"] = traceback.format_exc()
finally:
    sc.render.resolution_percentage = pct_antes
    sc.render.filepath = ruta_antes
    sc.frame_set(cuadro_antes)
    win.scene = escena_antes
responder(salida)
'''

if __name__ == '__main__':
    d = json.dumps({"python": CODIGO, "meta": {"tipo": "libre"}}).encode()
    r = urllib.request.Request("https://conectorblender.onrender.com/api/blender/execute", data=d,
                               headers={"Content-Type": "application/json"})
    try:
        res = json.loads(urllib.request.urlopen(r, timeout=590).read())
    except urllib.error.HTTPError as e:
        print("HTTP", e.code, e.read().decode()[:500]); raise SystemExit(1)

    def buscar(o):
        if isinstance(o, dict):
            if "renders" in o: return o
            for v in o.values():
                x = buscar(v)
                if x: return x
        if isinstance(o, str) and '"renders"' in o:
            try: return json.loads(o)
            except Exception: pass
        return None

    datos = buscar(res)
    if not datos:
        print(json.dumps(res)[:2000]); raise SystemExit(1)
    os.makedirs(os.path.join(AQUI, 'mac_estilo'), exist_ok=True)
    for k, v in datos["renders"].items():
        open(os.path.join(AQUI, 'mac_estilo', 'MAC_EEVEE_%s.png' % k), 'wb').write(base64.b64decode(v))
    datos.pop("renders")
    json.dump(datos, open(os.path.join(AQUI, 'mac_estilo', 'resultado.json'), 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(datos, ensure_ascii=False, indent=1))
