import streamlit as st
import pandas as pd
from pathlib import Path

# -----------------------------------------
# CONFIG
# -----------------------------------------
DATA_FILE = Path("data/vehiculos.json")
FOTOS_DIR = Path("data/fotos_vehiculos")

st.title("🚚 Ficha de Vehículos")

# -----------------------------------------
# CARGA SEGURA
# -----------------------------------------
if not DATA_FILE.exists() or DATA_FILE.stat().st_size == 0:
    st.warning("⚠️ No hay vehículos cargados en el sistema.")
    st.stop()

try:
    df = pd.read_json(DATA_FILE)
except ValueError:
    st.error("❌ El archivo vehiculos.json está corrupto.")
    st.stop()

df = df.fillna("")

if df.empty:
    st.warning("⚠️ No hay vehículos registrados.")
    st.stop()

if "id_vehiculo" not in df.columns:
    st.error("❌ Falta la columna id_vehiculo en vehiculos.json")
    st.stop()

df["id_vehiculo"] = df["id_vehiculo"].astype(int)

# -----------------------------------------
# SELECTOR
# -----------------------------------------
df["label"] = df["id_vehiculo"].astype(str) + " - " + df["matricula"]

vehiculo_sel = st.selectbox(
    "Selecciona un vehículo",
    df["label"].tolist()
)

vehiculo = df[df["label"] == vehiculo_sel].iloc[0]

# -----------------------------------------
# VISTA
# -----------------------------------------
col_info, col_foto = st.columns([3, 2])

with col_info:
    st.markdown(f"## {vehiculo['matricula']}")
    st.write(f"**Marca:** {vehiculo['marca']}")
    st.write(f"**Modelo:** {vehiculo['modelo']}")
    st.write(f"**Tipo:** {vehiculo['tipo']}")
    st.write(f"**Estado:** {vehiculo['estado']}")
    st.write(f"**Bastidor:** {vehiculo['bastidor']}")

    asignado = vehiculo.get("id_empleado", "")
    if asignado:
        st.success(f"Asignado a empleado ID {asignado}")
    else:
        st.info("No asignado a ningún empleado")

with col_foto:
    foto_path = FOTOS_DIR / f"{vehiculo['id_vehiculo']}.jpg"
    if foto_path.exists():
        st.image(str(foto_path), use_container_width=True)
    else:
        st.info("📷 Imagen del vehículo no disponible")

