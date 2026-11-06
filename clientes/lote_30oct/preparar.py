"""Prepara voces (Fish) y referencias del lote 30 oct: Giovanni (G1, G2a, G2b), Mariano (MT_habla). Uso: python3 preparar.py"""
import json, re, subprocess, urllib.request
from pathlib import Path
import imageio_ffmpeg
from PIL import Image

AQUI = Path(__file__).resolve().parent; RAIZ = AQUI.parents[1]
FF = imageio_ffmpeg.get_ffmpeg_exe()
env = {}
for l in open(RAIZ / '.env'):
    if '=' in l and not l.lstrip().startswith('#'): k, v = l.split('=', 1); env[k.strip()] = v.strip().strip('"\'')
LLAVE = env['FISH_API_KEY']
VOZ_G = '603b9da080ec4a75ba5d3a42465fa754'
VOZ_M = re.search(r"VOZ_MARIANO\s*=\s*['\"]([0-9a-f]+)", (RAIZ / 'clientes/Mariano/video/spiderman_voces.py').read_text()).group(1)
LINEAS = {
    'G1': (VOZ_G, 'Más de noventa divorcios resueltos en Los Cabos. Trámite cien por ciento en línea. Soy el licenciado Giovanni Pulido, abogado con más de quince años de experiencia.'),
    'G2a': (VOZ_G, 'Buscamos el acuerdo en el divorcio, con total confidencialidad. Divorcio voluntario desde veinte mil pesos, precio único sin sorpresas.'),
    'G2b': (VOZ_G, 'Escríbeme por WhatsApp al seis dos cuatro, uno tres seis, treinta y tres, veintiocho. Los tiempos varían según el juzgado.'),
    'MT': (VOZ_M, 'Si creías que un Tesla solo impresiona en la calle... te presento casas que impresionan más.'),
}
for k, (vid, t) in LINEAS.items():
    r = urllib.request.Request('https://api.fish.audio/v1/tts', method='POST', data=json.dumps({'text': t, 'format': 'wav', 'reference_id': vid, 'prosody': {'speed': 1.0}}).encode(),
                               headers={'Authorization': 'Bearer ' + LLAVE, 'Content-Type': 'application/json', 'model': 's2-pro'})
    (AQUI / 'voz' / f'{k}.wav').write_bytes(urllib.request.urlopen(r, timeout=300).read())
    err = subprocess.run([FF, '-i', str(AQUI / 'voz' / f'{k}.wav')], capture_output=True, text=True).stderr
    h, m, s = err.split('Duration: ')[1].split(',')[0].split(':'); print(k, round(int(h) * 3600 + int(m) * 60 + float(s), 1), 's')
# Giovanni: recorte de su rostro/traje del anuncio B (foto real que él mandó)
b = Image.open(RAIZ / 'clientes/Giovanni/whatsapp/hechos_por_mi/20261028_142957_image.jpg').convert('RGB')
b.crop((900, 170, 1600, 1100)).save(AQUI / 'refs' / 'giovanni_cara.png')
