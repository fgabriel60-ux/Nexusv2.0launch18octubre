"""Baja los reels de referencia de la app para probarse ropa (1 nov) + comentarios, y arma hojas de cuadros para Glimmer."""
import io, json, os, subprocess, urllib.request
import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
from PIL import Image, ImageDraw, ImageFont
T = os.environ['APIFY_TOKEN']
CODIGOS = ['DJ4nXYLhl8D', 'DZd00LrsCGQ', 'DOcn-0MjTeK']
def apify(body):
    r = urllib.request.Request(f'https://api.apify.com/v2/acts/apify~instagram-scraper/run-sync-get-dataset-items?token={T}&timeout=280',
                               data=json.dumps(body).encode(), headers={'Content-Type': 'application/json'})
    return json.loads(urllib.request.urlopen(r, timeout=320).read())
urls = [f'https://www.instagram.com/reel/{c}/' for c in CODIGOS]
info = {}
for it in apify({'directUrls': urls, 'resultsType': 'posts', 'resultsLimit': 1}):
    sc, v = it.get('shortCode'), it.get('videoUrl')
    info[sc] = {'cuenta': it.get('ownerUsername'), 'texto': it.get('caption') or '', 'likes': it.get('likesCount'),
                'comentarios_n': it.get('commentsCount'), 'vistas': it.get('videoPlayCount') or it.get('videoViewCount')}
    if not v: continue
    p = f'{sc}.mp4'; open(p, 'wb').write(urllib.request.urlopen(v, timeout=120).read())
    d = imageio_ffmpeg.count_frames_and_secs(p)[1]
    ims = []
    for i in range(10):
        t = d * (i + .5) / 10
        b = subprocess.run([FF, '-v', 'error', '-ss', str(t), '-i', p, '-frames:v', '1', '-vf', 'scale=216:384:force_original_aspect_ratio=decrease,pad=216:384:(ow-iw)/2:(oh-ih)/2', '-f', 'image2pipe', '-vcodec', 'png', '-'], capture_output=True).stdout
        im = Image.open(io.BytesIO(b)); ImageDraw.Draw(im).text((6, 4), f'{t:.0f}s', fill='yellow', font=ImageFont.load_default(22)); ims.append(im)
    H = Image.new('RGB', (1080, 768)); [H.paste(im, ((i % 5) * 216, (i // 5) * 384)) for i, im in enumerate(ims)]; H.save(f'{sc}_hoja.jpg', quality=85)
    info[sc]['duracion'] = round(d); print(sc, it.get('ownerUsername'), round(d), flush=True)
com = apify({'directUrls': urls[:2], 'resultsType': 'comments', 'resultsLimit': 80})
for c in com:
    sc = (c.get('postUrl') or '').rstrip('/').split('/')[-1]
    info.setdefault(sc, {}).setdefault('comentarios', []).append(c.get('text'))
json.dump(info, open('refs.json', 'w'), ensure_ascii=False, indent=1)
print({k: (len(v.get('comentarios', [])), v.get('cuenta')) for k, v in info.items()})
