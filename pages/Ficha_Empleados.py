import streamlit as st
import pandas as pd
from pathlib import Path
from utils.storage import load_json

# -----------------------------------------
# CONFIGURACIÓN
# -----------------------------------------
DATA_EMPLEADOS = "data/empleados.json"
FOTOS_DIR = Path("data/fotos_empleados")

st.title("👤 Ficha de Empleados")

# -----------------------------------------
# CARGA DE EMPLEADOS
# -----------------------------------------
empleados = load_json(DATA_EMPLEADOS, [])

if not empleados:
    st.warning("⚠️ No hay empleados cargados en el sistema.")
    st.stop()

df = pd.DataFrame(empleados).fillna("")

# Asegurar columnas mínimas
for col in [
    "id_empleado", "nombre", "dni", "email",
    "telefono", "puesto", "ubicacion", "estado"
]:
    if col not in df.columns:
        df[col] = ""

# -----------------------------------------
# SELECTOR DE EMPLEADO
# -----------------------------------------
st.subheader("Selecciona un empleado")

df["label"] = df["nombre"] + " (" + df["dni"] + ")"

empleado_sel = st.selectbox(
    "Empleado",
    df["label"].tolist()
)

emp = df[df["label"] == empleado_sel].iloc[0]

st.markdown("---")

# -----------------------------------------
# LAYOUT FOTO + DATOS
# -----------------------------------------
col_foto, col_info = st.columns([1, 3])

# ---------- FOTO ----------
with col_foto:
    foto_path = FOTOS_DIR / f"{emp['id_empleado']}.jpg"

    if foto_path.exists():
        st.image(
            str(foto_path),
            caption="Foto del empleado",
            width=150
        )
    else:
        st.info("📷 Sin foto")

# ---------- DATOS ----------
with col_info:
    st.markdown(f"## {emp['nombre']}")
    st.write(f"**DNI:** {emp['dni']}")
    st.write(f"**Email:** {emp['email']}")
    st.write(f"**Teléfono:** {emp['telefono']}")
    st.write(f"**Puesto:** {emp['puesto']}")
    st.write(f"**Ubicación:** {emp['ubicacion']}")
    st.write(f"**Estado:** {emp['estado']}")

st.markdown("---")

# -----------------------------------------
# BLOQUES FUTUROS (YA PREPARADOS)
# -----------------------------------------
st.subheader("🧰 EPIs")
st.info("EPIs asociados al empleado (pendiente de implementación)")

st.subheader("🩺 PRL y reconocimientos médicos")
st.info("Cursos PRL, reconocimientos y documentación médica")

st.subheader("🚐 Vehículo asignado")
vehiculo = emp.get("vehiculo_asignado", "")

if vehiculo:
    st.success(f"Vehículo asignado: {vehiculo}")
else:
    st.info("No tiene vehículo asignado")
