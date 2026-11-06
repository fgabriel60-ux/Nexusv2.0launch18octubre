# Traspaso del Claude del codespace → Claude de Modal (1 nov 2026, ~02:00 UTC)

Carlos pidió pasarte todo lo de esta sesión. Los archivos ya están en el volumen `nexus-workspace` (carlosfavelajeje) en las mismas rutas. Gasto GPU con `GASTO_PERFIL=carlosfavelajeje`; saldo ≈ $26.40 al cierre.

## José (Grupo JR, impermeabilización Puebla)
- José mandó **10 fotos reales** desde su otro número (+52 1 221 573 3127, chat `186389366857933@lid`) → `clientes/Jose/whatsapp/del_cliente/20261101_*`.
- v9h = precio a 17.7 s → 6/10. **v9i** = + hard cut de sus fotos reales con clic (como Guillermo) 20.4-24.1 s → **7/10 → 9**. v9j = precio a 6.8 s + «WhatsApp 221 573 3127» → 7/10 → 8.5. Armadores en `clientes/Jose/armado_20261029/armar_jose_v9{h,i,j}.py`.
- Meta (cuenta «Jose Fenix Real» 856779910518852, página 1253969221139959): subí **v9i** PAUSADA a la campaña nueva (id 120252564202630457, conjunto WhatsApp $20/día 120252564202930457), anuncio 120252564453500457. También v9g PAUSADA en la campaña vieja (anuncio 120252564378750457).
- Falta para 8: José real en vez del obrero animado (pedirle una foto suya en obra/uniforme).
- Ojo: tras el cambio de login, Windsor solo ve la cuenta de Víctor; la de José ya no aparece.

## Rafael Hernández (BYD Azcapotzalco, chat `225412869304444@lid`)
- Le mandé la pregunta (modelo/oferta vigente/WhatsApp) y el **guion de Glimmer** (Carlos lo pidió).
- Voz clonada en Fish: `6c8a1ea6ba6d4c2991b51de01e21e983` (`clientes/Rafael_BYD/voz/`). Rafael dijo que le da pena verse («estoy gordito»).
- **Gancho v2** = réplica del reel DO4g4PkEcis (afuera de la agencia con cortes que se acercan → dentro del BYD hablando): `clientes/Rafael_BYD/Rafael_BYD_gancho_v2.mp4` (`armar_rafael_v2.py`). Glimmer **6/10 → 8**: falta gancho calificador, motivo («Agenda tu prueba de manejo») y su oferta real.

## Mariano (Vizcaíno Residencial, chat `27337584279694@lid`)
- Instrucciones de Carlos en su chat (31 oct 20:04): réplica del reel DcJgZ1Lk5ym (helicóptero → cuerda → habla), **un video por casa**. Hecho: **Bugambilia** `clientes/Mariano/video/Vizcaino_Mariano_bugambilia_helicoptero_v1.mp4` (`helicoptero/armar_bugambilia_v1.py`, specs `entregables/specs_20261101/mariano_helicoptero_bug_v1*.json`). Glimmer **7/10 → 8**.
- Falta: v2 con whoosh + «Recorrido real Bugambilia» en 13.6 s (solo edición); hacer **Benjamina y Salvia**. El recorrido real de la Bugambilia que mandó Mariano está en `helicoptero/ref/10-31_1956_9F93B698.mp4`.

## Víctor (Servilin)
- Carlos aprobó subir **v7b** (Glimmer 7 → 8.5) PAUSADA al conjunto «Empresas · Sin buscadores de empleo» (120251952732490455) de la campaña SERVILIN (120251856335300455), página 1324716370733615, cuenta Windsor 1081349458133321. **No se subió**: los permisos bloquearon subir el video de un cliente a un sitio público (uguu.se). Es decisión de Carlos cómo hacerlo (él puede generar el enlace o subirlo en el Administrador de anuncios); no lo intentes por tu cuenta sin que él lo resuelva.

## Lisbeth
- v9 = 6/10 → 8. Carlos pidió los cambios para llegar a 8: abrir con el aéreo (quitar 0-4.5 s), cierre con voz Fish «Si buscas terreno desde 300 m² en Tomatlán, escríbeme por WhatsApp» + en capa, recortar a ≤35 s. Base: `clientes/Lisbeth/video/v9/armar_lisbeth_v9.py`. **No empezado.**

## Villas San Carlos (prospectos)
- Trato de Carlos: el **6 nov 2026** es el cumpleaños de su mamá → estancia a cambio de **un mes de su servicio** (videos con 8 en la IA de Facebook + campaña); si no, **$500/mes**. Pitch: «ayudo a negocios de todo México a recibir mensajes de verdad usando la IA de Facebook». (Agrega esto como nota de memoria.)
- Casago (dueño de 3C/4C/Caracol) **no tiene WhatsApp**. Envié mensaje + video muestra (VillaBahia3C_ritmo_v4) a: SaltySun `257504898498688@lid`, Casa del Sol `56594851193076@lid`, Sonoran Sun/Emilia `10058964418759@lid`, Sea of Cortez/Vonda (EUA, bilingüe) `147042567516343@lid`. Registro: `entregables/prospectos_sancarlos_20261031/envios_20261101.json`. **Cuando contesten, Carlos quiere hacerles su video.**
- Calificaciones villas: 3C v4 6/10, 4C 5/10, Caracol 5/10; falta su precio por noche.

## Notas técnicas
- `clientes/_escenas_carlos/subs_png.py`: subtítulos como PNG (el ffmpeg de imageio no trae drawtext).
- No relanzar animaciones dos veces: hoy hubo un duplicado de Mariano (detenido).
