import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Administrar Vehículos", layout="wide")
st.title("🚗 Administrar Vehículos")

archivo = st.file_uploader(
    "Sube el Excel de vehículos",
    type=["xlsx"]
)

if archivo:
    df = pd.read_excel(archivo)

    # Normalizar columnas
    df.columns = (
        df.columns.str.lower()
        .str.strip()
        .str.replace(" ", "_")
    )

    columnas_ok = {
        "id_vehiculo",
        "matricula",
        "marca",
        "modelo",
        "estado",
        "itv",
        "seguro"
    }

    faltan = columnas_ok - set(df.columns)

    if faltan:
        st.error(f"❌ Faltan columnas: {list(faltan)}")
    else:
        st.success("✅ Excel válido")
        st.dataframe(df, use_container_width=True)

        if st.button("Guardar vehículos"):
            os.makedirs("data", exist_ok=True)
            df[list(columnas_ok)].to_csv(
                "data/vehiculos.csv",
                index=False,
                encoding="utf-8-sig"
            )
            st.success("🚗 Vehículos guardados correctamente")

