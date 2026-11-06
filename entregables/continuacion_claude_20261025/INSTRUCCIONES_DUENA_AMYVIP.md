# Amy VIP Taxi — pago de Render y cambios de la app

App: https://amy-vip-taxi-9ts5.onrender.com
GitHub privado: https://github.com/garciayerania63/amy-vip-taxi
Panel del servicio: https://dashboard.render.com/web/srv-dbf9j2e7bikc73cmik8g
Cuenta usada: garciayerania63 en GitHub; garciayerania63@gmail.com en Render.

## 1. Agregar la tarjeta y activar el servidor de pago

1. Entrar en https://dashboard.render.com con la cuenta que tiene AmyVIP.
2. Abrir el espacio de trabajo «My Workspace» y entrar a «Billing» (Facturación).
3. En «Payment method» o «Payment Methods», agregar la tarjeta y los datos de facturación. Estos datos se ingresan directamente en Render.
4. Abrir el servicio «amy-vip-taxi» desde el enlace del panel indicado arriba.
5. En «Settings», buscar «Instance Type» / «Change Instance Type» y seleccionar «Starter», la instancia de 512 MB de aproximadamente US$7 al mes; si Render muestra nombres de tamaño, seleccionar la equivalente de US$7/mes.
6. Revisar el importe que muestra Render y confirmar. Esperar a que el servicio vuelva a aparecer «Live».
7. Abrir la app para comprobar que sigue funcionando.

Render cobra el uso mensualmente. El precio base actual es US$7/mes, antes de impuestos y posibles cargos adicionales de consumo. Agregar la tarjeta por sí solo no cambia la instancia Free: hay que seleccionar y confirmar la instancia de pago del servicio.

**Guardar historial requiere otro paso técnico.** El servidor pagado evita que se duerma por inactividad, pero el sistema de archivos sigue siendo efímero si no se agrega un disco persistente o una base de datos. Los discos cuestan US$0.25 por GB/mes. AmyVIP todavía necesita adaptar su ruta de datos y migrar los registros antes de usar ese disco. No agregar un disco encima de la carpeta del código: podría impedir el arranque. Este ajuste no se ha cobrado ni se ha contratado automáticamente.

Fuentes oficiales verificadas el 26/10/2026:
- https://render.com/pricing
- https://render.com/docs/render-dashboard
- https://render.com/docs/disks
- https://render.com/docs/faq

## 2. Cómo pedir cambios

Indicar qué quiere cambiar, qué rol lo ve y qué debe pasar. Por ejemplo:
- «En la pantalla del pasajero agrega la colonia X con tarifa de $Y.»
- «Cuando el chofer acepte un viaje, muestra el teléfono del pasajero en un botón grande para llamar.»
- «En administración quiero descargar la facturación de esta semana por chofer.»

El código está en el repositorio privado de GitHub. Puede descargarlo desde «Code → Download ZIP» y dárselo a un desarrollador o a un asistente que pueda editar archivos y ejecutar herramientas. Los accesos API se entregan en un archivo privado separado, nunca dentro del código que se sube al repositorio.

Texto para encargar un cambio:

> Esta es Amy VIP Taxi, una app de taxis de Nogales. Lee PLAN.md y DEPLOYMENT.md antes de modificarla. Quiero este cambio: [describir]. El rol afectado es [pasajero/conductor/admin]. Conserva lo demás, prueba el cambio y guarda el código en el repositorio privado. Después actualiza APP_COMMIT en el servicio de Render a la revisión nueva y publica mediante la API. Comprueba /ping, los tres roles y los accesos. Dime los archivos modificados y la URL funcionando.

## 3. Cómo se publica una modificación en esta instalación

El responsable técnico realiza esto:
1. Modifica y prueba la copia de la app.
2. Hace commit y push a main de garciayerania63/amy-vip-taxi.
3. Toma el identificador del commit que quiere publicar.
4. Actualiza en Render la variable APP_COMMIT al identificador nuevo.
5. Solicita un nuevo despliegue con la API o «Manual Deploy» en el panel.
6. Espera «Live» y comprueba la app en la URL pública.

En la configuración actual, subir archivos a GitHub por sí solo NO publica la app. Render descarga el código privado durante la construcción con un token guardado en sus variables de entorno. Hay que conservar APP_SOURCE_TOKEN, APP_REPOSITORY y las claves VAPID. Si el token de GitHub vence, se actualiza antes de publicar otra versión.

Antes de publicar cambios que reinicien el servicio, conservar un respaldo de los registros: el plan gratuito actual no ofrece persistencia del historial.

## 4. APIs y acceso

API GitHub: https://api.github.com
API Render: https://api.render.com/v1
Repositorio: garciayerania63/amy-vip-taxi
Servicio Render: srv-dbf9j2e7bikc73cmik8g

Las claves están en ACCESOS_PRIVADOS_AMYVIP.txt, entregado por separado. Tener una clave API no equivale a tener la contraseña de inicio de sesión del panel: la dueña entra al panel con el método de acceso de su cuenta.
