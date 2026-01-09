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
# CARGA DE USUARIOS
# -----------------------------------------
def load_users():
    path = Path("data/usuarios.csv")

    # Si no existe usuarios.csv → admin por defecto
    if not path.exists():
        return pd.DataFrame([{
            "usuario": "admin",
            "contraseña": "admin",
            "rol": "admin"
        }])

    try:
        return pd.read_csv(path, encoding="latin1")
    except Exception:
        return pd.DataFrame([{
            "usuario": "admin",
            "contraseña": "admin",
            "rol": "admin"
        }])

# -----------------------------------------
# VALIDACIÓN DE USUARIO
# -----------------------------------------
def validar_usuario(username, password):
    df = load_users()

    if not {"usuario", "contraseña"}.issubset(df.columns):
        return False, None

    df["usuario"] = df["usuario"].astype(str).str.strip()
    df["contraseña"] = df["contraseña"].astype(str).str.strip()

    user = df[df["usuario"] == username]

    if not user.empty:
        if user.iloc[0]["contraseña"] == password:
            rol = user.iloc[0].get("rol", "consulta")
            return True, rol

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
# MENÚ SIMPLE (VERSIÓN ANTIGUA)
# -----------------------------------------
def mostrar_paginas():
    st.sidebar.title("PRODE Última Milla")

    menu = {
        "Dashboard": "9_Dashboard.py",
        "Ficha de empleados": "Ficha_Empleados.py",
        "Ficha de vehículos": "Ficha_Vehiculos.py",
        "Servicios": "3_Servicios.py",
        "Ausencias": "5_Ausencias.py",
        "EPIs": "6_EPIs.py",
        "Mantenimiento": "8_Mantenimiento.py",
        "Documentación": "Documentacion.py",
        "Administrar empleados": "Administrar_Empleados.py",
        "Administrar vehículos": "Administrar_Vehiculos.py",
        "Papelera Central": "10_Papelera_Central.py",
        "Papelera": "99_Papelera.py",
    }

    opcion = st.sidebar.radio("Ir a:", list(menu.keys()))
    archivo = menu[opcion]
    ruta = Path("pages") / archivo

    st.sidebar.write("---")
    st.sidebar.write(f"👤 Usuario: {st.session_state['usuario']}")

    if st.sidebar.button("Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

    if ruta.exists():
        with open(ruta, "r", encoding="utf-8") as f:
            exec(f.read(), globals())
    else:
        st.error(f"No existe la página: {archivo}")

# -----------------------------------------
# CONTROL PRINCIPAL
# -----------------------------------------
if "login" not in st.session_state:
    st.session_state["login"] = False

if not st.session_state["login"]:
    pantalla_login()
else:
    mostrar_paginas()
