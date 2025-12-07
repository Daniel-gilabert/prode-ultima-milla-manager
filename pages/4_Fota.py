import streamlit as st
import pandas as pd
import os

st.title("Gestión de Flota")

# -----------------------------------------
# TABS PARA SEPARAR SECCIONES
# -----------------------------------------
tab1, tab2 = st.tabs(["🚗 Vehículos", "🛠️ Mantenimiento"])

# -----------------------------------------
# TAB VEHÍCULOS
# -----------------------------------------
with tab1:
    st.subheader("Listado de Vehículos")

    ruta_veh = "data/vehiculos.csv"

    if os.path.exists(ruta_veh):
        df_veh = pd.read_csv(ruta_veh)
        st.dataframe(df_veh, use_container_width=True)
    else:
        st.warning("No existe el archivo data/vehiculos.csv")

    st.write("---")
    st.write("Aquí va TODO el contenido original de 4_Vehiculos.py")


# -----------------------------------------
# TAB MANTENIMIENTO
# -----------------------------------------
with tab2:
    st.subheader("Control de Mantenimiento")

    ruta_mant = "data/mantenimiento.csv"

    if os.path.exists(ruta_mant):
        df_mant = pd.read_csv(ruta_mant)
        st.dataframe(df_mant, use_container_width=True)
    else:
        st.warning("No existe el archivo data/mantenimiento.csv")

    st.write("---")
    st.write("Aquí va TODO el contenido original de 8_Mantenimiento.py")
