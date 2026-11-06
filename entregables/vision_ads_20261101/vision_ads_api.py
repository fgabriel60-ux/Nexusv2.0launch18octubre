"""
Vision Ads API — módulo de campañas de Meta para desplegar en Modal.

Qué hace:
  1. El usuario conecta su Facebook (Inicio de sesión con Facebook para empresas).
  2. Lista sus cuentas publicitarias y páginas.
  3. Toma el video que ya generó tu app en Modal y crea:
     campaña -> conjunto de anuncios -> creativo -> anuncio.
     Todo se crea en PAUSA; el usuario lo revisa y lo activa con /campaigns/{id}/activate.

Objetivos soportados (parámetro "objetivo"):
  - "whatsapp"   -> clic a WhatsApp (costo por conversación)
  - "messenger"  -> clic a Messenger
  - "trafico"    -> tráfico a sitio web
  - "leads"      -> formulario instantáneo (necesitas lead_form_id)
  - "alcance"    -> alcance / reconocimiento

Configuración (una sola vez):
  pip install modal
  modal secret create meta-ads \
      META_APP_ID=1851074386342905 \
      META_APP_SECRET=<la clave secreta de la app> \
      META_LOGIN_CONFIG_ID=<id de configuración de Login for Business> \
      REDIRECT_URI=https://<tu-workspace>--vision-ads-api-web.modal.run/auth/callback \
      FRONTEND_URL=https://<tu-app>/campanas \
      GRAPH_VERSION=v24.0
  modal deploy vision_ads_api.py
"""

import hashlib
import hmac
import os
import secrets
import time
from typing import Literal, Optional
from urllib.parse import urlparse

import modal

app = modal.App("vision-ads-api")
image = modal.Image.debian_slim().pip_install("fastapi[standard]", "httpx")

# Almacenamiento simple para el MVP. En producción, pásalo a tu base de datos.
tokens = modal.Dict.from_name("vision-ads-tokens", create_if_missing=True)
oauth_states = modal.Dict.from_name("vision-ads-oauth-states", create_if_missing=True)


@app.function(image=image, secrets=[modal.Secret.from_name("meta-ads")])
@modal.asgi_app()
def web():
    import httpx
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import RedirectResponse
    from pydantic import BaseModel, Field

    APP_ID = os.environ["META_APP_ID"]
    APP_SECRET = os.environ["META_APP_SECRET"]
    CONFIG_ID = os.environ["META_LOGIN_CONFIG_ID"]
    REDIRECT_URI = os.environ["REDIRECT_URI"]
    FRONTEND_URL = os.environ["FRONTEND_URL"]
    V = os.environ.get("GRAPH_VERSION", "v24.0")
    GRAPH = f"https://graph.facebook.com/{V}"

    api = FastAPI(title="Vision Ads API")
    api.add_middleware(
        CORSMiddleware,
        allow_origins=["{0.scheme}://{0.netloc}".format(urlparse(FRONTEND_URL))],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ---------- utilidades Graph API ----------

    def proof(token: str) -> str:
        return hmac.new(APP_SECRET.encode(), token.encode(), hashlib.sha256).hexdigest()

    def user_token(user_id: str) -> str:
        data = tokens.get(user_id)
        if not data:
            raise HTTPException(401, "El usuario no ha conectado su Facebook.")
        return data["access_token"]

    def graph(method: str, path: str, token: str, **params):
        params.update(access_token=token, appsecret_proof=proof(token))
        with httpx.Client(timeout=60) as c:
            if method == "GET":
                r = c.get(f"{GRAPH}/{path}", params=params)
            else:
                # Meta acepta objetos JSON como strings en form-data
                import json
                form = {k: json.dumps(v) if isinstance(v, (dict, list)) else v for k, v in params.items()}
                r = c.post(f"{GRAPH}/{path}", data=form)
        body = r.json()
        if "error" in body:
            err = body["error"]
            raise HTTPException(400, {
                "mensaje": err.get("error_user_msg") or err.get("message"),
                "code": err.get("code"),
                "subcode": err.get("error_subcode"),
                "paso": path,
            })
        return body

    # ---------- 1. Conexión con Facebook ----------

    @api.get("/auth/login")
    def login(user_id: str):
        """Tu app manda al usuario aquí: /auth/login?user_id=<id del usuario en tu app>"""
        state = secrets.token_urlsafe(24)
        oauth_states[state] = {"user_id": user_id, "ts": time.time()}
        from urllib.parse import urlencode
        url = f"https://www.facebook.com/{V}/dialog/oauth?" + urlencode({
            "client_id": APP_ID, "redirect_uri": REDIRECT_URI,
            "config_id": CONFIG_ID, "response_type": "code", "state": state,
        })
        return RedirectResponse(url)

    @api.get("/auth/callback")
    def callback(code: Optional[str] = None, state: Optional[str] = None, error: Optional[str] = None):
        if error or not code or not state:
            return RedirectResponse(f"{FRONTEND_URL}?fb=cancelado")
        info = oauth_states.pop(state, None)
        if not info or time.time() - info["ts"] > 900:
            return RedirectResponse(f"{FRONTEND_URL}?fb=expirado")

        with httpx.Client(timeout=30) as c:
            short = c.get(f"{GRAPH}/oauth/access_token", params={
                "client_id": APP_ID, "client_secret": APP_SECRET,
                "redirect_uri": REDIRECT_URI, "code": code,
            }).json()
            if "access_token" not in short:
                return RedirectResponse(f"{FRONTEND_URL}?fb=error")
            long = c.get(f"{GRAPH}/oauth/access_token", params={
                "grant_type": "fb_exchange_token", "client_id": APP_ID,
                "client_secret": APP_SECRET, "fb_exchange_token": short["access_token"],
            }).json()

        tokens[info["user_id"]] = {
            "access_token": long.get("access_token", short["access_token"]),
            "expires_at": time.time() + long.get("expires_in", 3600),
        }
        return RedirectResponse(f"{FRONTEND_URL}?fb=conectado")

    @api.get("/me/status")
    def status(user_id: str):
        data = tokens.get(user_id)
        return {"conectado": bool(data and data["expires_at"] > time.time())}

    # ---------- 2. Cuentas y páginas del usuario ----------

    @api.get("/me/adaccounts")
    def ad_accounts(user_id: str):
        t = user_token(user_id)
        r = graph("GET", "me/adaccounts", t,
                  fields="id,name,currency,account_status,timezone_name", limit=100)
        return [a for a in r["data"] if a.get("account_status") == 1]  # 1 = activa

    @api.get("/me/pages")
    def pages(user_id: str):
        t = user_token(user_id)
        r = graph("GET", "me/accounts", t, fields="id,name,picture{url}", limit=100)
        return r["data"]

    # ---------- 3. Crear campaña ----------

    OBJ = {
        "whatsapp":  dict(objective="OUTCOME_ENGAGEMENT", goal="CONVERSATIONS", dest="WHATSAPP"),
        "messenger": dict(objective="OUTCOME_ENGAGEMENT", goal="CONVERSATIONS", dest="MESSENGER"),
        "trafico":   dict(objective="OUTCOME_TRAFFIC",    goal="LINK_CLICKS",   dest="WEBSITE"),
        "leads":     dict(objective="OUTCOME_LEADS",      goal="LEAD_GENERATION", dest="ON_AD"),
        "alcance":   dict(objective="OUTCOME_AWARENESS",  goal="REACH",         dest=None),
    }

    class Ubicacion(BaseModel):
        paises: list[str] = ["MX"]
        # Opcional: ciudades por key de Meta (usa /targeting/ciudades para buscarlas)
        ciudades: list[dict] = []          # [{"key": "1234", "radius": 20, "distance_unit": "kilometer"}]

    class NuevaCampana(BaseModel):
        user_id: str
        ad_account_id: str                 # "act_123..."
        page_id: str
        objetivo: Literal["whatsapp", "messenger", "trafico", "leads", "alcance"]
        nombre: str
        video_url: str                     # URL pública del video que generó Modal
        texto: str                         # texto principal del anuncio
        titulo: str = ""
        presupuesto_diario: float = Field(gt=0, description="En la moneda de la cuenta, p. ej. 100 = $100 MXN")
        dias: int = Field(7, ge=1, le=90)
        edad_min: int = Field(18, ge=18, le=65)
        edad_max: int = Field(65, ge=18, le=65)
        ubicacion: Ubicacion = Ubicacion()
        link: Optional[str] = None         # obligatorio para "trafico"
        lead_form_id: Optional[str] = None # obligatorio para "leads"
        whatsapp_numero: Optional[str] = None  # número conectado a la página, si tiene varios

    def subir_video(t: str, account: str, url: str) -> tuple[str, str]:
        vid = graph("POST", f"{account}/advideos", t, file_url=url)["id"]
        for _ in range(40):                # hasta ~2 min
            st = graph("GET", vid, t, fields="status")["status"]["video_status"]
            if st == "ready":
                break
            if st == "error":
                raise HTTPException(400, "Meta no pudo procesar el video.")
            time.sleep(3)
        else:
            raise HTTPException(504, "El video sigue procesándose; intenta de nuevo en un minuto.")
        thumbs = graph("GET", f"{vid}/thumbnails", t)["data"]
        thumb = next((x["uri"] for x in thumbs if x.get("is_preferred")), thumbs[0]["uri"])
        return vid, thumb

    @api.post("/campaigns")
    def crear(c: NuevaCampana):
        t = user_token(c.user_id)
        o = OBJ[c.objetivo]
        acct = c.ad_account_id if c.ad_account_id.startswith("act_") else f"act_{c.ad_account_id}"

        if c.objetivo == "trafico" and not c.link:
            raise HTTPException(422, "Para tráfico necesitas 'link'.")
        if c.objetivo == "leads" and not c.lead_form_id:
            raise HTTPException(422, "Para leads necesitas 'lead_form_id'.")

        # Campaña
        campaign = graph("POST", f"{acct}/campaigns", t,
            name=c.nombre, objective=o["objective"], status="PAUSED",
            special_ad_categories=[], buying_type="AUCTION",
            is_adset_budget_sharing_enabled=False,
        )["id"]

        # Segmentación
        geo = {"countries": c.ubicacion.paises}
        if c.ubicacion.ciudades:
            geo = {"cities": c.ubicacion.ciudades}
        targeting = {
            "geo_locations": geo,
            "age_min": c.edad_min, "age_max": c.edad_max,
            "targeting_automation": {"advantage_audience": 0},
        }

        promoted = {"page_id": c.page_id}
        if c.objetivo == "whatsapp" and c.whatsapp_numero:
            promoted["whatsapp_phone_number"] = c.whatsapp_numero

        adset_params = dict(
            name=f"{c.nombre} - Conjunto", campaign_id=campaign, status="PAUSED",
            daily_budget=int(round(c.presupuesto_diario * 100)),  # en centavos
            billing_event="IMPRESSIONS", optimization_goal=o["goal"],
            bid_strategy="LOWEST_COST_WITHOUT_CAP", targeting=targeting,
            start_time=int(time.time()) + 600,
            end_time=int(time.time()) + 600 + c.dias * 86400,
        )
        if o["dest"]:
            adset_params["destination_type"] = o["dest"]
        if c.objetivo != "trafico":
            adset_params["promoted_object"] = promoted
        adset = graph("POST", f"{acct}/adsets", t, **adset_params)["id"]

        # Video + creativo (page_id forzado para que salga con la identidad correcta)
        video_id, thumb = subir_video(t, acct, c.video_url)
        cta = {
            "whatsapp":  {"type": "WHATSAPP_MESSAGE", "value": {"app_destination": "WHATSAPP"}},
            "messenger": {"type": "MESSAGE_PAGE",     "value": {"app_destination": "MESSENGER"}},
            "trafico":   {"type": "LEARN_MORE",       "value": {"link": c.link}},
            "leads":     {"type": "SIGN_UP",          "value": {"lead_gen_form_id": c.lead_form_id}},
            "alcance":   {"type": "LEARN_MORE",       "value": {"link": c.link or f"https://facebook.com/{c.page_id}"}},
        }[c.objetivo]
        video_data = {"video_id": video_id, "image_url": thumb, "message": c.texto, "call_to_action": cta}
        if c.titulo:
            video_data["title"] = c.titulo

        creative = graph("POST", f"{acct}/adcreatives", t,
            name=f"{c.nombre} - Creativo",
            object_story_spec={"page_id": c.page_id, "video_data": video_data},
        )["id"]

        ad = graph("POST", f"{acct}/ads", t,
            name=f"{c.nombre} - Anuncio", adset_id=adset,
            creative={"creative_id": creative}, status="PAUSED",
        )["id"]

        return {"campaign_id": campaign, "adset_id": adset, "creative_id": creative,
                "ad_id": ad, "estado": "PAUSADA"}

    class Activar(BaseModel):
        user_id: str

    @api.post("/campaigns/{campaign_id}/activate")
    def activar(campaign_id: str, body: Activar):
        """Activa campaña, conjuntos y anuncios. Llamar solo cuando el usuario confirme."""
        t = user_token(body.user_id)
        for a in graph("GET", f"{campaign_id}/ads", t, fields="id")["data"]:
            graph("POST", a["id"], t, status="ACTIVE")
        for s in graph("GET", f"{campaign_id}/adsets", t, fields="id")["data"]:
            graph("POST", s["id"], t, status="ACTIVE")
        graph("POST", campaign_id, t, status="ACTIVE")
        return {"campaign_id": campaign_id, "estado": "ACTIVA"}

    @api.get("/campaigns/{campaign_id}/insights")
    def resultados(campaign_id: str, user_id: str):
        t = user_token(user_id)
        r = graph("GET", f"{campaign_id}/insights", t, date_preset="maximum",
                  fields="spend,impressions,reach,clicks,actions,cost_per_action_type")
        return r["data"][0] if r["data"] else {}

    @api.get("/targeting/ciudades")
    def buscar_ciudades(user_id: str, q: str):
        t = user_token(user_id)
        r = graph("GET", "search", t, type="adgeolocation", location_types='["city"]',
                  q=q, country_code="MX", limit=10)
        return [{"key": x["key"], "nombre": f'{x["name"]}, {x.get("region", "")}'} for x in r["data"]]

    return api
