import streamlit as st
import pandas as pd
import os

st.title("Empleados")

archivo = st.file_uploader(
    "Sube el Excel de empleados",
    type=["xlsx"]
)

if archivo:
    df = pd.read_excel(archivo)

    columnas_correctas = [
        "id_empleado", "nombre", "dni", "email",
        "telefono", "puesto", "ubicacion", "estado"
    ]

    if list(df.columns) != columnas_correctas:
        st.error("❌ El Excel no tiene las columnas correctas")
        st.write("Columnas esperadas:")
        st.write(columnas_correctas)
    else:
        st.success("✅ Excel válido")
        st.dataframe(df, use_container_width=True)

        if st.button("Guardar empleados en el sistema"):
            os.makedirs("data", exist_ok=True)
            df.to_csv("data/empleados.csv", index=False, encoding="utf-8-sig")
            st.success("✅ Empleados cargados correctamente")
