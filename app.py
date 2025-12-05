import streamlit as st
import json
from pathlib import Path
# Cargar estilos CSS
def load_css():
    try:
        with open("assets/estilos.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except:
        pass

load_css()


# ============================
# CONFIGURACIÓN GENERAL
# ============================
APP_NAME = "PRODE Última Milla Manager"
LOGO_PATH = "assets/logo_prode.jpg"

ADMIN_USER = "daniel"
ADMIN_PASS = "admin123"

EDITOR_USER = "jorge"
EDITOR_PASS = "editor123"

# ============================
# FUNCIÓN UTILIDADES
# ============================

def load_json(path):
    if Path(path).exists():
        return json.loads(Path(path).read_text(encoding="utf-8"))
    return []

def save_json(path, data):
    Path(path).write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")

# ============================
# LOGIN
# ============================

if "logged" not in st.session_state:
    st.session_state.logged = False
    st.session_state.role = ""

def login_screen():
    st.title(APP_NAME)
    if Path(LOGO_PATH).exists():
        st.image(LOGO_PATH, width=180)

    st.subheader("Acceso al sistema")
    user = st.text_input("Usuario")
    pwd = st.text_input("Contraseña", type="password")

    if st.button("Entrar"):
        if user == ADMIN_USER and pwd == ADMIN_PASS:
            st.session_state.logged = True
            st.session_state.role = "admin"
            st.success("Acceso como ADMIN")
        elif user == EDITOR_USER and pwd == EDITOR_PASS:
            st.session_state.logged = True
            st.session_state.role = "editor"
            st.success("Acceso como EDITOR")
        else:
            st.error("Usuario o contraseña incorrectos")


if not st.session_state.logged:
    login_screen()
    st.stop()

# ============================
# MENÚ LATERAL
# ============================

st.sidebar.title("Menú Principal")
page = st.sidebar.radio("Ir a:", ["Dashboard", "Empleados"])

st.sidebar.markdown("---")
st.sidebar.write(f"Sesión iniciada como: **{st.session_state.role.upper()}**")
if st.sidebar.button("Cerrar sesión"):
    st.session_state.logged = False
    st.session_state.role = ""
    st.rerun()

# ============================
# PÁGINA DASHBOARD
# ============================

if page == "Dashboard":
    st.title("📊 Dashboard — PRODE Última Milla Manager")

    if Path(LOGO_PATH).exists():
        st.image(LOGO_PATH, width=200)

    st.markdown("### Bienvenido, AMCHÍ 👋")
    st.write("Desde aquí podrás acceder a empleados, servicios, vehículos y ausencias.")

    empleados = load_json("data/empleados.json")
    st.metric("Empleados activos", len(empleados))

# ============================
# PÁGINA EMPLEADOS
# ============================

if page == "Empleados":
    st.title("👷‍♂️ Gestión de Empleados")

    empleados = load_json("data/empleados.json")

    st.subheader("Añadir nuevo empleado")

    nombre = st.text_input("Nombre")
    apellidos = st.text_input("Apellidos")
    dni = st.text_input("DNI")
    telefono = st.text_input("Teléfono personal")
    correo = st.text_input("Correo personal")
    puesto = st.text_input("Puesto")
    foto = st.file_uploader("Foto del empleado", type=["jpg", "png"])

    if st.button("Guardar empleado"):
        if nombre and apellidos:
            nuevo = {
                "id": len(empleados)+1,
                "nombre": nombre,
                "apellidos": apellidos,
                "dni": dni,
                "telefono": telefono,
                "correo": correo,
                "puesto": puesto
            }
            empleados.append(nuevo)
            save_json("data/empleados.json", empleados)
            st.success("Empleado añadido correctamente")
            st.rerun()
        else:
            st.error("Nombre y apellidos obligatorios")

    st.subheader("Listado de empleados")

    for emp in empleados:
        with st.expander(f"{emp['nombre']} {emp['apellidos']}"):
            st.write(emp)
            if st.session_state.role == "admin":
                if st.button(f"Eliminar {emp['id']}"):
                    papelera = load_json("data/papelera.json")
                    papelera.append(emp)
                    save_json("data/papelera.json", papelera)

                    empleados = [e for e in empleados if e["id"] != emp["id"]]
                    save_json("data/empleados.json", empleados)

                    st.warning("Empleado movido a la papelera")
                    st.rerun()
