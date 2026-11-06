# Encargo (Carlos, 5 nov 2026): aplicar lo que pidió Amy en la app y revisar los comentarios CADA MAÑANA

Amy (VIP Taxi, Nogales) deja sus peticiones **dentro de la app**, en la sección de comentarios, y da por
hecho que el sistema las aplica. Dijo por WhatsApp: «le dejé todo lo que le falta a la app en los
comentarios y nada, creí que el sistema lo haría». Carlos ya le confirmó que de ahora en adelante así
será. **Esto es una rutina permanente tuya.**

## La rutina de cada mañana (obligatoria)

1. Lee los comentarios: `curl -s https://amy-vip-taxi-1.onrender.com/api/comments` (es público, no pide clave).
2. Toma los que no estén aplicados todavía y conviértelos en cambios reales en `proyectos/amyvip/`.
3. Despliega a Render y **compruébalo en la app en vivo**, no solo en el código.
4. Deja un comentario de respuesta en la misma app (`POST /api/comments` con
   `{"text":"...","author":"Soporte","role":"admin"}`) diciendo qué quedó listo, para que ella lo vea ahí mismo.
5. Reporta a Carlos: qué aplicaste, qué falta y qué necesitas de él. A Amy no le escribas por WhatsApp
   salvo que Carlos lo pida en ese mensaje.

## Lo que está pendiente HOY (sus 6 peticiones, del 4 nov)

1. **Timbre más alto** cuando entra un servicio. «Me podrías poner el timbre más alto, al momento de que
   caen los servicios.»
2. **Estados del chofer**: poder ponerse *activo*, *ocupado* o *en descanso*. «También falta ponerle al
   chofer para activarse, ocupado, o en descanso.»
3. **Botón de emergencia** para pasajero y chofer. Ella lo marcó como «súper importante».
4. **Compartir el viaje** con familia o amigos, desde el lado del pasajero.
5. **Décimo viaje gratis**: contador por cliente que se descuente automático conforme pide servicios.
   «Falta poner el décimo viaje gratis para el cliente y que se vaya descontando en automático.»
6. **Que la app siga en segundo plano** y no desconecte al chofer a los minutos: la desconexión debe ser
   manual, por eso importa el estado (activo / ocupado / en descanso).

Orden sugerido por impacto: 2 y 6 van juntos (es el mismo problema de disponibilidad del chofer), luego
3 (seguridad), luego 1 (es rápido), después 5 y 4.

## Reglas

- No borres datos de viajes ni comentarios; la app ya tiene disco en Render con historial.
- Versiona y prueba antes de desplegar: es una app en uso, con choferes trabajando.
- Si algo no se puede hacer (por ejemplo, el botón de emergencia necesita definir a quién llama),
  escríbelo en el comentario de respuesta y pregúntale a Carlos qué quiere.
