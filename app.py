import streamlit as st
import pandas as pd
import os
from pathlib import Path

# -----------------------------------------
# CONFIGURACIÓN GENERAL
# -----------------------------------------
st.set_page_config(
    page_title="PRODE Última Milla Manager",
    layout="wide",
    initial_sidebar_state="expanded",
)
# -----------------------------------------
# OCULTAR MENÚ AUTOMÁTICO DE STREAMLIT
# -----------------------------------------
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------
# CARGA DE USUARIOS
# -----------------------------------------
def load_users():
    path = Path("data/usuarios.csv")

    if not path.exists():
        return pd.DataFrame([{
            "username": "admin",
            "password": "admin",
            "rol": "admin"
        }])

    for encoding in ["utf-8-sig", "latin1"]:
        try:
            return pd.read_csv(path, dtype=str, encoding=encoding).fillna("")
        except Exception:
            pass

    return pd.DataFrame([{
        "username": "admin",
        "password": "admin",
        "rol": "admin"
    }])

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
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

# -----------------------------------------
# CARGAR PÁGINA
# -----------------------------------------
def cargar_pagina(nombre):
    ruta = os.path.join("pages", nombre)
    if not os.path.exists(ruta):
        st.error(f"No existe la página: {nombre}")
        return

    with open(ruta, "r", encoding="utf-8") as f:
        exec(f.read(), globals())

# -----------------------------------------
# MENÚ PRINCIPAL
# -----------------------------------------
def mostrar_paginas():
    st.sidebar.markdown("## 🚚 PRODE Última Milla")

    rol = st.session_state.get("rol", "")

    # -------------------------
    # MENÚ CONSULTA (TODOS)
    # -------------------------
    st.sidebar.markdown("### 📊 Consulta")

    menu_consulta = {
        "Dashboard": "Dashboard.py",
        "Ficha empleados": "Ficha_Empleados.py",
        "Ficha vehículos": "Ficha_Vehiculos.py",
        "Ficha servicios": "Ficha_Servicios.py",
        "Ficha ausencias": "Ficha_Ausencias.py",
        "Documentación": "Documentacion.py",
    }

    opcion = st.sidebar.radio(
        "Ir a:",
        list(menu_consulta.keys()),
        key="menu_consulta"
    )

    # -------------------------
    # MENÚ ADMIN (SOLO ADMIN)
    # -------------------------
    if rol == "admin":
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🛠️ Gestión (Admin)")

        menu_admin = {
            "Administrar empleados": "Administrar_Empleados.py",
            "Administrar vehículos": "Administrar_Vehiculos.py",
            "Administrar servicios": "Administrar_Servicios.py",
            "Administrar ausencias": "Administrar_Ausencias.py",
            "Administrar mantenimiento": "Administrar_Mantenimiento.py",
            "Papelera central": "Papelera_Central.py",
        }

        opcion_admin = st.sidebar.radio(
            "Administrar:",
            list(menu_admin.keys()),
            key="menu_admin"
        )

        archivo = menu_admin[opcion_admin]

    else:
        archivo = menu_consulta[opcion]

    # -------------------------
    # CARGAR PÁGINA
    # -------------------------
    ruta = os.path.join("pages", archivo)

    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            exec(f.read(), globals())
    else:
        st.error(f"No existe la página: {archivo}")

    # -------------------------
    # FOOTER USUARIO
    # -------------------------
    st.sidebar.markdown("---")
    st.sidebar.write(f"👤 Usuario: **{st.session_state['usuario']}**")
    st.sidebar.write(f"🔐 Rol: **{st.session_state['rol']}**")

    if st.sidebar.button("Cerrar sesión"):
        st.session_state.clear()
        st.rerun()


# -----------------------------------------
# CONTROL PRINCIPAL
# -----------------------------------------
if "login" not in st.session_state or not st.session_state["login"]:
    pantalla_login()
else:
    mostrar_paginas()
