import streamlit as st
import pandas as pd
import os
from pathlib import Path

# =========================================
# CONFIGURACIÓN GENERAL
# =========================================
st.set_page_config(
    page_title="PRODE Última Milla Manager",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================
# CARGA DE USUARIOS
# =========================================
def load_users():
    path = Path("data/usuarios.csv")

    # Si NO existe usuarios.csv → admin por defecto
    if not path.exists():
        return pd.DataFrame([
            {"usuario": "admin", "contraseña": "admin", "rol": "admin"}
        ])

    try:
        df = pd.read_csv(path, encoding="latin1", dtype=str).fillna("")
    except Exception:
        # Archivo corrupto → no romper la app
        return pd.DataFrame([
            {"usuario": "admin", "contraseña": "admin", "rol": "admin"}
        ])

    # Validar columnas mínimas
    columnas_necesarias = {"usuario", "contraseña", "rol"}
    if not columnas_necesarias.issubset(df.columns):
        return pd.DataFrame([
            {"usuario": "admin", "contraseña": "admin", "rol": "admin"}
        ])

    return df


# =========================================
# VALIDACIÓN DE LOGIN
# =========================================
def validar_usuario(username, password):
    df = load_users()

    df["usuario"] = df["usuario"].astype(str).str.strip()
    df["contraseña"] = df["contraseña"].astype(str).str.strip()

    user = df[df["usuario"] == str(username).strip()]
    if not user.empty:
        if user.iloc[0]["contraseña"] == str(password).strip():
            return True, user.iloc[0]["rol"]

    return False, None


# =========================================
# PANTALLA LOGIN
# =========================================
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


# =========================================
# MENÚ PRINCIPAL
# =========================================
def mostrar_paginas():
    st.sidebar.title("🚚 PRODE Última Milla")

    rol = st.session_state.get("rol", "user")
    ES_ADMIN = rol == "admin"

    # =========================
    # CONSULTA (TODOS)
    # =========================
    st.sidebar.subheader("📊 Consulta")

    menu_consulta = {
        "Dashboard": "9_Dashboard.py",
        "Ficha de empleados": "Ficha_Empleados.py",
        "Ficha de vehículos": "Ficha_Vehiculos.py",
        "Servicios": "3_Servicios.py",
        "Calendario de ausencias": "Ausencias.py",
    }

    opcion_consulta = st.sidebar.radio(
        "Ver información",
        list(menu_consulta.keys()),
        key="menu_consulta"
    )

    archivo = menu_consulta[opcion_consulta]

    # =========================
    # GESTIÓN (SOLO ADMIN)
    # =========================
    if ES_ADMIN:
        st.sidebar.divider()
        st.sidebar.subheader("⚙️ Gestión")

        menu_admin = {
            "Administrar empleados": "Administrar_Empleados.py",
            "Administrar vehículos": "Administrar_Vehiculos.py",
            "Administrar servicios": "Administrar_Servicios.py",
            "Gestionar ausencias": "Administrar_Ausencias.py",
            "EPIs / PRL": "6_EPIs.py",
            "Documentación": "Documentacion.py",
            "Papelera": "10_Papelera_Central.py",
        }

        opcion_admin = st.sidebar.radio(
            "Administración",
            list(menu_admin.keys()),
            key="menu_admin"
        )

        archivo = menu_admin[opcion_admin]

    # =========================
    # CARGA DE PÁGINA
    # =========================
    ruta = os.path.join("pages", archivo)

    if not os.path.exists(ruta):
        st.error(f"❌ No existe la página: {archivo}")
    else:
        with open(ruta, "r", encoding="utf-8") as f:
            exec(f.read(), globals())

    # =========================
    # SESIÓN
    # =========================
    st.sidebar.divider()
    st.sidebar.write(f"👤 **Usuario:** {st.session_state.get('usuario','')}")
    st.sidebar.write(f"🔑 **Rol:** {rol}")

    if st.sidebar.button("🚪 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()


# =========================================
# CONTROL PRINCIPAL
# =========================================
if "login" not in st.session_state or st.session_state["login"] != True:
    pantalla_login()
else:
    mostrar_paginas()
