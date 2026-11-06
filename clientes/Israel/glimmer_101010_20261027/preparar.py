"""Lote de Glimmer para Israel (SIRLed): plan para recrear las 3 referencias de Instagram + guion 10/10/10 que Israel lee con su voz."""
import json
from pathlib import Path
AQUI = Path(__file__).resolve().parent
tr = json.loads((AQUI / 'transcripciones.json').read_text())
caps = Path('/workspaces/Nexusv2.0launch18octubre/visionagenciaIAV2.0-main 2/entregables/glimmer_consultas_20261020/capacidades_video.txt').read_text()

prompt = f"""Eres estratega de anuncios de Meta (Facebook/Instagram) para negocios en México y director de video. Da SOLO la respuesta final, en español, sin mostrar tu razonamiento.

CLIENTE: Israel, dueño de SIRLed (antes «Servicio de Ingeniería y Reparación»; su letrero en el taller todavía dice eso). Vende, instala y repara pantallas LED para negocios (bares, restaurantes, tiendas, iglesias, eventos). WhatsApp 55 7503 1182. Su material real (imagen 4): instalaciones terminadas en bares y restaurantes (partidos de béisbol, hockey y básquet en pantalla gigante), módulos LED de cerca, gabinetes y cajas de transporte, su taller con su letrero, él y su equipo armando estructuras, pantallas con video de la ciudad y de naturaleza.
En un anuncio anterior él mencionaba: equipos de importación directa y manufactura de alta calidad, tecnología que se adapta al presupuesto y «te incluimos tus primeros videos publicitarios gratis al instalar». NO tenemos precios, medidas ni modelos (pitch) de sus pantallas, ni tiempos de instalación, ni garantía: escribe [POR CONFIRMAR CON ISRAEL] donde haga falta y no inventes cifras.
Videos anteriores que le hicimos (v1 y v2, 28 s): voz en off genérica sobre sus videos reales, con música, subtítulos y tarjeta final con WhatsApp. Calificación anterior: oferta 8, confianza 9, calidad 9. Falta su voz real: Israel acaba de pedir «envíeme un guion para leerlo» y va a grabarlo con su celular. También puede grabarse a cuadro si se lo pedimos.

REFERENCIAS DE INSTAGRAM que Carlos le mandó (imágenes 1 a 3 = hojas de 8 cuadros de cada reel, en este orden):
1. Reel Dbjy5rnujqg (30 s, presentación de producto): una mujer junto a dos pantallas LED verticales tipo tótem en una oficina, la cámara muestra la parte trasera y las ruedas, textos con el modelo y brillo («P2.4 1,000 nits», «P3.9 5,000 nits»), luego tomas de pantallas en vitrinas y una sala de juntas. Audio: «{tr['Dbjy5rnujqg']['texto']}»
2. Reel DZW99XNtlqQ (26 s, proceso/«detrás de cámaras» estilo cine, marca Gramola): manos abriendo cajas de transporte, cables, broches, gente armando y levantando módulos en un taller, la pantalla enciende con un video de humo de colores y luego un partido de futbol, cierre con logo. Música sin voz (en francés).
3. Reel DduYDrtJQJa (14 s, antes y después, marca Leds Go; Carlos dice que es «el más potente»): cámara rápida del montaje en un salón de eventos vacío, con textos irónicos en pantalla: «“La IA te va a dejar sin trabajo”» → «¿Ah sí?» → «¿Cuándo?» → «¿Seguimos esperando?», y la revelación final: el salón de XV años terminado con la pantalla LED mostrando un castillo, luces y la quinceañera. Canción comercial en inglés (no se puede usar).
Imagen 4: material real de Israel (fotos y cuadros de sus videos).

{caps}
Adaptación para este cliente: SÍ tenemos 45 fotos y 36 videos reales de Israel (instalaciones, taller, equipo, pantallas encendidas). Él va a grabar su voz leyendo el guion y puede grabar tomas nuevas con su celular (montajes en cámara rápida, él a cuadro, encendido de pantalla) si se las pedimos claramente. NO tenemos una modelo como la del reel 1 ni salones de XV propios a menos que él los tenga.

TAREA:
A) PLAN PARA RECREAR CADA REFERENCIA con el material de Israel (un video por referencia). Para cada una: qué copiar y qué NO, escenas (tabla: #, segundos, qué se ve y fuente —su video real / su foto / grabar Israel / Qwen / H3—, texto en pantalla exacto, sonido), qué tomas debe grabar Israel (instrucciones concretas: encuadre, cámara rápida, luz, duración) y una calificación esperada.
B) GUION 10/10/10 PARA QUE ISRAEL LO LEA CON SU VOZ (el entregable principal para mandarle hoy): un guion de 25-35 s, palabra por palabra, en lenguaje natural de dueño de negocio mexicano (que suene a él, no a locutor), que sirva sobre el video que mejor funcione de los tres (dilo). Debe cumplir la FÓRMULA 10/10/10: Confianza 10/10, Claridad de la oferta 10/10, Probabilidad de mensajes calificados por WhatsApp 10/10. Incluye:
 1) 3 ganchos de 0-3 s y el mejor.
 2) El guion final palabra por palabra, separado en frases cortas (una por línea) para que lo lea fácil.
 3) Indicaciones para grabar el audio con su celular (lugar, distancia, tono, cuántas tomas, que lo mande como nota de voz o archivo).
 4) CTA exacto y 2-3 preguntas de precalificación para WhatsApp (tipo de negocio, medida aproximada/ubicación, interior o exterior, presupuesto/fecha).
 5) Qué NO decir (políticas de Meta, sin inventar datos) y qué datos hay que confirmarle a Israel.
 6) Calificación honesta Confianza/Claridad/Mensajes (x/10) y qué falta para 10/10/10."""
fotos = [str(AQUI / f'ref_{n}.jpg') for n in ('Dbjy5rnujqg', 'DZW99XNtlqQ', 'DduYDrtJQJa')] + [str(AQUI / 'material_israel.jpg')]
(AQUI / 'prompt.txt').write_text(prompt)
(AQUI / 'lote.json').write_text(json.dumps([{'nombre': 'israel_sirled', 'prompt': prompt, 'fotos': fotos}], ensure_ascii=False))
print(len(prompt))
