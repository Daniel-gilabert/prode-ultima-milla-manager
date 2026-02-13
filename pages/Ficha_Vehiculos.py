import streamlit as st
import pandas as pd
import psycopg2

def get_connection():
    return psycopg2.connect(st.secrets["DATABASE_URL"])

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

# ---------------------------------------
# SELECTOR
# ---------------------------------------
vehiculo_sel = st.selectbox(
    "Selecciona un vehículo",
    df["matricula"].astype(str).tolist()
)

veh = df[df["matricula"] == vehiculo_sel].iloc[0]

st.markdown("---")
st.subheader("📋 Información del vehículo")

col1, col2 = st.columns(2)

# ---------------------------------------
# COLUMNA 1
# ---------------------------------------
with col1:
    st.write("**Matrícula:**", veh.get("matricula", ""))
    st.write("**Marca:**", veh.get("marca", ""))
    st.write("**Modelo:**", veh.get("modelo", ""))
    st.write("**Tipo:**", veh.get("tipo", ""))
    st.write("**Bastidor:**", veh.get("bastidor", ""))

# ---------------------------------------
# COLUMNA 2
# ---------------------------------------
with col2:
    st.write("**ITV vigente hasta:**", veh.get("itv_vigente_hasta", ""))
    st.write("**Seguro vigente hasta:**", veh.get("seguro_vigente_hasta", ""))
    st.write("**Aseguradora:**", veh.get("aseguradora", ""))
    st.write("**Póliza:**", veh.get("poliza", ""))
