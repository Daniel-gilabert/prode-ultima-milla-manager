import streamlit as st
import pandas as pd
from utils.storage import load_json, save_json

DATA_PATH = "data/empleados.json"

st.title("🛠️ Administrar Empleados")

empleados = load_json(DATA_PATH, [])

st.success(f"Hay {len(empleados)} empleados guardados en el sistema.")

st.info(
    "Los empleados NO se borran al cerrar la app.\n\n"
    "Solo cambiarán si subes un nuevo Excel y confirmas que quieres sobrescribir."
)

st.markdown("---")

st.subheader("📥 Cargar empleados desde Excel")

archivo = st.file_uploader(
    "Sube el Excel de empleados",
    type=["xlsx"],
    help="Este Excel sustituirá completamente los empleados actuales"
)

if archivo:
    df = pd.read_excel(archivo).fillna("")

    if st.checkbox("Confirmo que quiero sobrescribir los empleados actuales"):
        empleados = df.to_dict(orient="records")
        save_json(DATA_PATH, empleados)
        st.success("✅ Empleados guardados correctamente")
        st.rerun()
    else:
        st.warning("Debes confirmar para sobrescribir los datos")

st.markdown("---")

st.subheader("👥 Empleados actualmente guardados")

if empleados:
    st.dataframe(pd.DataFrame(empleados), use_container_width=True)
else:
    st.warning("No hay empleados guardados todavía")
