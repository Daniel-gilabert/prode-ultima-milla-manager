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
# CARGA DE USUARIOS (ROBUSTA)
# -----------------------------------------
def load_users():
    path = Path("data/usuarios.csv")

    # Usuario admin por defecto si no existe el archivo
    if not path.exists():
        return pd.DataFrame([
            {
                "username": "admin",
                "password": "admin",
                "rol": "admin"
            }
        ])

    # Intentos de lectura robustos
    for encoding in ["utf-8-sig", "latin1"]:
        try:
            df = pd.read_csv(path, dtype=str, encoding=encoding).fillna("")
            return df
        except Exception:
            pass

    # Fallback absoluto (no romper la app)
    return pd.DataFrame([
        {
            "username": "admin",
            "password": "admin",
            "rol": "admin"
        }
    ])

# -----------------------------------------
# VALIDACIÓN DE CREDENCIALES (CORREGIDA)
# -----------------------------------------
def validar_usuario(username, password):
    df = load_users()

    # Normalizar columnas esperadas
    for col in ["username", "password", "rol"]:
        if col not in df.columns:
            df[col] = ""

    df["username"] = df["username"].astype(str).str.strip()
    df["password"] = df["password"].astype(str).str.strip()

    user = df[df["username"] == str(username).strip()]

    if not user.empty:
        stored_pass = user.iloc[0]["password"]
        if stored_pass == str(password):
            return True, user.iloc[0]["rol"]

    return False, None

# -----------------------------------------
# PANTALLA DE LOGIN
# -----------------------------------------
def pantalla_login():
    st.title("PRODE Última Milla Manager")
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
# MENÚ PRINCIPAL
# -----------------------------------------
def mostrar_paginas():
    st.sidebar.title("Menú")

    orden_menu = {
        "9_Dashboard": "Dashboard",
        "Empleados": "Empleados",
        "6_EPIs": "EPIs",
        "3_Servicios": "Servicios",
        "4_Vehiculos": "Vehículos",
        "8_Mantenimiento": "Mantenimiento",
        "Documentacion": "Documentación",
        "10_Papelera_Central": "Papelera Central",
        "99_Papelera": "Papelera",
    }

    seleccion = st.sidebar.radio("Ir a:", list(orden_menu.values()))

    archivo = [k for k, v in orden_menu.items() if v == seleccion][0] + ".py"
    ruta = os.path.join("pages", archivo)

    with open(ruta, "r", encoding="utf-8") as f:
        code = f.read()
        exec(code, globals())

    st.sidebar.write("---")
    st.sidebar.write(f"Usuario: **{st.session_state['usuario']}**")
    st.sidebar.write(f"Rol: **{st.session_state['rol']}**")

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
