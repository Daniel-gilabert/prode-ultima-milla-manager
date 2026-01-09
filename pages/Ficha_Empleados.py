import streamlit as st
import json
from pathlib import Path
import pandas as pd

st.title("👤 Ficha de Empleados")

# -----------------------------------------
# RUTA DE DATOS
# -----------------------------------------
EMP_FILE = Path("data/empleados.json")

# -----------------------------------------
# CARGA DE EMPLEADOS
# -----------------------------------------
def load_empleados():
    if EMP_FILE.exists():
        try:
            return json.loads(EMP_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []

empleados = load_empleados()

# -----------------------------------------
# SIN EMPLEADOS
# -----------------------------------------
if not empleados:
    st.warning("No hay empleados cargados en el sistema.")
    st.stop()

# -----------------------------------------
# SELECTOR DE EMPLEADO
# -----------------------------------------
st.subheader("Selecciona un empleado")

# Convertimos a DataFrame solo para facilitar filtros
df = pd.DataFrame(empleados)

# Campo que se mostrará en el selector
df["display"] = (
    df.get("nombre", "") + " " + df.get("apellidos", "") + " (" + df.get("dni", "") + ")"
)

seleccion = st.selectbox(
    "Empleado",
    df["display"].tolist()
)

emp = df[df["display"] == seleccion].iloc[0].to_dict()

st.markdown("---")

# -----------------------------------------
# DATOS DEL EMPLEADO
# -----------------------------------------
col1, col2 = st.columns([1, 3])

with col1:
 from pathlib import Path

foto_path = Path(f"data/fotos_empleados/{empleado['id_empleado']}.jpg")

if foto_path.exists():
    st.image(str(foto_path), width=150, caption="Foto empleado")
else:
    st.info("📷 Sin foto")


with col2:
    st.markdown(f"### {emp.get('nombre','')} {emp.get('apellidos','')}")
    st.write(f"**DNI:** {emp.get('dni','')}")
    st.write(f"**Email:** {emp.get('email','')}")
    st.write(f"**Teléfono:** {emp.get('telefono','')}")
    st.write(f"**Puesto:** {emp.get('puesto','')}")
    st.write(f"**Ubicación:** {emp.get('ubicacion','')}")
    st.write(f"**Estado:** {emp.get('estado','')}")

st.markdown("---")

# -----------------------------------------
# SECCIONES FUTURAS
# -----------------------------------------
st.subheader("📦 EPIs")
st.info("Sección de EPIs (en construcción)")

st.subheader("📅 Ausencias")
st.info("Sección de ausencias (en construcción)")

st.subheader("🛠️ Servicios")
st.info("Sección de servicios (en construcción)")

st.subheader("🚗 Vehículo asignado")
st.info("Sección de vehículo asignado (en construcción)")






