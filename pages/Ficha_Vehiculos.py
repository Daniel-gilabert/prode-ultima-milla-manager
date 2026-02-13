import streamlit as st
import pandas as pd
import psycopg2

# ---------------------------------------
# CONEXIÓN
# ---------------------------------------

def get_connection():
    return psycopg2.connect(st.secrets["DATABASE_URL"])

st.title("🚗 Ficha de Vehículos")

# ---------------------------------------
# CARGAR VEHÍCULOS DESDE SUPABASE
# ---------------------------------------

try:
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM vehiculos ORDER BY matricula", conn)
    conn.close()

except Exception as e:
    st.error(f"Error cargando vehículos: {e}")
    st.stop()

if df.empty:
    st.warning("⚠️ No hay vehículos cargados en el sistema.")
    st.stop()

# ---------------------------------------
# SELECTOR
# ---------------------------------------

df["label"] = df["matricula"]

vehiculo_sel = st.selectbox(
    "Selecciona un vehículo",
    df["label"].tolist()
)

veh = df[df["label"] == vehiculo_sel].iloc[0]

st.markdown("---")

# ---------------------------------------
# DATOS
# ---------------------------------------

st.subheader("Información del vehículo")

col1, col2 = st.columns(2)

with col1:
    st.write(f"**Matrícula:** {veh['matricula']}")
    st.write(f"**Marca:** {veh['marca']}")
    st.write(f"**Modelo:** {veh['modelo']}")
    st.write(f"**Tipo:** {veh['tipo']}")
    st.write(f"**Bastidor:** {veh['bastidor']}")

with col2:
    st.write(f"**ITV vigente hasta:** {veh['itv_vigente_hasta']}")
    st.write(f"**Seguro**

