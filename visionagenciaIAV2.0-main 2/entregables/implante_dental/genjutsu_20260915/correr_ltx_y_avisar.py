"""Corre la prueba de LTX ControlNet a 480p y le manda el resultado a Carlos por WhatsApp, porque ya se fue.

Mide el saldo de WaveSpeed ANTES y DESPUÉS para reportar el costo REAL, no el de lista: se comprobó que el
`base_price` engaña (MiniMax decía $0.25 y cobró ~$2.85).
Uso: python3 correr_ltx_y_avisar.py
"""
import base64, json, subprocess, time, urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ENV = Path('/workspaces/visionagenciaIAV2.0/visionagenciaIAv2.0-cripto-sim-y-corte-catania/VisionagenciaIAv2.0-main/.env')
CARLOS = '5216312470486@c.us'
SALIDA = AQUI / 'PRUEBA_LTX_DEPTH_TRAMO_A.mp4'
TIRA = AQUI / 'REVISION_LTX.jpg'

env = {}
for l in ENV.read_text().splitlines():
    if '=' in l and not l.lstrip().startswith('#'):
        k, v = l.split('=', 1); env[k.strip()] = v.strip().strip('"').strip("'")


def saldo():
    r = urllib.request.Request('https://api.wavespeed.ai/api/v3/balance',
                               headers={'Authorization': 'Bearer ' + env['WAVESPEED_API_KEY']})
    return float(json.load(urllib.request.urlopen(r, timeout=60))['data']['balance'])


def wa_texto(m):
    r = urllib.request.Request('https://waapi.app/api/v1/instances/' + env['WAAPI_INSTANCE'] + '/client/action/send-message',
                               data=json.dumps({'chatId': CARLOS, 'message': m}).encode(),
                               headers={'Authorization': 'Bearer ' + env['WAAPI_TOKEN'], 'Content-Type': 'application/json'})
    return (json.load(urllib.request.urlopen(r, timeout=120)).get('data') or {}).get('status')


def wa_media(f, cap):
    b = {'chatId': CARLOS, 'mediaBase64': base64.b64encode(Path(f).read_bytes()).decode(),
         'mediaName': Path(f).name, 'asDocument': False, 'mediaCaption': cap}
    r = urllib.request.Request('https://waapi.app/api/v1/instances/' + env['WAAPI_INSTANCE'] + '/client/action/send-media',
                               data=json.dumps(b).encode(),
                               headers={'Authorization': 'Bearer ' + env['WAAPI_TOKEN'], 'Content-Type': 'application/json'})
    return (json.load(urllib.request.urlopen(r, timeout=300)).get('data') or {}).get('status')


def ffprobe(f):
    out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v',
                          '-show_entries', 'stream=r_frame_rate,nb_frames,width,height',
                          '-show_entries', 'format=duration', '-of', 'default=nw=1', str(f)],
                         capture_output=True, text=True).stdout
    return dict(l.split('=', 1) for l in out.strip().splitlines() if '=' in l)


if __name__ == '__main__':
    antes = saldo()
    t0 = time.monotonic()
    p = subprocess.run(['python3', '-u', str(AQUI / 'prueba_ltx_control.py'), 'depth'],
                       capture_output=True, text=True, cwd=str(AQUI))
    tardo = round(time.monotonic() - t0)
    log = (p.stdout + p.stderr)[-1200:]
    (AQUI / 'prueba_ltx.log').write_text(p.stdout + p.stderr)
    despues = saldo()
    costo = antes - despues

    if p.returncode != 0 or not SALIDA.exists():
        wa_texto('🤖 Claude · La prueba de LTX FALLÓ.\n\nSaldo: $%.2f (no se cobró casi nada)\n\nError:\n%s' % (despues, log[-600:]))
        print('falló'); raise SystemExit(1)

    info = ffprobe(SALIDA)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(SALIDA), '-vf',
                    "select='eq(n\\,0)+eq(n\\,90)+eq(n\\,180)+eq(n\\,270)+eq(n\\,400)',scale=220:392,tile=5x1",
                    '-frames:v', '1', '-vsync', 'vfr', str(TIRA)], check=False)

    dur = float(info.get('duration', 0))
    texto = ('🤖 Claude · LTX ControlNet (guía por profundidad), 480p\n\n'
             '💰 COSTO REAL: $%.2f  (lista decía $0.20)\n'
             '⏱️ Tardó %d min %d seg\n'
             '📐 Salida: %sx%s, %.1f segundos, %s fps\n'
             '   Entrada: 432x768, 18.0 segundos, 30 fps\n\n'
             '%s\n\n'
             'Saldo que te queda: $%.2f\n\n'
             'Comparación:\n'
             '• lucy $0.01 · 100 seg · rompió el tiempo, sin corte anatómico\n'
             '• MiniMax ~$2.85 · 21 min · calidad sí, velocidad no\n'
             '• LTX $%.2f · %d min · ver video\n\n'
             'Te mando el video y la tira de 5 cuadros para que juzgues.') % (
        costo, tardo // 60, tardo % 60, info.get('width'), info.get('height'), dur,
        (info.get('r_frame_rate') or '').split('/')[0],
        ('✅ Respetó la duración' if abs(dur - 18) < 1.5 else '⚠️ CAMBIÓ la duración: entraron 18 s y salieron %.1f s' % dur),
        despues, costo, tardo // 60)

    rec = {'texto': wa_texto(texto)}
    time.sleep(5)
    rec['video'] = wa_media(SALIDA, 'LTX depth 480p · tramo A completo de 18 s')
    if TIRA.exists():
        time.sleep(6)
        rec['tira'] = wa_media(TIRA, 'Los 5 momentos: rostro, aguja, corte y sticker')
    (AQUI / 'recibo_ltx.json').write_text(json.dumps(
        {'costo_real': round(costo, 4), 'saldo_antes': antes, 'saldo_despues': despues,
         'segundos': tardo, 'video': info, 'whatsapp': rec}, ensure_ascii=False, indent=1))
    print(json.dumps({'costo_real': round(costo, 4), 'segundos': tardo, 'whatsapp': rec}, ensure_ascii=False))
