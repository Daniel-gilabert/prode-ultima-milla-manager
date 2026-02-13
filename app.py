import streamlit as st
import pandas as pd
import os
from pathlib import Path
import psycopg2
import streamlit as st

def get_connection():
    return psycopg2.connect(st.secrets["DATABASE_URL"])

try:
    conn = get_connection()
    st.success("Conexión a Supabase OK 🚀")
    conn.close()
except Exception as e:
    st.error(f"Error de conexión: {e}")


# -----------------------------------------
# CONFIGURACIÓN GENERAL
# -----------------------------------------
st.set_page_config(
    page_title="PRODE Última Milla Manager",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------
# OCULTAR MENÚ AUTOMÁTICO DE STREAMLIT (CLAVE)
# -----------------------------------------
st.markdown("""
<style>
[data-testid="stSidebarNav"] {
    display: none;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------
# CARGA DE USUARIOS (ROBUSTA)
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

    for col in ["username", "password", "rol"]:
        if col not in df.columns:
            df[col] = ""

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
            st.session_state["pagina_actual"] = "Dashboard"
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

# -----------------------------------------
# NAVEGACIÓN PRINCIPAL
# -----------------------------------------
def mostrar_paginas():

    # Página activa (UNA SOLA SIEMPRE)
    if "pagina_actual" not in st.session_state:
        st.session_state["pagina_actual"] = "Dashboard"

    # ---------------- CONSULTA ----------------
    st.sidebar.markdown("## 📊 Consulta")

    consulta_paginas = {
        "Dashboard": "Dashboard.py",
        "Ficha empleados": "Ficha_Empleados.py",
        "Ficha vehículos": "Ficha_Vehiculos.py",
        "Ficha servicios": "Ficha_Servicios.py",
        "Ficha ausencias": "Ficha_Ausencias.py",
        "Documentación": "Documentacion.py",
    }

    consulta_keys = list(consulta_paginas.keys())
    consulta_index = (
        consulta_keys.index(st.session_state["pagina_actual"])
        if st.session_state["pagina_actual"] in consulta_keys else 0
    )

    seleccion_consulta = st.sidebar.radio(
        "Ir a:",
        consulta_keys,
        index=consulta_index,
        key="menu_consulta"
    )

    st.session_state["pagina_actual"] = seleccion_consulta

    # ---------------- GESTIÓN (ADMIN) ----------------
    admin_paginas = {}
    if st.session_state["rol"] == "admin":
        st.sidebar.markdown("---")
        st.sidebar.markdown("## 🛠️ Gestión (Admin)")

        admin_paginas = {
            "Administrar empleados": "Administrar_Empleados.py",
            "Administrar vehículos": "Administrar_Vehiculos.py",
            "Administrar servicios": "Administrar_Servicios.py",
            "Administrar ausencias": "Administrar_Ausencias.py",
            "Administrar mantenimiento": "Administrar_Mantenimiento.py",
            "Papelera central": "Papelera_Central.py",
        }

        admin_keys = list(admin_paginas.keys())
        admin_index = (
            admin_keys.index(st.session_state["pagina_actual"])
            if st.session_state["pagina_actual"] in admin_keys else -1
        )

        seleccion_admin = st.sidebar.radio(
            "Administrar:",
            ["—"] + admin_keys,
            index=admin_index + 1 if admin_index >= 0 else 0,
            key="menu_admin"
        )

        if seleccion_admin != "—":
            st.session_state["pagina_actual"] = seleccion_admin

    # ---------------- CARGA DE LA PÁGINA ----------------
    pagina = st.session_state["pagina_actual"]

    archivo = (
        consulta_paginas.get(pagina)
        or admin_paginas.get(pagina)
    )

    if archivo:
        ruta = os.path.join("pages", archivo)
        if os.path.exists(ruta):
            exec(open(ruta, encoding="utf-8").read(), globals())
        else:
            st.error(f"No existe la página: {archivo}")

    # ---------------- INFO USUARIO ----------------
    st.sidebar.markdown("---")
    st.sidebar.write(f"👤 Usuario: **{st.session_state['usuario']}**")
    st.sidebar.write(f"🔐 Rol: **{st.session_state['rol']}**")

    if st.sidebar.button("Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

# -----------------------------------------
# CONTROL PRINCIPAL
# -----------------------------------------
if "login" not in st.session_state or st.session_state["login"] is not True:
    pantalla_login()
else:
    mostrar_paginas()
