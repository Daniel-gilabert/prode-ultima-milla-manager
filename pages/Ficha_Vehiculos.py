import streamlit as st
import pandas as pd
import psycopg2

def get_connection():
    return psycopg2.connect(st.secrets["DATABASE_URL"])

st.title("Ficha de Vehiculos")

try:
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM vehiculos ORDER BY matricula", conn)
    conn.close()
except Exception as e:
    st.error(f"Error cargando vehiculos: {e}")
    st.stop()

if df.empty:
    st.warning("No hay vehiculos cargados en el sistema.")
    st.stop()

vehiculo_sel = st.selectbox(
    "Selecciona un vehiculo",
    df["matricula"].tolist()
)

veh = df[df["matricula"] == vehiculo_sel].iloc[0]

st.markdown("---")
st.subheader("Informacion del vehiculo")

col1, col2 = st.columns(2)

with col1:
    st.write("Matricula:", veh["matricula"])
    st.write("Marca:", v["marca"])
    st.write("Modelo:", veh["modelo"])
    st.write("Tipo:", veh["tipo"])
    st.write("Bastidor:", veh["bastidor"])

with col2:
    st.write("ITV vigente hasta:", veh["itv_vigente_hasta"])
    st.write("Seguro vigente hasta:", veh["seguro_vigente_hasta"])
    st.write("Aseguradora:", veh["aseguradora"])
    st.write("Poliza:", veh["poliza"])
