"""Arma el mensaje de calificación de Glimmer que convence de invertir (regla de Carlos, 30 oct):
traduce la calificación a dinero con casos REALES y dice cuántos mensajes puede esperar el cliente.
Uso: from mensaje_calificacion import mensaje; print(mensaje('Rubén', 7, 8.5, ['...'], ['...'], pauta=250))"""

COSTO_8 = 4.56          # Guillermo, anuncio calificado 8.2: $4.56 por mensaje (resultado real)
CASOS = ('• Guillermo (herrería, Puebla): su anuncio calificó 8.2 → le llegaron mensajes a $4.56 c/u y cerró trabajos.\n'
         '• Anuncios con 6: casi no llegaron mensajes; se pagó por vistas, no por clientes.\n'
         '• Nuestra propia campaña: pasó de $13.76 a $5.01 por mensaje al subir la calificación.')


def mensaje(nombre, hoy, proyectada, funciona, falta, pauta=250, hecho=()):
    esperados = int(pauta / COSTO_8)
    if hoy >= 8:
        estado = f'✅ Ya está en {hoy}/10: listo para subir.'
    else:
        estado = (f'Hoy está en {hoy}/10 → con los ajustes llega a {proyectada}/10.\n'
                  f'No lo subimos hasta llegar a 8: con menos de 8 se paga por vistas y no llegan mensajes.')
    t = [f'📊 *{nombre}* · calificación de Facebook (su IA)', '', estado, '',
         '💰 *Lo que significa en dinero* (resultados reales):', CASOS, '',
         f'👉 Con una calificación de 8 o más y ${pauta} de pauta, puede esperar alrededor de *{esperados} mensajes* '
         f'de personas interesadas (a ~${COSTO_8} c/u, como Guillermo).', '',
         '✅ *Por qué funciona su video:*'] + [f'• {x}' for x in funciona]
    if hecho: t += ['', '🔧 *Ya corregido:*'] + [f'• {x}' for x in hecho]
    if falta: t += ['', f'🎯 *Para llegar a {proyectada}:*'] + [f'• {x}' for x in falta]
    return '\n'.join(t)
