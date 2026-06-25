import streamlit as st
import pandas as pd
from pathlib import Path
import psycopg2
from psycopg2 import OperationalError
import hashlib
import time

# ─────────────────────────────────────────────
# CONFIGURACIÓN GENERAL (SIEMPRE LO PRIMERO)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="PRODE · Última Milla Manager",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CSS PERSONALIZADO
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Paleta PRODE ── */
    :root {
        --prode-blue:   #1B3A6B;
        --prode-orange: #E8500A;
        --prode-light:  #F5F7FA;
        --prode-border: #D1D9E6;
        --text-main:    #1C2B3A;
        --text-soft:    #5A6D82;
    }

    /* ── Fondo general ── */
    .stApp { background-color: var(--prode-light); }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: var(--prode-blue) !important;
        color: white !important;
    }
    [data-testid="stSidebar"] * { color: white !important; }
    [data-testid="stSidebar"] .stButton > button {
        background: var(--prode-orange) !important;
        border: none !important;
        color: white !important;
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        margin-top: 8px;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        opacity: 0.88;
    }

    /* ── Tarjeta de login ── */
    .login-card {
        background: white;
        border-radius: 16px;
        padding: 2.5rem 2rem;
        box-shadow: 0 4px 24px rgba(27,58,107,0.10);
        max-width: 420px;
        margin: 3rem auto;
        border-top: 5px solid var(--prode-orange);
    }
    .login-logo {
        font-size: 2.8rem;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .login-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--prode-blue);
        text-align: center;
        margin-bottom: 0.1rem;
    }
    .login-subtitle {
        font-size: 0.88rem;
        color: var(--text-soft);
        text-align: center;
        margin-bottom: 1.6rem;
    }

    /* ── Inputs ── */
    .stTextInput > div > div > input {
        border-radius: 8px !important;
        border: 1.5px solid var(--prode-border) !important;
        padding: 0.55rem 0.8rem !important;
        font-size: 0.95rem !important;
        color: var(--text-main) !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: var(--prode-blue) !important;
        box-shadow: 0 0 0 3px rgba(27,58,107,0.12) !important;
    }

    /* ── Botón login ── */
    .login-btn > button {
        background: var(--prode-orange) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.2rem !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        width: 100% !important;
        transition: opacity 0.2s !important;
    }
    .login-btn > button:hover { opacity: 0.88 !important; }

    /* ── Métricas del dashboard ── */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        box-shadow: 0 2px 12px rgba(27,58,107,0.07);
        border-left: 4px solid var(--prode-orange);
        margin-bottom: 1rem;
    }
    .metric-label {
        font-size: 0.78rem;
        color: var(--text-soft);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.3rem;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        color: var(--prode-blue);
    }

    /* ── Badge de rol ── */
    .role-badge {
        display: inline-block;
        background: rgba(232,80,10,0.12);
        color: var(--prode-orange);
        border-radius: 20px;
        padding: 2px 12px;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* ── Ocultar nav automático si no logueado ── */
    .hide-nav [data-testid="stSidebarNav"] { display: none; }

    /* ── Cabecera de página ── */
    .page-header {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid var(--prode-border);
    }
    .page-header h1 {
        font-size: 1.6rem !important;
        color: var(--prode-blue) !important;
        margin: 0 !important;
        font-weight: 800 !important;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONEXIÓN A SUPABASE
# ─────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_connection():
    """Retorna una conexión persistente a Supabase (cacheada)."""
    try:
        conn = psycopg2.connect(st.secrets["DATABASE_URL"], connect_timeout=8)
        return conn
    except OperationalError as e:
        return None

def check_db_connection() -> bool:
    """Verifica si la BD está disponible sin bloquear la UI."""
    conn = get_connection()
    if conn is None:
        return False
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
        return True
    except Exception:
        # Conexión caída: limpia caché para reconectar
        get_connection.clear()
        return False

# ─────────────────────────────────────────────
# UTILIDADES DE SEGURIDAD
# ─────────────────────────────────────────────
def hash_password(password: str) -> str:
    """SHA-256 básico. En producción usar bcrypt/argon2."""
    return hashlib.sha256(password.encode()).hexdigest()

def _passwords_match(plain: str, stored: str) -> bool:
    """
    Compara contraseña ingresada con la almacenada.
    Soporta tanto texto plano (legacy) como SHA-256 hasheado.
    """
    if len(stored) == 64:                          # parece un hash SHA-256
        return hash_password(plain) == stored
    return plain == stored                         # compatibilidad retroactiva

# ─────────────────────────────────────────────
# CARGA Y VALIDACIÓN DE USUARIOS
# ─────────────────────────────────────────────
@st.cache_data(ttl=60, show_spinner=False)
def load_users() -> pd.DataFrame:
    """
    Carga usuarios desde data/usuarios.csv.
    Si no existe, retorna el usuario administrador por defecto.
    Columnas esperadas: username, password, rol
    """
    default = pd.DataFrame([
        {"username": "admin", "password": "admin", "rol": "admin"}
    ])
    path = Path("data/usuarios.csv")
    if not path.exists():
        return default
    for encoding in ("utf-8-sig", "utf-8", "latin1"):
        try:
            df = pd.read_csv(path, dtype=str, encoding=encoding).fillna("")
            # Verificar columnas mínimas
            if {"username", "password", "rol"}.issubset(df.columns):
                return df.applymap(str.strip)
        except Exception:
            continue
    return default


def validar_usuario(username: str, password: str):
    """
    Retorna (True, rol) si las credenciales son válidas,
    (False, None) en caso contrario.
    Añade un pequeño delay para mitigar fuerza bruta.
    """
    df = load_users()
    match = df[df["username"] == username.strip()]
    time.sleep(0.3)                                # anti-fuerza bruta mínimo
    if not match.empty:
        stored_pwd = match.iloc[0]["password"]
        if _passwords_match(password, stored_pwd):
            return True, match.iloc[0]["rol"]
    return False, None

# ─────────────────────────────────────────────
# PANTALLA DE LOGIN
# ─────────────────────────────────────────────
def pantalla_login():
    # Ocultar nav lateral cuando no hay sesión
    st.markdown(
        '<style>[data-testid="stSidebarNav"]{display:none}</style>',
        unsafe_allow_html=True,
    )

    # Centrar contenido en columna central
    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown("""
        <div class="login-card">
            <div class="login-logo">🚚</div>
            <div class="login-title">PRODE Última Milla</div>
            <div class="login-subtitle">Gestión de control de asistencia y rutas</div>
        </div>
        """, unsafe_allow_html=True)

        with st.container():
            username = st.text_input(
                "Usuario",
                placeholder="Ingresa tu usuario",
                key="login_user",
            )
            password = st.text_input(
                "Contraseña",
                type="password",
                placeholder="••••••••",
                key="login_pass",
            )

            st.markdown('<div class="login-btn">', unsafe_allow_html=True)
            login_clicked = st.button("Entrar", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

            if login_clicked:
                if not username or not password:
                    st.warning("Por favor completa usuario y contraseña.")
                else:
                    with st.spinner("Verificando..."):
                        ok, rol = validar_usuario(username, password)
                    if ok:
                        st.session_state["login"]   = True
                        st.session_state["usuario"] = username.strip()
                        st.session_state["rol"]     = rol
                        st.rerun()
                    else:
                        st.error("Usuario o contraseña incorrectos.")

# ─────────────────────────────────────────────
# SIDEBAR (POST-LOGIN)
# ─────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("### 🚚 PRODE · Última Milla")
        st.markdown("---")

        usuario = st.session_state.get("usuario", "—")
        rol     = st.session_state.get("rol", "—")

        st.markdown(f"**👤 {usuario}**")
        st.markdown(
            f'<span class="role-badge">{rol}</span>',
            unsafe_allow_html=True,
        )
        st.markdown("---")

        # Estado de la BD
        db_ok = check_db_connection()
        if db_ok:
            st.markdown("🟢 Base de datos conectada")
        else:
            st.markdown("🔴 Sin conexión a BD")

        st.markdown("---")
        if st.button("🚪 Cerrar sesión"):
            st.session_state.clear()
            st.rerun()

# ─────────────────────────────────────────────
# DASHBOARD PRINCIPAL
# ─────────────────────────────────────────────
def render_dashboard():
    # Cabecera
    st.markdown("""
    <div class="page-header">
        <span style="font-size:1.8rem">📊</span>
        <h1>Dashboard</h1>
    </div>
    """, unsafe_allow_html=True)

    rol = st.session_state.get("rol", "")

    # Métricas de ejemplo — reemplaza con tus queries reales
    col1, col2, col3, col4 = st.columns(4)
    metrics = [
        ("🚛 Rutas activas",      "—", col1),
        ("📦 Entregas hoy",       "—", col2),
        ("✅ Completadas",        "—", col3),
        ("⚠️ Incidencias",        "—", col4),
    ]
    for label, value, col in metrics:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.info("👈 Selecciona una sección desde el menú lateral para comenzar.", icon="ℹ️")

    # Panel de administración exclusivo
    if rol == "admin":
        with st.expander("🔧 Panel de administración", expanded=False):
            st.markdown("Aquí irán las herramientas de configuración exclusivas para admins.")
            if st.button("🔄 Limpiar caché de usuarios"):
                load_users.clear()
                st.success("Caché de usuarios limpiado.")

# ─────────────────────────────────────────────
# CONTROL PRINCIPAL
# ─────────────────────────────────────────────
if not st.session_state.get("login"):
    pantalla_login()
else:
    render_sidebar()
    render_dashboard()
