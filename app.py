import streamlit as st
import pandas as pd
import os

# -----------------------------------------
# CONFIGURACIÓN DE LA APP
# -----------------------------------------
st.set_page_config(
    page_title="PRODE Última Milla Manager",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------
# CARGA DE USUARIOS DESDE CSV
# -----------------------------------------
def load_users():
    """Carga el archivo de usuarios con codificación correcta."""
    try:
        return pd.read_csv("data/usuarios.csv", encoding="utf-8-sig")
    except:
        return pd.read_csv("data/usuarios.csv", encoding="latin1")

# -----------------------------------------
# VALIDACIÓN DE CREDENCIALES
# -----------------------------------------
def validar_usuario(username, password):
    df = load_users()

    # Asegurar que no haya espacios ocultos
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
# MENÚ LATERAL Y NAVEGACIÓN
# -----------------------------------------
def cargar_paginas():
    """Carga automáticamente las páginas desde la carpeta pages."""
    paginas = {}
    base_dir = "pages"

    if not os.path.exists(base_dir):
        return paginas

    for file in sorted(os.listdir(base_dir)):
        if file.endswith(".py"):
            nombre = file.replace(".py", "")
            ruta = os.path.join(base_dir, file)
            paginas[nombre] = ruta

    return paginas

def mostrar_paginas():
    paginas = cargar_paginas()
    
    st.sidebar.title("Menú")
    seleccion = st.sidebar.radio("Ir a:", list(paginas.keys()))

    # Ejecuta la página seleccionada
    with open(paginas[seleccion], "r", encoding="utf-8") as f:
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

