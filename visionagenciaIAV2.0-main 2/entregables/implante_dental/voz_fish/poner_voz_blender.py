"""Mete IMPLANTE_VOZ_35s.wav en el Blender VIVO de la Mac por el puente HTTP, como pista de sonido del editor
de secuencias de CHICA_IMPLANTE_ESTILO_APROBADO, desde el cuadro 1, empaquetada dentro del .blend.

No renderiza nada (el render de Eevee se trabó antes). No cambia la escena activa, el cuadro ni el viewport.
El audio va en base64 dentro del script (no hay archivos compartidos con la Mac) y se escribe en
~/Desktop/IMPLANTE_DENTAL/IMPLANTE_VOZ_35s.wav. Si ya existe la pista VOZ_FISH_IMPLANTE la reemplaza.
NO guarda el archivo: la pista queda empaquetada en la sesión y Carlos guarda cuando quiera.
Uso: python3 poner_voz_blender.py"""
import base64, json, os, socket, urllib.error, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
WAV = os.path.join(AQUI, "IMPLANTE_VOZ_35s.wav")

CODIGO = "AUDIO_B64 = '%s'\n" % base64.b64encode(open(WAV, "rb").read()).decode() + r'''
import bpy, base64, json, os
if 'responder' not in globals():
    def responder(d): print(json.dumps(d))
sc = bpy.data.scenes['CHICA_IMPLANTE_ESTILO_APROBADO']
cuadro_antes = sc.frame_current
salida = {}
try:
    carpeta = os.path.expanduser('~/Desktop/IMPLANTE_DENTAL'); os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, 'IMPLANTE_VOZ_35s.wav')
    open(ruta, 'wb').write(base64.b64decode(AUDIO_B64))
    if not sc.sequence_editor:
        sc.sequence_editor_create()
    ed = sc.sequence_editor
    viejo = ed.sequences_all.get('VOZ_FISH_IMPLANTE')
    if viejo:
        ed.sequences.remove(viejo)
    ocupados = {s.channel for s in ed.sequences_all}
    canal = next(c for c in range(1, 33) if c not in ocupados)
    tira = ed.sequences.new_sound('VOZ_FISH_IMPLANTE', ruta, canal, 1)
    tira.sound.pack()
    tira.volume = 1.0
    sc.use_audio_scrub = True
    salida.update({"pista": tira.name, "canal": canal, "cuadros": [tira.frame_final_start, tira.frame_final_end],
                   "empaquetado": tira.sound.packed_file is not None, "fps": sc.render.fps})
    # No se guarda: la sesión abierta tiene el estilo de la hoja aplicado (render de Eevee en blanco sin
    # resolver) y guardar encima lo dejaría en el archivo de Carlos. Él decide cuándo guardar.
    salida["archivo_abierto"] = bpy.data.filepath
    salida["guardado"] = False
except Exception:
    import traceback
    salida["error"] = traceback.format_exc()
finally:
    sc.frame_set(cuadro_antes)
responder(salida)
'''

if __name__ == "__main__":
    d = json.dumps({"python": CODIGO, "meta": {"tipo": "libre"}}).encode()
    r = urllib.request.Request("https://conectorblender.onrender.com/api/blender/execute", data=d,
                               headers={"Content-Type": "application/json"})
    try:
        print(urllib.request.urlopen(r, timeout=240).read().decode()[:1500].split('"python"')[0])
    except urllib.error.HTTPError as e:
        print("HTTP", e.code, e.read().decode()[:500])
    except (socket.timeout, TimeoutError) as e:
        print("SIN RESPUESTA:", e)
