import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime

def get_connection():
    return psycopg2.connect(st.secrets["DATABASE_URL"])

def clean_value(value):
    if pd.isna(value) or value is None:
        return "—"
    return value

st.title("🚗 Ficha de Vehículos")

# ---------------------------------------
# CARGA DE DATOS
# ---------------------------------------
try:
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM vehiculos ORDER BY matricula", conn)
    conn.close()
except Exception as e:
    st.error(f"Error cargando vehículos: {e}")
    st.stop()

if df.empty:
    st.warning("No hay vehículos cargados en el sistema.")
    st.stop()

vehiculo_sel = st.selectbox(
    "Selecciona un vehículo",
    df["matricula"].astype(str).tolist()
)

veh = df[df["matricula"] == vehiculo_sel].iloc[0]

st.markdown("---")
st.subheader("📋 Información del vehículo")

col1, col2 = st.columns(2)

with col1:
    st.write("**Matrícula:**", clean_value(veh.get("matricula")))
    st.write("**Marca:**", clean_value(veh.get("marca")))
    st.write("**Modelo:**", clean_value(veh.get("modelo")))
    st.write("**Tipo:**", clean_value(veh.get("tipo")))
    st.write("**Bastidor:**", clean_value(veh.get("bastidor")))

with col2:
    st.write("**ITV vigente hasta:**", clean_value(veh.get("itv_vigente_hasta")))
    st.write("**Seguro vigente hasta:**", clean_value(veh.get("seguro_vigente_hasta")))
    st.write("**Aseguradora:**", clean_value(veh.get("aseguradora")))
    st.write("**Póliza:**", clean_value(veh.get("poliza")))

