"""Ideas de Instagram por cliente/prospecto (30 oct): reels más vistos por hashtags de su nicho → ideas.json para la página de aprobación."""
import json, os, urllib.request
T = os.environ['APIFY_TOKEN']
N = {  # nombre: (tipo, hashtags)
 'Guillermo · herrería': ('cliente', ['herreria', 'portonesdeherreria', 'pergolas']),
 'José · impermeabilización': ('cliente', ['impermeabilizacion', 'impermeabilizante', 'techosimpermeables']),
 'Giovanni · abogado divorcios': ('cliente', ['abogadodivorcios', 'divorcio', 'abogadofamiliar']),
 'Víctor · limpieza empresas': ('cliente', ['limpiezacomercial', 'limpiezadeoficinas', 'serviciodelimpieza']),
 'BD Pro · pistas de baile': ('cliente', ['pistadebaile', 'pistailuminada', 'renta de pista']),
 'Manuel · fotografía XV': ('cliente', ['fotografiaxv', 'xvanos', 'quinceañera']),
 'Lisbeth · terrenos': ('cliente', ['terrenosenventa', 'lotesenventa', 'bienesraicesmexico']),
 'Alberto · dental': ('cliente', ['carillasdentales', 'diseñodesonrisa', 'implantesdentales']),
 'Fernando · punto de venta': ('cliente', ['puntodeventa', 'sistemapos', 'emprendedoresmexico']),
 'Mariano · casas': ('cliente', ['casasenventa', 'recorridovirtual', 'casadelujo']),
 'Israel · pantallas LED': ('cliente', ['pantallasled', 'pantallaled', 'publicidadled']),
 'Iván · fumigación': ('cliente', ['fumigacion', 'controldeplagas', 'fumigador']),
 'Uriel · consultor': ('cliente', ['consultoriaempresarial', 'dueñosdenegocio', 'liderazgoempresarial']),
 'Rubén · quiropráctico': ('prospecto', ['quiropractico', 'alphabiotismo', 'dolordeespalda']),
 'Rachel · micropigmentación': ('prospecto', ['micropigmentacion', 'microblading', 'cejas']),
 'Verónica · inmobiliaria': ('prospecto', ['asesorinmobiliario', 'departamentosenventa', 'inmobiliaria']),
 'Generadores · plantas de luz': ('prospecto', ['plantasdeluz', 'generadorelectrico', 'generadores']),
 'Blanca · terapia de lenguaje': ('prospecto', ['terapiadelenguaje', 'lenguajeinfantil', 'logopedia']),
 'Mariachi': ('prospecto', ['mariachi', 'serenata', 'mariachiguadalajara']),
}
out = {}
for n, (tipo, tags) in N.items():
    tags = [t.replace(' ', '') for t in tags]
    try:
        r = urllib.request.Request(f'https://api.apify.com/v2/acts/apify~instagram-hashtag-scraper/run-sync-get-dataset-items?token={T}&timeout=280',
                                   data=json.dumps({'hashtags': tags, 'resultsType': 'reels', 'resultsLimit': 20}).encode(), headers={'Content-Type': 'application/json'})
        it = [x for x in json.loads(urllib.request.urlopen(r, timeout=300).read()) if x.get('videoUrl')]
    except Exception as e:
        print(n, 'error', e, flush=True); continue
    it.sort(key=lambda x: -(x.get('videoPlayCount') or x.get('videoViewCount') or 0))
    vistos, sel = set(), []
    for x in it:
        if x.get('ownerUsername') in vistos: continue
        vistos.add(x.get('ownerUsername')); sel.append({'cuenta': x.get('ownerUsername'), 'vistas': x.get('videoPlayCount') or x.get('videoViewCount'), 'url': x.get('url'),
                                                       'video': x.get('videoUrl'), 'portada': x.get('displayUrl'), 'texto': (x.get('caption') or '')[:220], 'duracion': x.get('videoDuration')})
        if len(sel) == 4: break
    out[n] = {'tipo': tipo, 'ideas': sel}; json.dump(out, open('ideas.json', 'w'), ensure_ascii=False, indent=1)
    print(n, [(s['cuenta'], s['vistas']) for s in sel], flush=True)
