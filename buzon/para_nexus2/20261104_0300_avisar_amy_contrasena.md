# Avisarle a Amy que ya quedó la contraseña de los choferes · 4 nov 2026

**Para el Claude de Modal (el que siempre está corriendo).** Carlos lo pidió a las 02:5x.

## Qué pasó
Amy (chat `281299671593046@lid`, +52 1 631 302 0074) pidió el 3 nov cambiar las contraseñas
de su app porque las sabía gente de administraciones pasadas. Se cambiaron las dos. La de
administración le funcionó («ya me dejó entrar»), **la de choferes no**, y ella ya la había
pasado al grupo: «me avisas corazón porque lo pasé al grupo y ya tengo encima a los choferes».

## Por qué fallaba
El servidor comparaba la contraseña exacta y el teclado del celular pone mayúscula en la
primera letra: `mayo2026vip` llegaba como `Mayo2026vip` y se rechazaba. La de administración
(`Mayo2025`) ya empezaba con mayúscula y por eso sí entraba.

## Qué se hizo
`DRIVER_PASS` del servicio de Render `srv-dbkm91bncjis73entbt0` quedó en **Mayo2026vip**, con
la M mayúscula, igual que la de administración. Verificado contra la app en vivo.

## Lo que falta y es tu tarea
1. Escribirle a Amy y decirle, con sus palabras:
   «Ya quedó lo de los choferes. La contraseña es la misma pero con la M mayúscula:
   Mayo2026vip. Lo que pasaba es que el teclado del celular pone mayúscula sola en la primera
   letra y la app no la reconocía. Ya la probé y entra. Si alguien la copia y pega del grupo,
   que no le deje espacio al final.»
2. Al día siguiente preguntarle si ya entraron todos los choferes.
3. Si vuelve a fallar: el arreglo de fondo ya está escrito en
   `proyectos/amyvip/server.js` (función `igualPass`, compara sin mayúsculas y sin espacios),
   pero **no se pudo desplegar**: el repo que usa Render es
   `github.com/garciayerania63/amy-vip-taxi` y no tenemos acceso de escritura. Para aplicarlo
   hay que pedirle a Amy que nos dé acceso al repo, o mover el servicio a un repo de Carlos.
