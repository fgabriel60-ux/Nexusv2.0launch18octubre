"""Junta los planes 10/10/10 de Glimmer de todos los clientes y prospectos → un .md por cliente en esta carpeta + planes.html (artifact).
Fuentes: respuestas guardadas en clientes/*/glimmer_101010_*, entregables/glimmer_*, y las tandas de entregables/planes_glimmer_20261030 (se agregan al terminar)."""
import html, json, re
from pathlib import Path
R = Path('/workspaces/Nexusv2.0launch18octubre'); AQUI = Path(__file__).resolve().parent


def final(t):
    """Respuesta final de Glimmer: lo que va después de «assistant to=user»; si no, desde la última calificación/plan."""
    k = t.rfind('assistant to=user')
    if k >= 0: return t[k + 17:].strip()
    for pat in (r'\*\*1\)', r'1\) ', r'CALIFICACI[ÓO]N'):
        ms = [m.start() for m in re.finditer(pat, t)]
        if ms: return t[ms[-1] if pat.startswith('CAL') else ms[0]:].strip()
    return t[-4000:].strip()


def de_log(log):
    out = {}
    if not log.exists(): return out
    for p in re.split(r'\n######## ', log.read_text(errors='ignore'))[1:]:
        n, _, t = p.partition('\n'); out[n.strip()] = final(t.split('\nDuración')[0])
    return out


P = R / 'entregables/planes_glimmer_20261030'
L1, L2 = de_log(P / 'glimmer.log'), de_log(P / 'glimmer_clientes.log')
leer = lambda p: (R / p).read_text(errors='ignore') if (R / p).exists() else ''
E = 'entregables/glimmer_evaluador/20261030/'
# (cliente, tipo, estado, [(título, texto)])
C = [
 ('Guillermo · herrería', 'cliente', 'Paga mensual', [('Plan con la referencia @far12', L1.get('GUILLERMO_PLAN_FAR12', ''))]),
 ('José · Grupo JR', 'cliente', 'v8 lista', [('Qué hacer con la grieta y el inicio', L1.get('JOSE_GRIETA', ''))]),
 ('Giovanni · abogado', 'cliente', 'v4 en GPU', [('Plan 10/10/10 (28 oct)', leer('clientes/Giovanni/glimmer_101010_20261028/respuesta_final.md')), ('Campaña', leer('entregables/glimmer_campanas_20261029/GIOVANNI_CAMPANA.md'))]),
 ('Doctora Ángeles · Veneers', 'cliente', 'v5 con su voz', [('Guion con su forma de hablar', L1.get('DOCTORA_ESTILO', '')), ('Guiones 10/10/10 (27 oct)', leer('clientes/Alberto/glimmer_101010_20261027/GUIONES_VENEERS_10_10_10.md'))]),
 ('Mariano · casas Vizcaíno', 'cliente', 'Spider-Man en plan', [('Gancho Spider-Man y escenas en Vizcaíno', L1.get('MARIANO_SPIDERMAN', ''))]),
 ('Israel · pantallas LED', 'cliente', 'Pagó, falta su voz', [('Plan con sus 3 referencias', L2.get('PLAN_Israel', '')), ('Plan 10/10/10 (27 oct)', leer('clientes/Israel/glimmer_101010_20261027/respuesta_final.md'))]),
 ('BD Pro · pistas de baile', 'cliente', 'Sin mensajes', [('Video solo de pistas', L2.get('PLAN_BDPro', '')), ('Video de eventos empresariales (audio, escenarios, pantallas)', L2.get('PLAN_BDPro_eventos', ''))]),
 ('Fernando · punto de venta', 'cliente', 'Grabará su guion', [('Plan con su guion', L2.get('PLAN_Fernando', '')), ('Plan 10/10/10 (27 oct)', final(leer('clientes/Fernando/glimmer_101010_20261027/respuesta_glimmer.txt')))]),
 ('Lisbeth · terrenos', 'cliente', '5/10, faltan datos', [('Plan con sus referencias', L2.get('PLAN_Lisbeth', '')), ('Campaña', leer('entregables/glimmer_campanas_20261029/LISBETH_CAMPANA.md'))]),
 ('Iván · fumigación', 'cliente', 'Preguntones', [('Plan con sus referencias', L2.get('PLAN_Ivan', ''))]),
 ('Blanca · terapia de lenguaje', 'cliente', 'Calidad tipo Lisbeth', [('Plan', L2.get('PLAN_Blanca', ''))]),
 ('Víctor · limpieza empresas', 'cliente', 'Activar campaña', [('Plan', L2.get('PLAN_Victor', ''))]),
 ('Manuel · fotografía XV', 'cliente', 'Subir campaña', [('Plan', L2.get('PLAN_Manuel', ''))]),
 ('Uriel · consultor', 'cliente', 'Campaña apagada', [('Plan', L2.get('PLAN_Uriel', ''))]),
 ('Jesús · Rar~Amore', 'cliente', 'Revisar mensajes', [('Plan', L2.get('PLAN_RarAmore', ''))]),
 ('Tatuador · Cancún', 'prospecto', 'Escenas en GPU', [('Estrategia 10/10/10', leer(E + 'final_TATUADOR_ESTRATEGIA_101010.md'))]),
 ('Andrés · contratista', 'prospecto', 'Muestra v2 lista', [('Estrategia 10/10/10', leer(E + 'final_ANDRES_CONSTRUCCION_ESTRATEGIA_101010.md'))]),
 ('Jesús · carpintería Mazatlán', 'prospecto', 'Escenas en GPU', [('Estrategia 10/10/10', leer(E + 'final_JESUS_CARPINTERIA_ESTRATEGIA_101010.md'))]),
 ('Carpintería Cadena · cocinetas MTY', 'prospecto', 'Muestra por aprobar', [('Muestra', L1.get('COCINETAS_MTY_MUESTRA', '') or L2.get('PLAN_Cocinetas', ''))]),
 ('Rachel · micropigmentación', 'prospecto', 'Cuadros en GPU', [('Plan', '(Glimmer 9/9/9, 22 oct) Video de 30-35 s: la especialista se presenta + antes/después recortado + clienta de cuento original en su cabina real + montaje de cejas + «citas esta semana» + CTA «escribe CEJAS». Precio del anuncio: [CONFIRMAR con ella].')]),
 ('Rubén · quiropráctico (alphabiotista)', 'prospecto', 'Falta su audio', [('Plan con su referencia', L2.get('PLAN_Ruben', '')), ('Plan 10/10/10 (29 oct)', leer('clientes/Ruben_Quiropraxia/glimmer_101010_20261029/respuesta_final.md'))]),
 ('Generadores · plantas de luz', 'prospecto', 'Quiere ventas', [('Plan con sus referencias', L2.get('PLAN_Generadores', ''))]),
 ('Verónica · inmobiliaria Tampico', 'prospecto', 'Corregir voz y pesos', [('Plan', L2.get('PLAN_Veronica', ''))]),
 ('Antonio · cancelería CDMX', 'prospecto', 'Pedí fotos', [('Estrategia 10/10/10', leer(E + 'final_ANTONIO_CANCELERIA_ESTRATEGIA_101010.md'))]),
 ('Julio César · rosticería', 'prospecto', 'Pedí fotos', [('Estrategia 10/10/10', leer(E + 'final_JULIO_ROSTICERIA_ESTRATEGIA_101010.md'))]),
 ('Luz y sonido · Guadalajara', 'prospecto', 'Pedí videos', [('Estrategia 10/10/10', leer(E + 'final_LUZ_SONIDO_GDL_ESTRATEGIA_101010.md'))]),
 ('Casas fraccionamiento · 222 833 5354', 'prospecto', 'Pedí datos', [('Plan', L2.get('PLAN_Casas_222', ''))]),
]


def md2html(t):
    t = html.escape(t.strip()); t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t); out, lst = [], False
    for l in t.splitlines():
        s = l.strip()
        if re.match(r'^[\*\-•] ', s):
            if not lst: out.append('<ul>'); lst = True
            out.append('<li>' + s[2:] + '</li>'); continue
        if lst: out.append('</ul>'); lst = False
        if s.startswith('|'): out.append('<p class="tabla">' + s + '</p>'); continue
        if s.startswith('#'): out.append('<p><b>' + s.lstrip('# ') + '</b></p>'); continue
        if s: out.append('<p>' + s + '</p>')
    if lst: out.append('</ul>')
    return '\n'.join(out)


secs, listos = {'cliente': [], 'prospecto': []}, 0
for n, tipo, estado, planes in C:
    slug = re.sub(r'\W+', '_', n.split(' ·')[0]).strip('_')
    (AQUI / f'{slug}.md').write_text(f'# {n}\nEstado: {estado}\n\n' + '\n\n'.join(f'## {t}\n{x.strip() or "(pendiente: se agrega cuando Glimmer termine)"}' for t, x in planes))
    hay = any(x.strip() for _, x in planes); listos += hay
    cuerpo = ''.join(f'<details{" open" if i == 0 and x.strip() else ""}><summary>{html.escape(t)}</summary><div class="txt">{md2html(x) if x.strip() else "<p class=\"pend\">En Glimmer · se agrega en cuanto termine.</p>"}</div></details>' for i, (t, x) in enumerate(planes))
    secs[tipo].append(f'<article class="c" id="{slug.lower()}"><header><h3>{html.escape(n)}</h3><span class="chip {"ok" if hay else "pend"}">{html.escape(estado)}</span></header>{cuerpo}</article>')
nav = lambda tipo: ''.join(f'<a href="#{re.sub(r"[^a-z0-9_]", "", re.sub(chr(92) + "W+", "_", n.split(" ·")[0]).strip("_").lower())}">{html.escape(n.split(" ·")[0])}</a>' for n, t, *_ in C if t == tipo)
page = f'''<title>Planes 10/10/10</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@75..100,600..800&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* Layout: índice de clientes y prospectos arriba; una tarjeta por cliente con su estado y sus planes de Glimmer plegables (el primero abierto). */
:root {{ --bg:#f1f2ee; --paper:#fbfbf8; --ink:#1c2420; --muted:#5f6b65; --line:#d5dad4; --accent:#1f5f8b; --ok:#2d7a4a; --ok-soft:#dcefe2; --pend:#a06b00; --pend-soft:#f5ead0;
  --f-d:"Archivo","Arial Narrow",system-ui,sans-serif; --f-b:"IBM Plex Sans",system-ui,sans-serif; --f-m:"IBM Plex Mono",ui-monospace,monospace; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg:#131815; --paper:#1a201c; --ink:#e6ebe7; --muted:#9ba8a1; --line:#2d3631; --accent:#6fb2e0; --ok:#63c48a; --ok-soft:#183626; --pend:#e9b44d; --pend-soft:#3a2d10; color-scheme:dark }} }}
:root[data-theme="dark"] {{ --bg:#131815; --paper:#1a201c; --ink:#e6ebe7; --muted:#9ba8a1; --line:#2d3631; --accent:#6fb2e0; --ok:#63c48a; --ok-soft:#183626; --pend:#e9b44d; --pend-soft:#3a2d10; color-scheme:dark }}
body {{ background:var(--bg); color:var(--ink); font:15px/1.55 var(--f-b) }}
.wrap {{ max-width:920px; margin:0 auto; padding-block:28px 64px; padding-left:max(16px,env(safe-area-inset-left,0px)); padding-right:max(16px,env(safe-area-inset-right,0px)); display:grid; gap:18px }}
h1,h2,h3 {{ font-family:var(--f-d); font-stretch:80%; margin:0; text-wrap:balance }} h1 {{ font-size:clamp(28px,5vw,42px); font-weight:800 }} h2 {{ font-size:24px; font-weight:800; margin-top:10px }} h3 {{ font-size:19px; font-weight:800 }}
.eyebrow {{ font:500 12px var(--f-m); letter-spacing:.08em; text-transform:uppercase; color:var(--muted) }} .lead {{ color:var(--muted); margin:0; max-width:68ch }}
nav {{ display:flex; flex-wrap:wrap; gap:6px }} nav a {{ font:500 12px var(--f-m); padding:4px 10px; border-radius:99px; border:1px solid var(--line); background:var(--paper); color:var(--ink); text-decoration:none }}
.c {{ background:var(--paper); border:1px solid var(--line); border-radius:10px; padding:14px 16px; display:grid; gap:8px; min-width:0 }}
.c header {{ display:flex; justify-content:space-between; gap:10px; align-items:center; flex-wrap:wrap }}
.chip {{ font:600 12px var(--f-b); padding:3px 10px; border-radius:99px }} .ok {{ background:var(--ok-soft); color:var(--ok) }} .pend {{ background:var(--pend-soft); color:var(--pend) }}
details summary {{ cursor:pointer; font:600 14px var(--f-b); color:var(--accent) }} .txt {{ max-width:72ch; overflow-wrap:anywhere }} .txt p {{ margin:.45em 0 }} .txt ul {{ margin:.3em 0; padding-left:20px }}
.tabla {{ font:400 13px var(--f-m) }} p.pend {{ background:none; color:var(--muted) }}
a:focus-visible,summary:focus-visible {{ outline:2px solid var(--accent); outline-offset:2px }}
</style>
<div class="wrap">
<header style="display:grid;gap:8px"><div class="eyebrow">Visión Agencia · Glimmer · 30 oct 2026</div><h1>Planes 10/10/10 de clientes y prospectos</h1>
<p class="lead">Un plan por cliente y prospecto: confianza, claridad de la oferta y mensajes calificados. {listos} de {len(C)} ya tienen plan; los que dicen «en Glimmer» se agregan solos en cuanto termina. También están guardados como archivos en entregables/planes_101010.</p></header>
<h2>Clientes</h2><nav>{nav("cliente")}</nav>{"".join(secs["cliente"])}
<h2>Prospectos</h2><nav>{nav("prospecto")}</nav>{"".join(secs["prospecto"])}
</div>'''
(AQUI / 'planes.html').write_text(page); print(listos, 'de', len(C), 'con plan')
