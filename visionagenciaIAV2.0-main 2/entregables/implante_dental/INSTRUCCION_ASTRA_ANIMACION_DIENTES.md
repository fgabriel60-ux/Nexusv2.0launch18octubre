Astra, Carlos te pide: **«que aplique la animación de los dientes de forma genial siguiendo el estilo de las imágenes»**.
Esta vez SÍ estás autorizada a trabajar en el Blender vivo de la Mac por el puente HTTP, con las reglas de abajo.

## Referencias visuales aprobadas (míralas antes de tocar nada)

`entregables/implante_dental/`
- `gpt_estilo_hoja/GPT2_CUADRO_150_CLOSEUP.png` — close-up de labios y hueco del diente.
- `gpt_transicion/GPT2_TRANSICION_CUADRO_749_v3.png` — pantalla dividida: labios a la izquierda, línea cian, corte anatómico.
- `gpt_transicion/GPT2_SOLO_DIENTES_ENCIAS_v4.png` — **destino principal**: solo dientes y encías, sin cara ni línea. Carlos:
  «la línea se desplazará y desaparecerá, la explicación será sobre solo los dientes y encías».
- `kling_transicion/CLIP1…, CLIP2…, CLIP3…` — referencia de movimiento de esas transiciones.
- Hoja de Alberto: `…/clientes/Vision Agencia/veneers_dental/hoja_proceso_implante/hoja_proceso_implante.png`.

## Estilo que debe cumplir

- Exactamente **4 dientes superiores** en el corte: 2 a cada lado del hueco, juntos, cada uno con su raíz visible en el hueso.
  Carlos se quejó de «dientes de más» y de dientes «tan abiertos».
- Implante en el hueco con la **punta hacia arriba** dentro del maxilar; en integración, tapón de cicatrización en la encía;
  después pilar y corona.
- Hueso marfil poroso con brillo cálido en el borde, encía rosa húmeda con borde luminoso, fondo oscuro turquesa, luz cálida + contraluz turquesa.
- La cara solo existe al inicio (rostro → close-up). La línea cian cruza, se desplaza a la orilla y **desaparece**; la cara se
  apaga y el corte queda centrado. Desde ahí, toda la explicación es sobre dientes y encías.

## Tiempos (escena `CHICA_IMPLANTE_ESTILO_APROBADO`, 30 fps, 1050 cuadros)

Marcadores y voz Fish ya colocada (tira `VOZ_FISH_IMPLANTE`, canal 1; frases en `voz_fish/tiempos.json`):
ROSTRO 1 · CLOSEUP 150 («Este es el espacio») · ANESTESIA 200 · CORTE 360 («Ahora, veamos por dentro») · PREPARACION 420 ·
IMPLANTE 620 · INTEGRACION 740 · CORONA 865 · SONRISA 1000. La animación debe coincidir con esas frases.

## Estado actual de la escena (lo que hice yo)

- `estilo_hoja.py` v4 aplicado en la sesión viva (materiales, luces, mundo, dientes ensanchados, `AP_Boca_interior`).
- Voz empaquetada en el secuenciador. Carlos ya guardó `CHICA_IMPLANTE_ESTILO_APROBADO.blend` (incluye la voz); comprobado a las 05:0x UTC, cuadro 560.
- Modelo 3D Hunyuan (`modelo_3d_hoja/HOJA_PASO5_hunyuan_LIGERO.glb` + `integrar_modelo_hoja.py`) solo probado local; puedes
  usarlo o descartarlo. Si lo usas, cuida escala, posición del implante y continuidad al entrar/salir.
- Render Eevee en blanco sin resolver (tu diagnóstico: posible SSR/sombreado/entorno gráfico).

## Reglas (AGENTS.md y lo que ya costó caro)

1. **Primero** guarda una copia de la sesión actual con `bpy.ops.wm.save_as_mainfile(filepath=..., copy=True)` en
   `~/Desktop/IMPLANTE_DENTAL/` con nombre nuevo (conserva la voz). No sobrescribas archivos existentes.
2. Captura estado (escena activa, cuadro, visibilidades, shading) y restáuralo en `finally`. Todo dentro de try/except/finally.
3. Prueba aislada antes de la corrida completa. No dupliques objetos al re-ejecutar (controla nombres/sufijos `.001`).
4. **Viewport en SOLID. No actives MATERIAL/RENDERED ni lances renders Eevee largos** (bloquearon el puente >10 min).
   Para verificar, usa capturas OpenGL del viewport o renders Cycles locales en este Codespace (Blender 4.0.2).
5. No modifiques la escena original `IMPLANTE_DENTAL_CINEMA`.
6. Al terminar guarda la versión animada como `CHICA_IMPLANTE_ANIMACION_DIENTES.blend` (copia), deja el archivo abierto
   en esa escena, cuadro 620, y documenta en `entregables/implante_dental/ESTADO_ANIMACION_DIENTES.md` qué cambiaste,
   qué verificaste (con capturas en esa carpeta) y qué falta.

Contesta a Carlos en español con lo que hiciste, las capturas de verificación y cualquier limitación real.

## Añadido de Carlos (después de lanzar la tarea)

«Modelos 3D bellos, movimientos de cámara». Se envía como seguimiento en `SEGUIMIENTO_ASTRA_CAMARA_MODELOS.md`.
