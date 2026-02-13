import streamlit as st
import pandas as pd
from pathlib import Path
import psycopg2

# -----------------------------------------
# CONFIGURACIÓN GENERAL (SIEMPRE LO PRIMERO)
# -----------------------------------------
st.set_page_config(
    page_title="PRODE Última Milla Manager",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------
# CONEXIÓN A SUPABASE (TEST)
# -----------------------------------------
def get_connection():
    return psycopg2.connect(st.secrets["DATABASE_URL"])

try:
    conn = get_connection()
    st.success("Conexión a Supabase OK 🚀")
    conn.close()
except Exception as e:
    st.error(f"Error de conexión: {e}")

# -----------------------------------------
# OCULTAR MENÚ AUTOMÁTICO SOLO SI NO LOGUEADO
# -----------------------------------------
if "login" not in st.session_state:
    st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {display: none;}
    </style>
    """, unsafe_allow_html=True)

# -----------------------------------------
# CARGA DE USUARIOS
# -----------------------------------------
def load_users():
    path = Path("data/usuarios.csv")

    if not path.exists():
        return pd.DataFrame([
            {"username": "admin", "password": "admin", "rol": "admin"}
        ])

    for encoding in ["utf-8-sig", "latin1"]:
        try:
            return pd.read_csv(path, dtype=str, encoding=encoding).fillna("")
        except Exception:
            pass

    return pd.DataFrame([
        {"username": "admin", "password": "admin", "rol": "admin"}
    ])

# -----------------------------------------
# VALIDACIÓN DE USUARIO
# -----------------------------------------
def validar_usuario(username, password):
    df = load_users()

    df["username"] = df["username"].astype(str).str.strip()
    df["password"] = df["password"].astype(str).str.strip()

    user = df[df["username"] == str(username).strip()]

    if not user.empty and user.iloc[0]["password"] == str(password):
        return True, user.iloc[0]["rol"]

    return False, None

# -----------------------------------------
# LOGIN
# -----------------------------------------
def pantalla_login():
    st.title("🚚 PRODE Última Milla Manager")
    st.subheader("Acceso al sistema")

    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Entrar"):
        ok, rol = validar_usuario(username, password)

        if ok:
            st.session_state["login"] = True
            st.session_state["usuario"] = username
            st.session_state["rol"] = rol
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

# -----------------------------------------
# CONTROL PRINCIPAL
# -----------------------------------------
if "login" not in st.session_state or st.session_state["login"] is not True:
    pantalla_login()
else:
    st.sidebar.markdown("---")
    st.sidebar.write(f"👤 Usuario: **{st.session_state['usuario']}**")
    st.sidebar.write(f"🔐 Rol: **{st.session_state['rol']}**")

    if st.sidebar.button("Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

    st.title("📊 Dashboard")
    st.write("Selecciona una página desde el menú lateral.")

