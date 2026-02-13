import streamlit as st
import pandas as pd
import psycopg2

# -----------------------------
# Conexión
# -----------------------------

def get_connection():
    return psycopg2.connect(st.secrets["DATABASE_URL"])

st.title("🚗 Ficha de Vehículos")

# -----------------------------
# Cargar vehículos
# -----------------------------

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

# -----------------------------
# Selector
# -----------------------------

vehiculo_sel = st.selectbox(
    "Selecciona un vehículo",
    df["matricula"].tolist()
)

veh = df[df["matricula"] == vehiculo_sel].iloc[0]

st.markdown("---")
st.subheader("Información del vehículo")

col1, col2 = st.columns(2)

with col1:
    st.write("Matrícula:", veh["matricula"])
    st.write("Marca:", veh["m]()


