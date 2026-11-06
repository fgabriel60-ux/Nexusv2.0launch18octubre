"""Busca en YouTube (Apify streamers~youtube-scraper) videos de Alex Hormozi y Monje Malo con subtítulos, para sacar ideas para Visión Agencia."""
import json, os, urllib.request
T = os.environ['APIFY_TOKEN']
def corre(entrada, nombre):
    r = urllib.request.Request(f'https://api.apify.com/v2/acts/streamers~youtube-scraper/run-sync-get-dataset-items?token={T}&timeout=600',
                               data=json.dumps(entrada).encode(), headers={'Content-Type': 'application/json'})
    it = json.loads(urllib.request.urlopen(r, timeout=660).read())
    json.dump(it, open(f'{nombre}.json', 'w'), ensure_ascii=False)
    for x in it: print(nombre, x.get('channelName'), '|', x.get('title'), '|', x.get('viewCount'), '| subs:', bool(x.get('subtitles')), flush=True)
corre({'searchQueries': ['Monje Malo negocios', 'Monje Malo ventas'], 'maxResults': 6, 'downloadSubtitles': True, 'subtitlesLanguage': 'es', 'subtitlesFormat': 'plaintext'}, 'monje')
corre({'searchQueries': ['Alex Hormozi how to get clients agency', 'Alex Hormozi grand slam offer', 'Alex Hormozi pricing raise prices', 'Alex Hormozi client retention churn'], 'maxResults': 3, 'downloadSubtitles': True, 'subtitlesLanguage': 'en', 'subtitlesFormat': 'plaintext'}, 'hormozi')
