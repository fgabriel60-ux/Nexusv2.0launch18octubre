# Respuesta de Claude al encargo de datos para Andromeda Lab

Para Astra. Tu sesión se cortó a la 01:30 con `usage_limit_exceeded` («try again at 3:26 AM»), así que Carlos me
pidió continuar. Hice **solo la extracción y preparación de datos**: no toqué `engine.py`, `server.py` ni reinicié
nada, y no escribí en `local-data/`. Windsor.ai en modo lectura; no se creó ni modificó nada en la cuenta.

## Rutas exactas

Carpeta: `entregables/facebook_ads_para_andromeda_20260916/`

| Archivo | Contenido |
|---|---|
| `facebook_ads_raw.json` | las dos consultas tal cual, con su configuración. Sin tokens |
| `facebook_ads_enriched.json` | 216 filas diarias + creativo unido por `ad_id`, ausencias conservadas como `null` |
| `facebook_ads_normalizado.csv` | 56 filas aptas para tu contrato |
| `creativos.json` | catálogo de los 56 anuncios |
| `VALIDACION.md` | consultas, mapeo, exclusiones, límites y reconciliación |
| `resumen_construccion.json` | conteos y motivos de exclusión |
| `construir_entregables.py` | script reproducible |

## Lo que pediste que comunicara

- **Cobertura del CSV:** 56 filas, **18 anuncios**, **8 campañas**, del **2026-04-14 al 2026-07-17**.
- **Extracción completa:** 216 filas diarias, 56 anuncios, 29 campañas, del 2026-04-14 al 2026-08-11. La cuenta no
  tiene entrega fuera de ese rango, aunque pedí 2026-04-01 a 2026-09-15.
- **Moneda:** MXN, confirmada por `account_currency`. **Zona:** America/Tijuana (UTC−7).
- **Atribución:** `default` del conector = **7d_click + 1d_view**. Etiqueta usada: `default_7d_click_1d_view`.
  Tenías razón: el sufijo `7d` del nombre del campo no la determina, la fija la opción `attribution_window`.
- **Creativo disponible:** **25 de 56 anuncios (44.6 %)** traen texto (`body`). 40 de 56 traen título e
  `image_url`; los 56 traen miniatura y `creative_id`. Los 31 sin texto son casi todos `object_type = SHARE`.
- **Reconciliación de la referencia:** coincide exacto, sin ajustar nada. Gasto 210.65, impresiones 7,786,
  conversaciones 48, por día 1/29/10/8. **Dato nuevo:** fue un solo anuncio, `120250891895420651`, y sus clics de
  enlace reales son **160**, no los 454 clics totales del informe anterior.
- **Validación con tu motor:** `parse_history` devuelve `{"filas_validas": 56, "duplicados_exactos": 0}`, sin
  periodos solapados.

## Decisiones que tomé, por si no coinciden con lo que esperabas

1. **Objetivo mapeado solo cuando concuerda con el evento de optimización.** Hay campañas `MESSAGES` optimizadas a
   `POST_ENGAGEMENT` y `LINK_CLICKS` optimizadas a `CONVERSATIONS`; esas filas quedaron fuera del CSV con su valor
   original conservado en el enriquecido.
2. **`audience` = nombre del conjunto de anuncios**, no su ID, como pediste.
3. **Ceros explícitos solo con entrega:** 31 filas donde Meta omitió la acción pero el anuncio tuvo impresiones.
   Las filas sin impresiones se excluyeron. Ningún dato desconocido se rellenó con cero.
4. **Sin texto del creativo no hay `idea`:** 67 filas de 24 anuncios excluidas en vez de inventar descripciones.

## El problema que tienes que decidir tú

Tu motor exige **3 anuncios comparables por contexto**. Con estos datos:

| Contexto | Anuncios |
|---|---:|
| `leads` · Promoción continua de generación de clientes potenciales | **8** |
| `traffic` · México 35-64 - Tráfico Enlace IMSS | **5** |
| `messages` · cada una de las 4 campañas de mensajes | **1 cada una** |

**El objetivo `messages`, que es el caso de negocio de Carlos, no alcanza el mínimo.** Cada campaña de mensajes
tuvo su propio conjunto con nombre distinto, así que cada una es su propio contexto.

Se podría llegar a 4 anuncios de mensajes agrupando la audiencia de forma más gruesa, por ejemplo tratando todas
las campañas de WhatsApp como un mismo contexto. **No lo hice**: mezclaría públicos que el anunciante definió por
separado y tu propio encargo prohíbe unir mercados sin evidencia. Es decisión tuya y necesita criterio documentado.

## Lo que sigue faltando

1. Texto de 31 anuncios `SHARE`: el conector no devuelve el cuerpo del post original.
2. Descripción visual de las piezas: solo hay URLs, nadie las describió. `idea` lleva texto literal, no escena.
3. `description_asset_text` y `video_asset_video_id`: bloqueados por el error de Meta
   `(#100) Current combination of data breakdown columns (action_type, description_asset, video_asset) is invalid`.
4. Ingresos y ventas: no existen en la plataforma. No se calculó ROAS ni se dieron por ciertas las dos ventas.
5. Supermetrics no sirve: Facebook Ads sin autenticar y trial vencido. Windsor está en plan gratuito.
