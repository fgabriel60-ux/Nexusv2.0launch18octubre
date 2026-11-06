"""Send an explicit Blender Python file through the existing live-session bridge."""
import json, sys, urllib.request, urllib.error
from pathlib import Path
source, output = map(Path, sys.argv[1:3])
req = urllib.request.Request('https://conectorblender.onrender.com/api/blender/execute', data=json.dumps({'python':source.read_text(), 'meta':{'tipo':'libre'}}).encode(), headers={'Content-Type':'application/json'})
try:
    with urllib.request.urlopen(req, timeout=580) as response:
        result=json.load(response)
except urllib.error.HTTPError as error:
    result={'http_error':error.code,'detail':error.read().decode()}
output.write_text(json.dumps(result,ensure_ascii=False))
print('Respuesta guardada:', output)
