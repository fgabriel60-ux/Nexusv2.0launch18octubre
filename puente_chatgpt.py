"""Puente WhatsApp → ChatGPT (Carlos, 31 oct 2026): cuando Carlos escribe en su propio chat un mensaje que empieza con «chatgpt»,
se lo pasa a ChatGPT (Codex CLI con su cuenta, ./gpt.sh) y responde ahí mismo. No usa Claude.
Correr: nohup setsid python3 puente_chatgpt.py > /vol/claude-config/codex/puente.log 2>&1 &
«chatgpt nuevo» borra la conversación."""
import json, os, re, subprocess, sys, time
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/herramientas')
from wa import accion

CHAT = '44522318905388@lid'
D = '/vol/claude-config/codex'
VISTOS, HIST = f'{D}/puente_vistos.json', f'{D}/conversacion.txt'
GPT = '/workspaces/Nexusv2.0launch18octubre/gpt.sh'
RAIZ = '/workspaces/Nexusv2.0launch18octubre'
PREFIJO = re.compile(r'^\s*chat\s*gpt[\s,:.-]*', re.I)
INICIO = time.time()


def cargar():
    try: return set(json.load(open(VISTOS)))
    except Exception: return set()


def mensajes():
    r = accion('fetch-messages', {'chatId': CHAT, 'limit': 15}) or {}
    d = r.get('data', {}); ms = d.get('data', d) if isinstance(d, dict) else d
    for x in ms or []:
        m = x.get('message', x); yield m.get('_data', m)


def responder(texto):
    if texto.strip().lower() in ('nuevo', 'nueva', 'reset'):
        open(HIST, 'w').close(); return 'Listo, empecé una conversación nueva.'
    hist = open(HIST).read()[-6000:] if os.path.exists(HIST) else ''
    ctx = open(f'{D}/contexto_carlos.md').read() if os.path.exists(f'{D}/contexto_carlos.md') else ''
    prompt = (f'{ctx}\n\n---\n\n'
              + (f'Conversación previa:\n{hist}\n\n' if hist else '') + f'Carlos: {texto}')
    env = dict(os.environ, CODEX_HOME=D)   # modo agente: acceso total al workspace (AGENTS.md trae herramientas y reglas)
    try:
        r = subprocess.run(['codex', 'exec', '--skip-git-repo-check', '--dangerously-bypass-approvals-and-sandbox', '-C', RAIZ, prompt],
                           capture_output=True, text=True, timeout=2700, env=env).stdout
        r = r.split('\ntokens used')[0].strip() or '(ChatGPT no respondió, intenta otra vez)'
    except subprocess.TimeoutExpired:
        r = '(Se tardó más de 45 min; pídeme el estado otra vez)'
    with open(HIST, 'a') as f: f.write(f'Carlos: {texto}\nChatGPT: {r}\n')
    return r


vistos = cargar()
print(time.strftime('%H:%M:%S'), 'puente activo', flush=True)
while True:
    try:
        for m in mensajes():
            if not isinstance(m, dict): continue   # WaAPI a veces devuelve texto de error en vez de mensajes
            mid = m.get('id'); mid = mid.get('_serialized') if isinstance(mid, dict) else mid
            cuerpo = m.get('body') or ''
            if m.get('type') != 'chat' or not mid or mid in vistos or not PREFIJO.match(cuerpo): continue
            vistos.add(mid); json.dump(sorted(vistos)[-500:], open(VISTOS, 'w'))
            if m.get('t', 0) < INICIO - 120: continue   # no contestar mensajes viejos al arrancar
            pregunta = PREFIJO.sub('', cuerpo, count=1).strip()
            print(time.strftime('%H:%M:%S'), 'pregunta:', pregunta[:80], flush=True)
            accion('send-message', {'chatId': CHAT, 'message': '🤖 ChatGPT: ⏳ trabajando…'})
            accion('send-message', {'chatId': CHAT, 'message': '🤖 ChatGPT: ' + responder(pregunta)[:3800]})
    except Exception as e:
        print(time.strftime('%H:%M:%S'), 'error', str(e)[:200], flush=True)
    time.sleep(12)
