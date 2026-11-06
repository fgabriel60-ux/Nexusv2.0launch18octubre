from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
caps=(ROOT/'visionagenciaIAV2.0-main 2/entregables/glimmer_consultas_20261020/capacidades_video.txt').read_text()
base='Responde en español, SOLO LA RESPUESTA FINAL, sin razonamiento interno. Evalúa con criterio exigente los cuadros de este video. Son fotogramas, NO puedes oír audio ni comprobar sincronía labial; no lo afirmes. Da notas reales de 1 a 10 para gancho, legibilidad, claridad de oferta, calidad visual y CTA; identifica hasta 3 defectos concretos visibles con su tiempo aproximado y propone cambios realizables. No exijas 10/10 ni inventes defectos. '+caps
jobs=[]
for name,context,refs in [
 ('Flyers','Cuatro flyers animados de Mariano, 7s cada uno. Entran textos originales extraídos por capas, no reescritos. Las primeras imágenes son las hojas temporales de los cuatro videos y después vienen los originales de los dos nuevos. Compara los textos y precios con los originales. Los primeros 0.2s tienen aparición progresiva deliberada; toda la oferta queda visible desde 2s. Da evaluación separada por flyer. No exigimos CTA nuevo porque preservamos fielmente los originales.', ['Benjamina','Bugambilia_pareja','Sotol_familia','Bugambilia_mejor_opcion']),
 ('Pixar','Anuncio de Nexus. Se reutiliza voz original sin alterarla. Métricas confirmadas: costo por mensaje 13.76 a 5, JR 80 mensajes a 6.43 y CTR 3.91%, Servilin 6 a 2.21. Llamada de 10min gratis; mensualidad de 500 si le gusta la estrategia. CTA comenta VIDEO o agenda llamada. Efectos adaptados: vidrio, toggles, teléfono, giro, match cut, screen push. Califica oferta/confianza además. Notas antiguas de v3: oferta4, confianza5, calidad8; evalúa esta versión independientemente.', ['Pixar']),
 ('Dental','Video de la Dra. Ángeles con modelos dentales superpuestos y subtítulos. Datos del cliente: implante desde12500MXN, corona aparte, anestesia local, WhatsApp6311651910. La voz es genérica autorizada del pipeline; no se presenta como grabación de voz real. Evalúa solo claridad visual, colocación de subtítulos, oferta y cierre, no hagas diagnóstico médico.', ['Dental']),
 ('Spiderman','Mariano salta de la casa, aterriza y habla; después casas reales, precios y CTA. Dron y noche son visualizaciones y están rotuladas. Comprueba manos/rostro, legibilidad de subtítulos y tarjetas. Precios de su narración original: Sotol1.4, Bugambilia2.4, Benjamina2.8 y Salvia3.1 millones. Flyers separados usan ofertas posteriores de 2.45 y2.85; no cambiar voz al revisar estas hojas.', ['Spiderman']),
 ('Pajaro','Visualización de un pájaro de nitinol: bola, lanzamiento con una mano, despliegue, corredera, aleteo y reenrollado. No es simulación física; admite que la IA interpreta engranajes y espirales. Evalúa mecanismo visible, continuidad y fases. No le exijas CTA de anuncio ni oferta; usa criterios propios de visualización mecánica.', ['Pajaro'])]:
    photos=[str(OUT/'revisiones'/f'{n}.jpg') for n in refs]
    if not all(Path(p).exists() for p in photos):continue
    if name=='Flyers':photos += [str(ROOT/'clientes/Mariano/flyers_recibidos'/f) for f in ['1018_005111_BA9020.jpg','1020_210408_4AF9D8.jpg']]
    jobs.append({'nombre':name,'prompt':base+'\nCONTEXTO: '+context,'fotos':photos})
# Dos consultas para evitar repetir cargas y contexto por cada video.
flyers = [j for j in jobs if j['nombre']=='Flyers']
rest = [j for j in jobs if j['nombre'] in ('Pixar','Dental','Spiderman')]
if rest:
    flyers.append({'nombre':'Anuncios', 'prompt':base+'\nEvalúa POR SEPARADO cada anuncio; usa como máximo 150 palabras por anuncio y una tabla de notas. Las hojas están en el siguiente orden: '+', '.join(j['nombre'] for j in rest)+'\n'+'\n'.join(j['nombre']+': '+j['prompt'].split('CONTEXTO: ')[-1] for j in rest), 'fotos':[f for j in rest for f in j['fotos']]})
jobs=flyers
(OUT/'lote_glimmer.json').write_text(json.dumps(jobs,ensure_ascii=False,indent=2))
print([j['nombre'] for j in jobs])
