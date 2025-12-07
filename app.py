import streamlit as st
import pandas as pd
import os

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
    try:
        return pd.read_csv("data/usuarios.csv", encoding="utf-8-sig")
    except:
        return pd.read_csv("data/usuarios.csv", encoding="latin1")

# -----------------------------------------
# VALIDACIÓN DE CREDENCIALES
# -----------------------------------------
def validar_usuario(username, password):
    df = load_users()

    df["usuario"] = df["usuario"].astype(str).str.strip()
    df["contraseña"] = df["contraseña"].astype(str).str.strip()

    user = df[df["usuario"] == username]
    if not user.empty:
        stored_pass = str(user.iloc[0]["contraseña"])
        if stored_pass == str(password):
            rol = user.iloc[0]["rol"]
            return True, rol

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
# MENÚ ORDENADO SEGÚN TU LISTA (1–2–6–3–4–7–10–8–9)
# -----------------------------------------
def mostrar_paginas():
    st.sidebar.title("Menú")

    # ORDEN PERSONALIZADO EXACTO QUE PEDISTE
    orden_menu = {
        "9_Dashboard": "Dashboard",               # 1
        "Empleados": "Empleados",                 # 2
        "6_EPIs": "EPIs",                         # 6
        "3_Servicios": "Servicios",               # 3
        "4_Vehiculos": "Vehículos",               # 4
        "8_Mantenimiento": "Mantenimiento",       # 7
        "Documentacion": "Documentación",         # 10
        "10_Papelera_Central": "Papelera Central",# 8
        "99_Papelera": "Papelera",                # 9
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
if "login" not in st.session_state or st.session_state["login"] != True:
    pantalla_login()
else:
    mostrar_paginas()


