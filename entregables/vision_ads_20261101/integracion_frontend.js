// Integración de Vision Ads API en tu app (frontend).
// Cambia API por la URL que te da `modal deploy`.
const API = "https://<tu-workspace>--vision-ads-api-web.modal.run";

// El id del usuario en TU app (el mismo que usas para sus videos de muestra).
const userId = window.usuarioActual?.id;

// 1) Botón "Conectar Facebook"
function conectarFacebook() {
  window.location.href = `${API}/auth/login?user_id=${encodeURIComponent(userId)}`;
}

// Al volver, tu página recibe ?fb=conectado | cancelado | expirado | error
async function estaConectado() {
  const r = await fetch(`${API}/me/status?user_id=${encodeURIComponent(userId)}`);
  return (await r.json()).conectado;
}

// 2) Llenar los selectores de cuenta publicitaria y página
async function cargarCuentasYPaginas() {
  const q = `user_id=${encodeURIComponent(userId)}`;
  const [cuentas, paginas] = await Promise.all([
    fetch(`${API}/me/adaccounts?${q}`).then(r => r.json()),
    fetch(`${API}/me/pages?${q}`).then(r => r.json()),
  ]);
  return { cuentas, paginas };
}

// 3) Crear la campaña con el video que ya generó Modal (se crea en PAUSA)
async function crearCampana({ cuentaId, paginaId, objetivo, videoUrl, texto, presupuesto, dias, link, leadFormId }) {
  const r = await fetch(`${API}/campaigns`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_id: userId,
      ad_account_id: cuentaId,
      page_id: paginaId,
      objetivo,                 // "whatsapp" | "messenger" | "trafico" | "leads" | "alcance"
      nombre: `Campaña ${new Date().toLocaleDateString("es-MX")}`,
      video_url: videoUrl,      // URL pública del video de Modal
      texto,
      presupuesto_diario: presupuesto, // p. ej. 100 = $100 MXN al día
      dias,
      link,                     // solo para "trafico"
      lead_form_id: leadFormId, // solo para "leads"
    }),
  });
  const data = await r.json();
  if (!r.ok) throw new Error(data.detail?.mensaje || data.detail || "Error al crear la campaña");
  return data; // { campaign_id, adset_id, creative_id, ad_id, estado: "PAUSADA" }
}

// 4) Cuando el usuario confirme presupuesto y vista previa: activar (empieza a gastar)
async function activarCampana(campaignId) {
  const r = await fetch(`${API}/campaigns/${campaignId}/activate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId }),
  });
  return r.json();
}

// 5) Resultados
async function verResultados(campaignId) {
  const r = await fetch(`${API}/campaigns/${campaignId}/insights?user_id=${encodeURIComponent(userId)}`);
  return r.json(); // spend, impressions, reach, clicks, actions...
}
