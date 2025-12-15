import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Ficha Vehículos", layout="wide")
st.title("🚘 Ficha de Vehículos")

DATA = Path("data")
CSV = DATA / "vehiculos.csv"

if not CSV.exists():
    st.warning("No hay vehículos cargados")
    st.stop()

df = pd.read_csv(CSV, dtype=str).fillna("")
df["id_vehiculo"] = df["id_vehiculo"].astype(int)
df = df.sort_values("id_vehiculo").reset_index(drop=True)

if "idx_veh" not in st.session_state:
    st.session_state.idx_veh = 0

veh = df.iloc[st.session_state.idx_veh]

# Navegación
col1, col2 = st.columns([8, 2])
with col1:
    st.selectbox(
        "Selecciona un vehículo",
        range(len(df)),
        format_func=lambda i: f"{df.iloc[i].matricula} - {df.iloc[i].marca}",
        index=st.session_state.idx_veh,
        key="veh_select"
    )

with col2:
    if st.button("◀"): st.session_state.idx_veh -= 1
    if st.button("▶"): st.session_state.idx_veh += 1

st.session_state.idx_veh = max(0, min(len(df)-1, st.session_state.idx_veh))
veh = df.iloc[st.session_state.idx_veh]

st.markdown("---")

st.subheader(f"🚗 {veh.matricula}")
st.write(f"Marca: {veh.marca}")
st.write(f"Modelo: {veh.modelo}")
st.write(f"Estado: {veh.estado}")
st.write(f"ITV: {veh.itv}")
st.write(f"Seguro: {veh.seguro}")
