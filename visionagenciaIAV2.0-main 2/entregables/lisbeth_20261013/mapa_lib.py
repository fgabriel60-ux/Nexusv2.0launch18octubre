"""Mapa satelital (mosaicos Esri World Imagery) con cámara continua: render(lat, lon, z, W, H) + proyección para dibujar encima."""
import math, os, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from PIL import Image

CACHE = Path(__file__).resolve().parent / 'tmp_mapa' / 'tiles'; CACHE.mkdir(parents=True, exist_ok=True)
URL = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
POLIGONO = [(-105.2785587767478, 19.96032403756652), (-105.2771308890864, 19.96080598244208), (-105.2779633001179, 19.96224991157576),
            (-105.2789979673481, 19.96190289779376)]   # (lon, lat) del KMZ de Lisbeth
AEROPUERTO = (19.71861, -105.23222)                    # Aeropuerto de Chalacatepec (Costalegre), Tomatlán, Jal.


def px(lat, lon, z):
    n = 256 * 2 ** z
    return (lon + 180) / 360 * n, (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n


def tile(z, x, y):
    n = 2 ** z; x %= n
    f = CACHE / f'{z}_{x}_{y}.jpg'
    if not f.exists():
        r = urllib.request.Request(URL.format(z=z, x=x, y=y), headers={'User-Agent': 'Mozilla/5.0 (visionagencia mapa)'})
        for i in range(3):
            try: f.write_bytes(urllib.request.urlopen(r, timeout=30).read()); break
            except Exception: pass
    try: return Image.open(f).convert('RGB')
    except Exception: return Image.new('RGB', (256, 256), (20, 30, 40))


def render(lat, lon, z, W, H):
    zi = min(18, int(math.floor(z + 0.35))); k = 2 ** (z - zi)
    cx, cy = px(lat, lon, zi); vw, vh = W / k, H / k; x0, y0 = cx - vw / 2, cy - vh / 2
    tx0, ty0, tx1, ty1 = int(x0 // 256), int(y0 // 256), int((x0 + vw) // 256), int((y0 + vh) // 256)
    coords = [(x, y) for y in range(ty0, ty1 + 1) for x in range(tx0, tx1 + 1)]
    with ThreadPoolExecutor(8) as ex: ims = list(ex.map(lambda c: tile(zi, *c), coords))
    lienzo = Image.new('RGB', ((tx1 - tx0 + 1) * 256, (ty1 - ty0 + 1) * 256))
    for (x, y), im in zip(coords, ims): lienzo.paste(im, ((x - tx0) * 256, (y - ty0) * 256))
    box = (x0 - tx0 * 256, y0 - ty0 * 256, x0 - tx0 * 256 + vw, y0 - ty0 * 256 + vh)
    img = lienzo.crop(tuple(int(round(v)) for v in box)).resize((W, H), Image.BICUBIC)

    def proj(la, lo):
        a, b = px(la, lo, zi); return (a - x0) * k, (b - y0) * k
    return img, proj


def haversine(a, b):
    R = 6371.0088; p1, p2 = math.radians(a[0]), math.radians(b[0]); dp = p2 - p1; dl = math.radians(b[1] - a[1])
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))


def centro_y_area():
    la0 = sum(p[1] for p in POLIGONO) / 4; lo0 = sum(p[0] for p in POLIGONO) / 4
    m = [((lo - lo0) * 111320 * math.cos(math.radians(la0)), (la - la0) * 110574) for lo, la in POLIGONO]
    a = abs(sum(m[i][0] * m[(i + 1) % 4][1] - m[(i + 1) % 4][0] * m[i][1] for i in range(4))) / 2
    return (la0, lo0), a
