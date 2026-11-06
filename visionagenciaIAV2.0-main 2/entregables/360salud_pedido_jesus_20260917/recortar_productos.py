"""Recorta el frasco de capsulas y el bote de balsamo de la foto que mando Jesus (17 sep 11:27)."""
from pathlib import Path
from PIL import Image
from rembg import new_session, remove

AQUI = Path(__file__).resolve().parent
PROD = AQUI / 'productos'
PROD.mkdir(exist_ok=True)

SESION = new_session('u2net')  # bria-rmbg (1 GB) tumba el proceso con 7 GB de RAM
foto = Image.open(AQUI / 'imagenes' / '112720_JESUS_image.jpg').convert('RGB')
print('foto:', foto.size)

# recortes generosos; rembg quita el fondo (banqueta, tablero del carro)
cortes = {
    'capsulas': (0, 55, 385, 765),
    'balsamo': (330, 160, 800, 730),
}
for nombre, caja in cortes.items():
    trozo = foto.crop(caja)
    sin_fondo = remove(trozo, session=SESION)
    sin_fondo = sin_fondo.crop(sin_fondo.getbbox())   # aprieta al producto
    grande = sin_fondo.resize((sin_fondo.width * 3, sin_fondo.height * 3), Image.LANCZOS)
    grande.save(PROD / f'{nombre}.png')
    print(nombre, caja, '->', grande.size)
