import base64
try:
    with open('/Users/juancarlos/Desktop/IMPLANTE_DENTAL/ANTES_STICKER_20260915_101838.blend','rb') as f:
        responder({'blend':base64.b64encode(f.read()).decode()})
except Exception:
    raise
finally:
    pass
