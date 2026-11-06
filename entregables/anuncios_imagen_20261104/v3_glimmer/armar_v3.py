"""Tipografía vectorial en postproducción sobre fotografías creadas con imagegen.
Ejecutar desde esta carpeta: python armar_v3.py
"""
import base64, json, shutil
from pathlib import Path
from html import escape
import cairosvg
from PIL import ImageFont, Image

ROOT = Path(__file__).resolve().parent
NAVY = '#0B1D35'
COPY = {
 'MARIANO_v3_A1': (['3 casas en','Vizcaíno'],80,'Bugambilia · Benjamina · Salvia',['Recorrido con Mariano','Compara las tres opciones'],'Pide el recorrido por WhatsApp'),
 'MARIANO_v3_A2': (['Conoce las casas','por dentro'],80,'Recorre Vizcaíno Residencial con Mariano',['Bugambilia, Benjamina y Salvia','Compara tus opciones'],'Pide el recorrido por WhatsApp'),
 'MARIANO_v3_B1': (['Conoce tu próxima','casa: Benjamina'],72,'Consulta precio y disponibilidad con Mariano',['Vizcaíno Residencial','Recorrido de la casa'],'Consulta por WhatsApp'),
 'MARIANO_v3_B2': (['Agenda tu visita','a Benjamina'],80,'Conoce la casa con Mariano',['Consulta disponibilidad','Pregunta por el precio vigente'],'Agenda por WhatsApp'),
 'RAFAEL_v3_1A': (['Agenda tu prueba','de manejo'],76,'Coordina tu visita con Rafael',['Atención por WhatsApp','Confirma el horario'],'Agenda por WhatsApp'),
 'RAFAEL_v3_1B': (['Súbete y conoce','tu próximo BYD'],78,'Agenda tu prueba de manejo con Rafael',['Consulta disponibilidad','Coordina tu horario'],'Pide tu prueba por WhatsApp'),
 'RAFAEL_v3_2A': (['Habla con Rafael,','asesor BYD'],76,'Información para elegir tu próximo auto',['Versiones y disponibilidad','Coordina tu visita'],'Escríbele por WhatsApp'),
 'RAFAEL_v3_2B': (['Pregunta por tu','BYD por WhatsApp'],72,'Consulta versiones y disponibilidad con Rafael',['Información del auto','Agenda tu visita'],'Escríbele a Rafael por WhatsApp'),
}

def text(x,y,s,size,weight='bold'):
 font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans'+('-Bold' if weight=='bold' else '')+'.ttf',size)
 assert font.getlength(s) <= 864, (s,font.getlength(s))
 return f'<text x="{x}" y="{y}" fill="white" font-family="DejaVu Sans" font-weight="{weight}" font-size="{size}">{escape(s)}</text>'

def main():
 (ROOT/'fuentes').mkdir(exist_ok=True)
 (ROOT/'editables').mkdir(exist_ok=True)
 manifest=json.loads((ROOT/'produccion.json').read_text())
 for row in manifest['imagenes']:
  name=row['id']; src=Path(row['path'])
  saved=ROOT/'fuentes'/f'{name}_imagegen.png'
  if src.exists() and src!=saved: shutil.copy2(src,saved)
  data=base64.b64encode(saved.read_bytes()).decode()
  headline,size,support,bullets,cta=COPY[name]
  assert len(' '.join(headline).split())<=8 and len(support.split())<=10
  brand='MARIANO · VIZCAÍNO RESIDENCIAL' if name.startswith('MARIANO') else 'RAFAEL · ASESOR BYD'
  photo_y=-25
  photo_tag=f'<image x="0" y="{photo_y}" width="1080" height="1350" preserveAspectRatio="none" xlink:href="data:image/png;base64,{data}" clip-path="url(#hero)"/>'
  if name.startswith('RAFAEL'):
   clean=base64.b64encode((ROOT/'fuentes'/'RAFAEL_hero_sin_texto.png').read_bytes()).decode()
   x,y,w,h=(-108,110,1188,668) if name.endswith('2A') else (0,135,1080,605)
   photo_tag=f'<image x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice" xlink:href="data:image/png;base64,{clean}" clip-path="url(#hero)"/>'
  svg=f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1080" height="1350" viewBox="0 0 1080 1350">
  <defs><clipPath id="hero"><rect y="135" width="1080" height="605"/></clipPath></defs>
  <rect width="1080" height="1350" fill="{NAVY}"/>
  {photo_tag}
  '''
  svg+=text(108,58,brand,28)
  if name.startswith('MARIANO'): svg+=text(108,99,'Rosarito, B.C.',24,'normal')
  svg+=text(108,825,headline[0],size)+text(108,912,headline[1],size)
  svg+=text(108,974,support,36,'normal')
  for y,bullet in zip([1030,1077],bullets):
   svg+=f'<path d="M111 {y-12} l8 8 l16 -19" fill="none" stroke="white" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
   svg+=text(150,y,bullet,30,'normal')
  svg+='<rect x="108" y="1140" width="864" height="90" rx="22" fill="#087F3C"/>'
  svg+='<g transform="translate(137 1157)" fill="none" stroke="white" stroke-width="3.4"><path d="M6 48 l3 -11 a23 23 0 1 1 9 9 Z"/><path d="M20 13 q-8 5 3 18 q10 11 17 4 l-7 -6 l-4 3 q-7 -3 -9 -10 l4 -3 Z"/></g>'
  svg+=text(210,1197,cta,36)
  svg+='</svg>'
  (ROOT/'editables'/f'{name}.svg').write_text(svg)
  cairosvg.svg2png(bytestring=svg.encode(),write_to=str(ROOT/f'{name}.png'))
  with Image.open(ROOT/f'{name}.png') as im: assert im.size==(1080,1350)
  print(name,'1080x1350 OK')

if __name__=='__main__': main()
