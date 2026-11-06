"""Cinthia pidió que la peonía del logo sea la abierta del reverso: cambia el capullo del icono B por esa flor → iconos/icono_b2p.png"""
from PIL import Image, ImageDraw, ImageChops
from armar_logo import AQUI

im = Image.open(AQUI / 'iconos' / 'icono_b1.png').convert('RGB')
d = ImageDraw.Draw(im)
d.rectangle((418, 150, 622, 240), fill='white')   # capullo sin tocar las puntas del aro
d.rectangle((398, 240, 632, 368), fill='white')
fl = Image.open(AQUI / 'refs' / 'peonia_flor.png').convert('RGB')
ancho = 300; fl = fl.resize((ancho, int(fl.height * ancho / fl.width)), Image.LANCZOS)
m = ImageChops.invert(fl.convert('L')).point(lambda v: min(255, v * 5))
x, y = 515 - ancho // 2, 372 - fl.height
im.paste(fl, (x, y), m)
im.save(AQUI / 'iconos' / 'icono_b2p.png')
im.crop((250, 60, 780, 520)).save('/tmp/claude-1000/-workspaces-Nexusv2-0launch18octubre/632e0195-4202-422b-a741-74f9ff894c0c/scratchpad/b2p_top.png')
