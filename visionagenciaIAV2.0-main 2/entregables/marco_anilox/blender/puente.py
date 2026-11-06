"""Manda código Python al Blender EN VIVO de la Mac de Carlos por el puente HTTP (ver AGENTS.md).
Uso: python3 puente.py archivo.py [archivo2.py ...]   (concatena los archivos en un solo script)"""
import json, sys, urllib.request, urllib.error

URL = "https://conectorblender.onrender.com/api/blender/execute"


def manda(codigo, timeout=580):
    d = json.dumps({"python": codigo, "meta": {"tipo": "libre"}}).encode()
    r = urllib.request.Request(URL, data=d, headers={"Content-Type": "application/json"})
    try:
        return json.loads(urllib.request.urlopen(r, timeout=timeout).read())
    except urllib.error.HTTPError as e:
        return {"_http": e.code, "_body": e.read().decode()[:800]}


if __name__ == "__main__":
    codigo = "\n\n".join(open(f).read() for f in sys.argv[1:])
    print(json.dumps(manda(codigo), ensure_ascii=False, indent=1)[:6000])
