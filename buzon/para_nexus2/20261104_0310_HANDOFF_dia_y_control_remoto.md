# HANDOFF para el Claude de Modal · 4 nov 2026, 03:10 UTC

Carlos pidió dos cosas en este encargo: **activar el control remoto** para manejarte desde el
celular, y que te quedes con **todo lo que pidió hoy**. Abajo está completo, con lo hecho y lo
que falta, para que no se repita trabajo.

## 1. CONTROL REMOTO (prioridad)
La página de control (`https://charlyfavela666--nexus3-control.us-east.modal.run`) responde,
pide `?t=<CONTROL_CLAVE>` del secreto `nexus-env`. Lo que está caído es el **remote control de
Claude Code** dentro del sandbox: el 2 nov salió el aviso «el Control Remoto está desconectado».
- Revisa en tmux que siga el bucle `claude remote-control --name nexus` (nexus_666.py línea 34).
- Si no corre: verifica que exista `/vol/claude-config/.credentials.json` y relánzalo.
- Cuando quede, mándale a Carlos por WhatsApp el enlace de la página con su clave, y dile que
  ya puede darte órdenes desde el celular.

## 2. LO QUE CARLOS PIDIÓ HOY

### Hecho (no lo repitas)
- **Tablero** (`…/tablero-nexus`): cada cliente muestra arriba su video mejor calificado con el
  plan para llegar a 8, y las demás versiones en «Ver las otras N versiones». Panel nuevo
  **«Lo que prometiste hoy»** (14 promesas sacadas del barrido de sus 25 chats, 7 cumplidas) y
  panel **«Te escribieron hoy»**. Señales por versión: ⭐ la más trabajada, 📤 la que sí se mandó.
- **Secciones de cliente** (`/c/<slug>?k=<clave>`): Mariano (`nHubcLiLWdpd`) y Rafael
  (`QIBvtNbk3ETS`). Video + calificación por rubro en lenguaje de cliente + arreglos con
  casillas + caja de pedidos + botón «Apruebo, háganlos todos».
- **Endpoint para ti**: `POST /c/<slug>/actualizar` con la clave maestra publica la versión
  nueva en la app del cliente (video, calificación y sugerencias nuevas) y reinicia el reloj.
- **Regla de los 10 minutos**: app `auto-aplicar-cambios` (cron 5 min). Si el cliente no
  contesta en 10 min, deja el encargo para aplicar todo, recalificar y reportar.
- **Vigía de clientes**: app `vigia-clientes` (cron 10 min). Detecta mensajes nuevos de los 25
  chats (Amy incluida), deja encargo aquí y avisa a Carlos. **No le escribe al cliente**: el
  acuse con tiempo de espera lo mandas tú al tomar el encargo.
- **Lista de prioridades**: app `prioridades-carlos` (cron 10 min) le manda a Carlos sus 7
  prioridades ordenadas. Carlos tiene TDAH: la lista corta es a propósito.
- **Glimmer al doble**: `glimmer_modal.py` ahora añade « to=user» al prompt y se salta el
  razonamiento interno. 3 videos en 8.2 min en vez de 4.9 min por video, y ya no se corta.
- **Calificaciones de hoy**: Adrián 6→8 (y su v2 ya aplicada: Oferta 4→7, sigue en 6 por el
  gancho), Mariano v8 cuerda 6.5→8.5, Rafael A y B 5→7.5.
- **Amy**: contraseñas cambiadas (admin `Mayo2025`, chofer `Mayo2026vip`, con mayúscula porque
  el teclado del celular capitaliza y por eso fallaba). Ya se le avisó.
- **Alberto**: se le mandaron los 5 guiones para que grabe la doctora, con instrucciones.
- **Giovanni**: se le mandó su calificación 6→8, las 3 cosas que faltan y su guion de 30 s.
- **Rafael**: se le mandó su calificación y plan; hoy dio su oferta por nota de voz:
  **el BYD Dolphin trae bono de $65,000 este mes**.

### Falta
1. **Rafael v6 con su oferta**: meter el bono de $65,000 del Dolphin en pantalla y en voz
   clonada (ya está grabada en `clientes/Rafael_BYD/voz/R7.wav`), quitar «al mejor precio con
   los mejores bonos» del gancho (va de 5.20s a 8.00s del clip
   `whatsapp/del_cliente/20261103_122142_video_0001A1F1.mp4`), poner su credencial en pantalla
   y recalificar. Base: `clientes/Rafael_BYD/v5_20261104/Rafael_BYD_v5B_sus_tomas.mp4`.
2. **Adrián**: faltan el gancho (abrir con primer plano de un tatuaje terminado, necesita
   MiniMax H3 o material suyo), el filtro «¿Quieres diseño único? Escríbeme CITAS» en
   8.9-10.1s y recortar el relleno del inicio de 4 s a 2 s.
3. **Campaña de Jesús (RIMO)**: Meta rechaza por permisos en la cuenta 1827272525138717.
   Falta que Carlos reconecte Windsor o que Jesús lo agregue como anunciante. Todo lo demás
   está listo (objetivo mensajes, $100 MXN/día, todo México, video que calificó 8).
4. **Amy**: el arreglo de fondo (aceptar mayúsculas y espacios en la contraseña) está escrito
   en `proyectos/amyvip/server.js` (`igualPass`) pero no se pudo desplegar: Render usa el repo
   `github.com/garciayerania63/amy-vip-taxi` y no tenemos acceso de escritura.
5. **Atender a Amy en el barrido**: revisar si pidió algo más y hacerlo, confirmándole tiempo
   de espera (Carlos lo pidió expresamente).

## 3. REGLAS NUEVAS DE CARLOS (de hoy)
- Cada calificación va con **cómo subir cada rubro** (escena, gancho, cambio con IA), no solo
  la nota. Ya está en el PROMPT de `entregables/glimmer_evaluador/evaluar.py`.
- Si un cliente no aprueba en **10 minutos**, los cambios se hacen solos, se recalifica y se
  reporta la calificación nueva; si no llega a 8, se dice qué falta.
- Todo cambio que hagas debe **aparecer en la app del cliente** con el video nuevo, la
  calificación nueva y las sugerencias nuevas (usa el endpoint de arriba).
- Nunca le escribas a un cliente por tu cuenta salvo el acuse con tiempo de espera cuando
  tomas un encargo del vigía.
