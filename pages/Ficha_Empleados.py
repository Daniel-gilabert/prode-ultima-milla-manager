import streamlit as st
import json
from pathlib import Path

# ----------------------------------------
# CONFIG
# ----------------------------------------
st.set_page_config(page_title="Ficha de Empleados", layout="wide")

DATA_PATH = Path("data/empleados.json")

st.title("🗂️ Ficha de Empleados")

# ----------------------------------------
# CARGA SEGURA DE EMPLEADOS
# ----------------------------------------
def cargar_empleados():
    if not DATA_PATH.exists():
        return []

    try:
        contenido = DATA_PATH.read_text(encoding="utf-8").strip()
        if not contenido or contenido == "[]":
            return []
        return json.loads(contenido)
    except Exception as e:
        st.error("❌ No se pudo leer empleados.json. El archivo está dañado.")
        st.exception(e)
        return []

empleados = cargar_empleados()

# ----------------------------------------
# SIN EMPLEADOS
# ----------------------------------------
if not empleados:
    st.warning("⚠️ No hay empleados cargados en el sistema.")
    st.info("👉 Ve a **Administrar Empleados** y carga el Excel.")
    st.stop()

# ----------------------------------------
# SELECTOR
# ----------------------------------------
opciones = {
    f"{e.get('id_empleado')} - {e.get('nombre')}": e
    for e in empleados
}

seleccion = st.selectbox(
    "Selecciona un empleado",
    list(opciones.keys())
)

emp = opciones[seleccion]

# ----------------------------------------
# FICHA
# ----------------------------------------
st.divider()

col1, col2 = st.columns([1, 2])

with col1:
    st.info("👤 Empleado sin foto")

with col2:
    st.subheader(emp.get("nombre", ""))

    st.markdown(f"**🆔 ID empleado:** {emp.get('id_empleado','')}")
    st.markdown(f"**🪪 DNI:** {emp.get('dni','')}")
    st.markdown(f"**📧 Email:** {emp.get('email','')}")
    st.markdown(f"**📞 Teléfono:** {emp.get('telefono','')}")
    st.markdown(f"**💼 Puesto:** {emp.get('puesto','')}")
    st.markdown(f"**📍 Ubicación:** {emp.get('ubicacion','')}")
    st.markdown(f"**✅ Estado:** {emp.get('estado','activo')}")

st.divider()
st.caption("Los vehículos, EPIs, ausencias y documentación se integrarán aquí.")


