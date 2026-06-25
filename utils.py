"""
utils.py — Utilidades compartidas para PRODE Última Milla Manager
Importar en Home.py y en todas las páginas.
"""
import streamlit as st
import psycopg2
import psycopg2.extras
import hashlib
import time

# ─────────────────────────────────────────────
# PALETA Y CSS GLOBAL
# ─────────────────────────────────────────────
GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --blue:      #1B3A6B;
    --blue-mid:  #254d8f;
    --orange:    #E8500A;
    --orange-lt: rgba(232,80,10,0.10);
    --bg:        #F0F2F6;
    --card:      #FFFFFF;
    --border:    #DDE3EE;
    --text:      #1C2B3A;
    --soft:      #5A6D82;
    --green:     #1A8C5B;
    --red:       #C0392B;
    --yellow:    #D4890A;
}

*, *::before, *::after { box-sizing: border-box; }
html, body, .stApp { font-family: 'Inter', sans-serif !important; }
.stApp { background: var(--bg) !important; }

/* ── Ocultar nav nativo de Streamlit ── */
[data-testid="stSidebarNav"] { display: none !important; }
header[data-testid="stHeader"] { background: transparent !important; }
#MainMenu, footer { visibility: hidden !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--blue) !important;
    min-width: 220px !important;
    max-width: 220px !important;
}
[data-testid="stSidebar"] * { color: white !important; }
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: none !important;
    color: white !important;
    text-align: left !important;
    width: 100% !important;
    padding: 0.55rem 0.8rem !important;
    border-radius: 8px !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    transition: background 0.15s !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.12) !important;
}
.nav-active > button {
    background: var(--orange) !important;
    font-weight: 700 !important;
}
.nav-section {
    font-size: 0.68rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: rgba(255,255,255,0.45) !important;
    padding: 1rem 0.8rem 0.3rem !important;
    display: block !important;
}
.logout-btn > button {
    background: rgba(232,80,10,0.25) !important;
    color: white !important;
    width: 100% !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    margin-top: 0.5rem !important;
}

/* ── Tarjetas ── */
.card {
    background: var(--card);
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    box-shadow: 0 2px 10px rgba(27,58,107,0.07);
    margin-bottom: 1rem;
}
.card-orange { border-left: 4px solid var(--orange); }
.card-blue   { border-left: 4px solid var(--blue); }
.card-green  { border-left: 4px solid var(--green); }
.card-yellow { border-left: 4px solid var(--yellow); }

/* ── Métrica ── */
.metric-label {
    font-size: 0.72rem;
    color: var(--soft);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 0.2rem;
}
.metric-value {
    font-size: 2.1rem;
    font-weight: 800;
    color: var(--blue);
    line-height: 1;
}

/* ── Cabecera de página ── */
.page-header {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    padding-bottom: 0.9rem;
    margin-bottom: 1.4rem;
    border-bottom: 2px solid var(--border);
}
.page-header-icon { font-size: 1.7rem; }
.page-header h1 {
    font-size: 1.5rem !important;
    font-weight: 800 !important;
    color: var(--blue) !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* ── Badge de estado ── */
.badge {
    display: inline-block;
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
.badge-green  { background: rgba(26,140,91,0.12);  color: var(--green); }
.badge-red    { background: rgba(192,57,43,0.12);   color: var(--red); }
.badge-orange { background: var(--orange-lt);        color: var(--orange); }
.badge-blue   { background: rgba(27,58,107,0.10);   color: var(--blue); }
.badge-yellow { background: rgba(212,137,10,0.12);  color: var(--yellow); }

/* ── Fila clickable en listas ── */
.row-card {
    background: var(--card);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.5rem;
    border: 1.5px solid var(--border);
    cursor: pointer;
    transition: border-color 0.15s, box-shadow 0.15s;
    display: flex;
    align-items: center;
    gap: 1rem;
}
.row-card:hover {
    border-color: var(--orange);
    box-shadow: 0 3px 14px rgba(232,80,10,0.10);
}
.row-avatar {
    width: 42px; height: 42px;
    border-radius: 50%;
    background: var(--orange-lt);
    color: var(--orange);
    font-weight: 800;
    font-size: 1.1rem;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}
.row-name { font-weight: 700; color: var(--text); font-size: 0.95rem; }
.row-sub  { font-size: 0.78rem; color: var(--soft); margin-top: 1px; }

/* ── Botón volver ── */
.back-btn > button {
    background: transparent !important;
    color: var(--blue) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 8px !important;
    font-size: 0.85rem !important;
    padding: 0.4rem 0.9rem !important;
    font-weight: 600 !important;
}
.back-btn > button:hover {
    border-color: var(--blue) !important;
    background: rgba(27,58,107,0.05) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    border-bottom: 2px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px 8px 0 0 !important;
    padding: 0.5rem 1.2rem !important;
    font-weight: 600 !important;
    color: var(--soft) !important;
}
.stTabs [aria-selected="true"] {
    background: var(--orange-lt) !important;
    color: var(--orange) !important;
    border-bottom: 2px solid var(--orange) !important;
}

/* ── Login card ── */
.login-card {
    background: white;
    border-radius: 16px;
    padding: 2.5rem 2rem 2rem;
    box-shadow: 0 4px 28px rgba(27,58,107,0.12);
    border-top: 5px solid var(--orange);
    max-width: 400px;
    margin: 4rem auto 0;
}
.login-card .stButton > button {
    background: var(--orange) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    width: 100% !important;
    padding: 0.6rem !important;
}
</style>
"""

# ─────────────────────────────────────────────
# BASE DE DATOS
# ─────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_conn():
    return psycopg2.connect(st.secrets["DATABASE_URL"], connect_timeout=8)

def query(sql: str, params=None):
    """Ejecuta SELECT y devuelve lista de dicts."""
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            return [dict(r) for r in cur.fetchall()]
    except Exception as e:
        st.error(f"ERROR SQL: {e}")
        get_conn.clear()
        return []
def execute(sql: str, params=None) -> bool:
    """Ejecuta INSERT/UPDATE/DELETE. Devuelve True si OK."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        st.error(f"Error de BD: {e}")
        return False

def db_status() -> bool:
    try:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
        return True
    except Exception:
        return False

# ─────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────
def hash_pwd(p: str) -> str:
    return hashlib.sha256(p.encode()).hexdigest()

def check_login(username: str, password: str):
    import pandas as pd
    from pathlib import Path
    default = pd.DataFrame([{"username": "admin", "password": "admin", "rol": "admin"}])
    path = Path("data/usuarios.csv")
    df = default
    if path.exists():
        for enc in ("utf-8-sig", "utf-8", "latin1"):
            try:
                df = pd.read_csv(path, dtype=str, encoding=enc).fillna("")
                break
            except Exception:
                continue
    time.sleep(0.25)
    match = df[df["username"].str.strip() == username.strip()]
    if not match.empty:
        stored = match.iloc[0]["password"].strip()
        plain_ok = stored == password
        hash_ok  = (len(stored) == 64 and hash_pwd(password) == stored)
        if plain_ok or hash_ok:
            return True, match.iloc[0]["rol"]
    return False, None

def require_login():
    """Llama en cada página para redirigir si no hay sesión."""
    if not st.session_state.get("login"):
        st.warning("Debes iniciar sesión primero.")
        st.stop()

# ─────────────────────────────────────────────
# SIDEBAR COMPARTIDO
# ─────────────────────────────────────────────
NAV_PAGES = {
    "📊 Dashboard":   "Dashboard",
    "👥 Empleados":   "Empleados",
    "🚛 Vehículos":   "Vehiculos",
    "📋 Servicios":   "Servicios",
    "📅 Ausencias":   "Ausencias",
}

def render_sidebar():
    with st.sidebar:
        st.markdown("## 🚚 PRODE")
        st.markdown("*Última Milla Manager*")
        st.markdown("---")

        for label, page in NAV_PAGES.items():
            active = st.session_state.get("page") == page
            css    = "nav-active" if active else ""
            st.markdown(f'<div class="{css}">', unsafe_allow_html=True)
            if st.button(label, key=f"nav_{page}"):
                # Limpiar ficha abierta al cambiar sección
                for k in ("selected_empleado", "selected_vehiculo",
                          "selected_servicio"):
                    st.session_state.pop(k, None)
                st.session_state["page"] = page
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")
        ok = db_status()
        st.markdown(
            f"{'🟢' if ok else '🔴'} {'BD conectada' if ok else 'Sin conexión'}",
        )
        st.markdown("---")
        usuario = st.session_state.get("usuario", "—")
        rol     = st.session_state.get("rol", "—")
        st.markdown(f"**👤 {usuario}**")
        st.markdown(
            f'<span class="badge badge-orange">{rol}</span>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        if st.button("🚪 Cerrar sesión"):
            st.session_state.clear()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HELPERS DE UI
# ─────────────────────────────────────────────
def page_header(icon: str, title: str):
    st.markdown(f"""
    <div class="page-header">
        <span class="page-header-icon">{icon}</span>
        <h1>{title}</h1>
    </div>
    """, unsafe_allow_html=True)

def metric_card(label: str, value, color: str = "orange"):
    st.markdown(f"""
    <div class="card card-{color}">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

def badge(text: str, color: str = "blue") -> str:
    return f'<span class="badge badge-{color}">{text}</span>'

def back_button(label: str = "← Volver"):
    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    clicked = st.button(label)
    st.markdown("</div>", unsafe_allow_html=True)
    return clicked
