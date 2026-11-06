# Memoria del sistema · 3 nov 2026

Todo lo que existe y cómo se toca. Escrito para el Claude que llegue después, cuando
este se acabe. Lo que no está aquí, no pasó: si algo contradice esto, gana lo que
digan los archivos y los logs, no la memoria.

---

## 1. Dónde vive cada cosa

| Qué | Dónde | Cuenta |
|---|---|---|
| Claude + ChatGPT vivos | app `nexus3` (`nexus3.py`) | charlyfavela666 |
| Tablero de revisión | app `tablero-nexus` (`tablero_modal.py`) | charlyfavela666 |
| Atención automática | app `atencion-nexus` (`atencion_modal.py`) | charlyfavela666 |
| Glimmer (calificar) | app `glimmer` (`entregables/glimmer_estrategias_20261029/glimmer_modal.py`) | charlyfavela666 |
| Escenas Qwen/MiniMax | `clientes/_escenas_carlos/escenas_carlos_modal.py` | charlyfavela666 |
| App de Amy VIP Taxi | Render, servicio `amy-vip-taxi-1` | Render de Carlos |
| Tablero de claude.ai | https://claude.ai/artifact/RNy7eDiVEyBaz12fxSKy42 | cuenta de Carlos |

**Todo el gasto va a `charlyfavela666`.** `gasto_modal.py` ya tiene ese perfil por
defecto y el tope en `float("inf")` porque Carlos lo pidió el 3 nov: **no hay vigía
que frene el gasto**, hay que mirar el saldo a mano (`python3 gasto_modal.py saldo`).

### Cuentas de Modal, al 3 nov 2026
- **charlyfavela666**: la que se usa. ~$29 de $30 de crédito.
- **carlosfavelajeje**: AGOTADA y cobrando dinero real ($39.98 consumidos sobre $30;
  $9.85 facturados). Ahí siguen desplegadas `nexus-app`, `arroyos-nogales`, `jarvis`
  y `nexus-chat`, todas en 0 tareas (no cobran mientras nadie entre).
- **fgabriel60**: ~$24 libres. Sin usar.

### Por qué se apagó nexus-claude
Corría 3 contenedores sin parar desde el 31 oct: **$24.80 de los $39.98**. La lección
quedó en el código: toda app web lleva `min_containers=0` y `scaledown_window` corto.
Una A100 ociosa cuesta igual que trabajando (~$4/hora).

---

## 2. El puente (esto causó un fallo real)

El codespace y el sandbox de Modal son **dos máquinas distintas**. Lo que se escribe en
`buzon/` aquí NO llega solo al sandbox: él lee el volumen `nexus-workspace`. Entre el
1 y el 3 de nov, los encargos de Mariano se quedaron aquí y nexus2 nunca los vio.

```
./herramientas/puente_modal.sh enviar    # codespace -> Modal (encargos)
./herramientas/puente_modal.sh traer     # Modal -> codespace (reportes)
./herramientas/puente_modal.sh ver       # qué hay de cada lado
```

**Después de escribir cualquier encargo en `buzon/para_nexus2/`, correr `enviar`.**

---

## 3. El tablero de revisión (lo más usado por Carlos)

https://charlyfavela666--tablero-nexus-web.us-east.modal.run/?k=CLAVE

- La clave está en el secreto de Modal `tablero-clave` y, de respaldo, en
  `entregables/tablero/.clave` del volumen. Sin clave da 401.
- Muestra **las 80 versiones calificadas de los 27 clientes**, cada una con su video.
- Separa **lo que nos toca a nosotros** de **lo que tiene que mandar el cliente**.
- Al darle "Enviar órdenes a Claude", escribe un `.md` en `buzon/para_nexus2/` del
  volumen con el nombre EXACTO de la versión aprobada.

**La regla que nació de un error de Carlos conmigo:** cuando él decía "haz lo de
Glimmer para tal cliente", yo trabajaba el video equivocado porque solo veía la última
versión. Por eso el tablero muestra todas y él elige. **Si llega una orden del tablero,
se trabaja ESA versión y ninguna otra.**

Para regenerarlo: `python3 armar_tablero.py` y subir `entregables/tablero` al volumen.

---

## 4. Atención automática a prospectos

https://charlyfavela666--atencion-nexus-web.us-east.modal.run

- `GET /estado` dice a quién atiende solo. `POST /probar` lo prueba sin Meta.
- `POST /meta` es el webhook que Meta llama cuando alguien escribe desde un anuncio.
- **Solo contesta a los chats encendidos** en `entregables/atencion/encendidos.json`
  con `activo: true`. Al 3 nov: Guillermo y Jesús cargados pero **apagados**.
- Da bienvenida y 4 preguntas de calificación. **Nunca promete precio.** Deja aviso
  en `buzon/para_nexus/` para que una persona cierre.
- Falta en el secreto `nexus-env`: `META_VERIFY_TOKEN` para que Meta valide el webhook.

---

## 5. Reglas de Carlos que se rompieron y no se vuelven a romper

1. **No se le escribe a un cliente** si Carlos no lo pide en ESE mensaje. Pasó dos
   veces con Jesús el 3 nov y Carlos tuvo que frenarlo.
2. **No se inventan datos del cliente**: precios, fotos, permisos. Si falta, se pide
   y se dice que falta. Glimmer marca esto como "oferta 1/10" y hunde la calificación.
3. **Cada video lleva su calificación de Glimmer**, separando la actual de la
   proyectada. Nunca se inventa una calificación.
4. **Nada se sube a campaña por debajo de 8**: con menos, Facebook cobra por vistas
   y no llegan mensajes.
5. **Versionar, no sobrescribir** (v9 → v9b). No borrar archivos de clientes.
6. **Verificar antes de decir que está hecho**: oír con Whisper, ver cuadros del
   video, leer el log.

---

## 6. Estado de los clientes al 3 nov

Lo más fácil de avanzar primero (sin depender de que el cliente mande algo):
**Guillermo, Rubén, Iván, Fernando, Lisbeth, Tatuador, Israel.**

- **Guillermo (Vicens, herrería Puebla)**: campaña ACTIVA en Meta, cuenta
  `1603722124889431`, campaña `23860083587680790`, conjunto `23860083588040790`
  (Puebla +40km). Corren el v8 con clics (6/10) y el v7 (8.3/10). El **v9b con
  tarjetas de precio** (`23860195593970790`, Glimmer 7/10 → 8.5) está EN PAUSA
  esperando que Carlos lo active. Precios reales que dio: zaguán $2,300/m²,
  celosía $1,400/m², puerta desde $3,200. **De portón no dio precio: no inventarlo.**
  Falta para 8.5: la voz dice "Bizens" en vez de "Vicens" (regrabar) y micro-zoom
  en el gancho.
  **Falta fondear la cuenta de Meta: $500 MXN por SPEI.**
- **Jesús (RIMO, bolsas)**: B3 v8 en 8/10. Carlos frenó dos envíos no autorizados.
- **Amy VIP Taxi**: app en Render plan Starter, disco `/data` de 1 GB creado el
  3 nov 06:24. Contraseñas: admin `amyvip2026`, chofer `chofervip2026`.
  **No tenemos su WhatsApp**: no está en los 516 chats ni en el proyecto.
- **Mariano**: encargo de Bugambilia v2 en el buzón, tope $3 USD.

---

## 7. Lo que quedó pendiente

- Activar el anuncio v9b de Guillermo (a Claude le negaron el permiso; lo hace Carlos).
- Fondear Meta con $500 MXN.
- Conseguir el WhatsApp de Amy.
- Borrar en el Administrador de Meta lo marcado "ZZ NO USAR".
- Medir el ahorro real del modelo precargado de Glimmer (pendiente para el 4 nov).
- Prueba limpia del paralelo: mismo spec en serie y en paralelo (~$1).
