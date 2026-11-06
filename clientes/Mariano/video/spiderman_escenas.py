"""Mariano · gancho «estilo Spiderman» (reel DbtClvhPXju): Mariano cae desde el techo de la casa Salvia REAL de Vizcaíno, aterriza en pose de superhéroe
en el camino de entrada, se levanta y con su voz clonada (labios guiados por el wav) dice «¿Buscas casa en Rosarito? Vizcaíno Residencial, ¡mira esto!»
y levanta el brazo al cielo → dron (visualización), Salvia de noche (visualización) y cierre de Mariano frente a la Benjamina con el CTA.
Cuadros: Qwen-Image-Edit-2511 desde fotos/cuadros REALES (refs en spiderman/refs). Tomas: MiniMax H3 704×1280 (múltiplos de 32), UNA sola GPU.
Uso: python3 spiderman_escenas.py rN [cuadro1,cuadro2,...] [toma1,toma2,...] [semilla]
     (sin listas o «-» = todo; «ninguna» en tomas = solo cuadros; los cuadros que no se pidan se reutilizan de la ronda anterior que los tenga como «listos»)"""
import sys
from pathlib import Path
sys.path.insert(0, '/workspaces/Nexusv2.0launch18octubre/clientes/_productor')
from escenas_modal import app, escenas

AQUI = Path(__file__).resolve().parent
SP = AQUI / 'spiderman'
REFS = SP / 'refs'
CARA = ('Conserva EXACTAMENTE la cara de este hombre de la primera imagen: mismos ojos, cejas, nariz, boca, barba de candado con canas, cabeza casi rapada, '
        'edad, complexión robusta y tono de piel moreno claro. Viste EXACTAMENTE como en la primera imagen: saco azul claro de cuadros puesto, camisa blanca abotonada, '
        'jeans azules y zapatos cafés, completamente vestido. ')
LUZ = ('Luz de sol natural de mediodía de Baja California, cielo azul limpio, colores reales y naturales (fachada color arena/gris claro, NO naranja), '
       'foto vertical 9:16, cinematográfica, nítida, sin texto, sin letras, sin logotipos, sin celulares.')
CUADROS = {
    'J0_aire': (['mariano', 'salvia'], CARA + 'Toma gran angular de 16 mm desde el piso del camino de entrada, mirando hacia arriba a ESTA misma casa de tres pisos: '
                'el hombre va SALTANDO EN EL AIRE desde el borde del techo plano de ESTA casa, a la altura del tercer piso, cuerpo completo pequeño contra el cielo, '
                'piernas dobladas y brazos abiertos como superhéroe cayendo. La misma fachada, las mismas ventanas, las mismas franjas de pasto. ' + LUZ),
    'J1_aterriza': (['mariano', 'salvia'], CARA + 'Toma gran angular de 18 mm a la altura de la cadera: el hombre acaba de aterrizar en pose de superhéroe, agachado '
                    'con las rodillas dobladas y la mano derecha apoyada en el concreto del camino de entrada, el otro brazo atrás, mirando con una sonrisa segura '
                    'directo a cámara, cuerpo completo en el centro del cuadro, frente a ESTA misma casa de tres pisos (la misma fachada, puerta, ventanas y '
                    'franjas de pasto) que se ve completa detrás de él. Sombra larga y marcada en el concreto. ' + LUZ),
    'N_noche': (['salvia'], 'La MISMA casa de tres pisos, el mismo encuadre y la misma fachada, pero de noche en la hora azul: cielo azul profundo con algunas '
                'estrellas, luces cálidas encendidas dentro de todas las ventanas y en la puerta de entrada, lámparas del techo de la entrada encendidas, el pasto '
                'y el concreto iluminados suavemente. Sin personas. Foto vertical 9:16 de arquitectura, cinematográfica, nítida, sin texto, sin letras.'),
    'D_aereo': (['salvia', 'padel'], 'Vista aérea de dron a gran altura, mirando en diagonal hacia el mar, sobre este desarrollo de casas nuevas de tres pisos '
                'color arena con techos planos (como la primera imagen): filas ordenadas de casas, calles de concreto y pequeños patios traseros con pasto verde '
                '(SIN canchas en los patios). En UNA sola área común junto al desarrollo hay DOS canchas de pádel azules juntas, como en la segunda imagen. '
                'Alrededor lomas secas de Baja California y al fondo el mar del Pacífico en el horizonte, cielo azul limpio. Foto vertical 9:16 de dron, '
                'cinematográfica, colores naturales, nítida, sin texto, sin letras.'),
    'K_cierre': (['mariano', 'benjamina'], CARA + 'Plano medio CERRADO: de la cintura a la cabeza, la cámara a un metro de él, su torso llena la mitad '
                 'inferior del cuadro y su cara se ve grande y nítida. Está de pie en el camino de entrada de concreto frente a ESTA misma casa (la misma '
                 'fachada clara con azulejo café oscuro y la puerta de entrada), sonriente, mirando a cámara y apuntando con el dedo índice derecho hacia '
                 'la cámara, lente de 50 mm, la casa desenfocada detrás. ' + LUZ),
}
HABLA = (' He speaks Spanish to the camera with natural lip movement matching the speech, confident friendly expression. Keep his face and clothes exactly '
         '(light blue checked blazer, white shirt). No phone, no text. Audio: clear male voice speaking Spanish.')
TOMAS = {
    'S_salto': ('J0_aire', 'Vertical wide low-angle shot: the man jumps off the flat rooftop and falls fast through the air down to the driveway, landing hard in a '
                'superhero crouch with one hand on the concrete, a small puff of dust and a camera shake on impact. Keep the same house. No text. Audio: wind whoosh '
                'and a heavy landing thud, no speech.', 5.0, 'J1_aterriza'),
    'S_habla': ('J1_aterriza', 'Vertical full-body shot on the driveway: the man rises from the superhero crouch and stands up straight, then talks to the camera. '
                'On the last words he raises his right arm high and points up to the sky. Slow handheld push-in, sunny day.' + HABLA, 4.6, None, 'gancho'),
    'S_aereo': ('D_aereo', 'Fast cinematic FPV drone shot flying forward and slightly down over the rows of houses toward the padel courts and the ocean, smooth, '
                'horizon level. No text. Audio: wind, no speech.', 5.0),
    'S_noche': ('N_noche', 'Slow cinematic push-in toward the house at blue hour, the warm interior lights glow softly, stars twinkle. Keep the house exactly. '
                'No people, no text. Audio: soft night ambience, no speech.', 5.0),
    'S_cierre': ('K_cierre', 'Vertical medium shot, slow push-in, he smiles and points at the camera while talking.' + HABLA, 3.4, None, 'cta'),
}


def main():
    ronda = sys.argv[1]
    pedir_c = ([] if sys.argv[2] == 'ninguna' else sys.argv[2].split(',')) if len(sys.argv) > 2 and sys.argv[2] != '-' else list(CUADROS)
    pedir_t = ([] if sys.argv[3] == 'ninguna' else sys.argv[3].split(',')) if len(sys.argv) > 3 and sys.argv[3] != '-' else list(TOMAS)
    semilla = int(sys.argv[4]) if len(sys.argv) > 4 else 12
    sal = SP / ronda; sal.mkdir(parents=True, exist_ok=True)
    refs = {'mariano': (AQUI.parent / 'fotos' / 'mariano_luz_final.png').read_bytes(), 'salvia': (REFS / 'salvia_fachada.png').read_bytes(),
            'benjamina': (REFS / 'benjamina_fachada.png').read_bytes(), 'padel': (REFS / 'salvia_padel.png').read_bytes()}
    # cuadros que se necesitan pero no se piden: el más reciente que exista en cualquier ronda
    usados = {x for t in pedir_t for x in (TOMAS[t][0], TOMAS[t][3] if len(TOMAS[t]) > 3 else None) if x}
    listos = {}
    for c in usados - set(pedir_c):
        hechos = sorted(SP.glob(f'r*/{c}.png'), key=lambda p: p.stat().st_mtime)
        if not hechos: raise SystemExit(f'falta el cuadro {c}: pídelo')
        listos[c] = hechos[-1].read_bytes(); print('reuso', hechos[-1], flush=True)
    voces = {n: (SP / 'voz' / f'{n}.wav').read_bytes() for n in ('gancho', 'cta')}
    tomas = [(n, *TOMAS[n]) for n in pedir_t]
    with app.run():
        res = escenas.remote(f'mariano_spider_{ronda}', refs, {c: CUADROS[c] for c in pedir_c}, tomas, semilla, listos, voces, (704, 1280))
    for n, b in res.items():
        (sal / n).write_bytes(b); print('guardado', sal / n, flush=True)


if __name__ == '__main__':
    main()
