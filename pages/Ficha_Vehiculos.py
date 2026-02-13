import psycopg2
import streamlit as st

def get_connection():
    return psycopg2.connect(st.secrets["DATABASE_URL"])

import streamlit as st
import pandas as pd
from pathlib import Path
from utils.storage import load_json

# -----------------------------------------
# CONFIGURACIÓN
# -----------------------------------------
DATA_VEHICULOS = "data/vehiculos.json"
FOTOS_DIR = Path("data/fotos_vehiculos")

st.title("🚗 Ficha de Vehículos")

# -----------------------------------------
# CARGA DE VEHÍCULOS
# -----------------------------------------
vehiculos = load_json(DATA_VEHICULOS, [])

if not vehiculos:
    st.warning("⚠️ No hay vehículos cargados en el sistema.")
    st.stop()

df = pd.DataFrame(vehiculos).fillna("")

# Asegurar columnas mínimas
for col in [
    "id_vehiculo", "matricula", "marca", "modelo",
    "tipo", "estado", "bastidor", "empleado_asignado"
]:
    if col not in df.columns:
        df[col] = ""

# -----------------------------------------
# SELECTOR DE VEHÍCULO
# -----------------------------------------
st.subheader("Selecciona un vehículo")

df["label"] = df["id_vehiculo"].astype(str) + " - " + df["matricula"]

vehiculo_sel = st.selectbox(
    "Vehículo",
    df["label"].tolist()
)

veh = df[df["label"] == vehiculo_sel].iloc[0]

st.markdown("---")

# -----------------------------------------
# LAYOUT FOTO + DATOS
# -----------------------------------------
col_info, col_foto = st.columns([3, 2])

# ---------- DATOS ----------
with col_info:
    st.markdown(f"## {veh['matricula']}")
    st.write(f"**Marca:** {veh['marca']}")
    st.write(f"**Modelo:** {veh['modelo']}")
    st.write(f"**Tipo:** {veh['tipo']}")
    st.write(f"**Estado:** {veh['estado']}")
    st.write(f"**Bastidor:** {veh['bastidor']}")

# ---------- FOTO ----------
with col_foto:
    fotos_dir = Path("data/fotos_vehiculos")
    foto = None

    for ext in ["jpg", "jpeg", "png", "JPG", "JPEG", "PNG"]:
        posible = fotos_dir / f"{veh['id_vehiculo']}.{ext}"
        if posible.exists():
            foto = posible
            break

    if foto:
        st.image(str(foto), use_container_width=True)
    else:
        st.info("📷 Imagen del vehículo no disponible")

# -----------------------------------------
# EMPLEADO ASIGNADO
# -----------------------------------------
st.subheader("👤 Empleado asignado")

if veh["empleado_asignado"]:
    st.success(f"Asignado a: {veh['empleado_asignado']}")
else:
    st.info("No asignado a ningún empleado")

# -----------------------------------------
# BLOQUES FUTUROS (PREPARADOS)
# -----------------------------------------
st.subheader("🛠️ Mantenimiento")
st.info("Historial de mantenimientos (pendiente de implementación)")

st.subheader("📄 Documentación")
st.info("ITV, seguro, revisiones, etc.")
