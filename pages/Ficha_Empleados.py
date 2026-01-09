import streamlit as st
import pandas as pd
from pathlib import Path

# -----------------------------------------
# CONFIG
# -----------------------------------------
st.title("👤 Ficha de Empleados")

DATA_FILE = Path("data/empleados.json")
FOTOS_DIR = Path("data/fotos_empleados")

# -----------------------------------------
# CARGA DE DATOS
# -----------------------------------------
if not DATA_FILE.exists():
    st.warning("⚠️ No hay empleados cargados en el sistema.")
    st.stop()

df = pd.read_json(DATA_FILE)

if df.empty:
    st.warning("⚠️ No hay empleados cargados en el sistema.")
    st.stop()

# Asegurar tipos
df["id_empleado"] = df["id_empleado"].astype(int)
df = df.fillna("")

# -----------------------------------------
# SELECTOR DE EMPLEADO
# -----------------------------------------
st.subheader("Selecciona un empleado")

opciones = {
    f"{row['nombre']} ({row['dni']})": row["id_empleado"]
    for _, row in df.iterrows()
}

empleado_label = st.selectbox(
    "Empleado",
    list(opciones.keys())
)

id_empleado = opciones[empleado_label]
empleado = df[df["id_empleado"] == id_empleado].iloc[0]

st.divider()

# -----------------------------------------
# LAYOUT PRINCIPAL
# -----------------------------------------
col_foto, col_info = st.columns([1, 3])

# ---------- FOTO ----------
with col_foto:
    foto_path = FOTOS_DIR / f"{id_empleado}.jpg"

    if foto_path.exists():
        st.image(str(foto_path), width=150)
    else:
        st.info("📷 Sin foto")

# ---------- DATOS ----------
with col_info:
    st.markdown(f"## {empleado['nombre']}")

    st.write(f"**DNI:** {empleado['dni']}")
    st.write(f"**Email:** {empleado['email']}")
    st.write(f"**Teléfono:** {empleado['telefono']}")
    st.write(f"**Puesto:** {empleado['puesto']}")
    st.write(f"**Ubicación:** {empleado['ubicacion']}")
    st.write(f"**Estado:** {empleado['estado']}")

st.divider()

# -----------------------------------------
# EPIs (LECTURA)
# -----------------------------------------
st.subheader("📦 EPIs")

if "epis" in empleado and empleado["epis"]:
    st.success("EPIs registrados")
    st.json(empleado["epis"])
else:
    st.info("No hay EPIs registrados para este empleado.")

# -----------------------------------------
# AUSENCIAS (LECTURA)
# -----------------------------------------
st.subheader("📅 Ausencias")

if "ausencias" in empleado and empleado["ausencias"]:
    st.success("Ausencias registradas")
    st.json(empleado["ausencias"])
else:
    st.info("No hay ausencias registradas.")

# -----------------------------------------
# SERVICIOS (LECTURA)
# -----------------------------------------
st.subheader("🛠️ Servicios")

if "servicios" in empleado and empleado["servicios"]:
    st.success("Servicios registrados")
    st.json(empleado["servicios"])
else:
    st.info("No hay servicios asociados.")

# -----------------------------------------
# VEHÍCULO ASIGNADO (PREPARADO PARA CLICK FUTURO)
# -----------------------------------------
st.subheader("🚗 Vehículo asignado")

if "vehiculo_id" in empleado and empleado["vehiculo_id"]:
    st.info(f"Vehículo asignado ID: {empleado['vehiculo_id']}")
    st.caption("👉 (En el siguiente paso lo haremos clickable)")
else:
    st.info("No tiene vehículo asignado.")
