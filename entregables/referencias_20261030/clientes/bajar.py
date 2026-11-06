"""Baja las referencias de Instagram que Carlos mandó a cada cliente (30 oct) y arma una hoja por reel, para el plan de Glimmer y para generar escenas como la referencia."""
import io, json, os, subprocess, urllib.request
from PIL import Image, ImageDraw, ImageFont
T = os.environ['APIFY_TOKEN']
REFS = {'Israel': ['DZW99XNtlqQ', 'Dbjy5rnujqg', 'DduYDrtJQJa'], 'BDPro': ['DZqntVJgrty'], 'Fernando': ['DasdFyGlBeq', 'DbGXLe7idHv'],
        'Lisbeth': ['DbvIz5iRf_M', 'DV_Gdpyjkd0'], 'Ivan': ['DeAKRRKh7Xt', 'DcFhjRnKQuQ'], 'Blanca': ['DV9o6DwjUZE', 'DWUG_L0EUCz'],
        'Ruben': ['DFYDrtPx6DZ'], 'Generadores': ['DeuJuRTo7ZF', 'DVRJl-lkbzt']}
todos = [c for v in REFS.values() for c in v]
r = urllib.request.Request(f'https://api.apify.com/v2/acts/apify~instagram-scraper/run-sync-get-dataset-items?token={T}&timeout=280',
                           data=json.dumps({'directUrls': [f'https://www.instagram.com/reel/{c}/' for c in todos], 'resultsType': 'posts', 'resultsLimit': 1}).encode(), headers={'Content-Type': 'application/json'})
info = {}
for it in json.loads(urllib.request.urlopen(r, timeout=320).read()):
    sc, v = it.get('shortCode'), it.get('videoUrl')
    info[sc] = {'cuenta': it.get('ownerUsername'), 'texto': (it.get('caption') or '')[:300]}
    if not v: continue
    p = f'{sc}.mp4'; open(p, 'wb').write(urllib.request.urlopen(v, timeout=120).read())
    d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p], capture_output=True, text=True).stdout)
    ims = []
    for i in range(10):
        t = d * (i + .5) / 10
        b = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(t), '-i', p, '-frames:v', '1', '-vf', 'scale=216:384:force_original_aspect_ratio=decrease,pad=216:384:(ow-iw)/2:(oh-ih)/2', '-f', 'image2pipe', '-vcodec', 'png', '-'], capture_output=True).stdout
        im = Image.open(io.BytesIO(b)); ImageDraw.Draw(im).text((6, 4), f'{t:.0f}s', fill='yellow', font=ImageFont.load_default(22)); ims.append(im)
    H = Image.new('RGB', (1080, 768)); [H.paste(im, ((i % 5) * 216, (i // 5) * 384)) for i, im in enumerate(ims)]; H.save(f'{sc}_hoja.jpg', quality=85)
    info[sc]['duracion'] = round(d); print(sc, it.get('ownerUsername'), round(d), flush=True)
json.dump({'refs': REFS, 'info': info}, open('refs.json', 'w'), ensure_ascii=False, indent=1)
