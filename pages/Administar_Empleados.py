
import streamlit as st
import pandas as pd
import os

# -----------------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# -----------------------------------------
st.title("Empleados")
st.write("Sube el Excel de empleados")

# -----------------------------------------
# SUBIDA DE ARCHIVO
# -----------------------------------------
archivo = st.file_uploader(
    "Sube el Excel de empleados",
    type=["xlsx"]
)

if archivo is not None:
    try:
        # Leer Excel
        df = pd.read_excel(archivo)

        # -----------------------------------------
        # NORMALIZAR NOMBRES DE COLUMNAS
        # -----------------------------------------
        df.columns = (
            df.columns
            .str.lower()
            .str.strip()
            .str.replace("á", "a")
            .str.replace("é", "e")
            .str.replace("í", "i")
            .str.replace("ó", "o")
            .str.replace("ú", "u")
            .str.replace(" ", "_")
        )

        # -----------------------------------------
        # COLUMNAS OBLIGATORIAS
        # -----------------------------------------
        columnas_obligatorias = {
    "id_empleado",
    "nombre",
    "dni",
    "email",
    "telefono",
    "puesto",
    "ubicacion",
    "estado",
    "url_foto",  
}


        columnas_excel = set(df.columns)

        faltan = columnas_obligatorias - columnas_excel
        sobran = columnas_excel - columnas_obligatorias

        if faltan:
            st.error("❌ El Excel NO es válido")
            st.write("Faltan estas columnas obligatorias:")
            st.write(list(faltan))
        else:
            st.success("✅ Excel válido")

            # Mostrar datos
            st.dataframe(df, use_container_width=True)

            if sobran:
                st.warning("⚠️ Columnas extra detectadas (se ignorarán)")
                st.write(list(sobran))

            # -----------------------------------------
            # BOTÓN DE GUARDADO
            # -----------------------------------------
            if st.button("Guardar empleados en el sistema"):
                try:
                    os.makedirs("data", exist_ok=True)
                    ruta = os.path.join("data", "empleados.csv")

                    df[list(columnas_obligatorias)].to_csv(
                        ruta,
                        index=False,
                        encoding="utf-8-sig"
                    )

                    st.success("✅ Empleados guardados correctamente")
                    st.info(f"Archivo creado en: {ruta}")

                except Exception as e:
                    st.error("❌ Error al guardar el archivo")
                    st.exception(e)

            # -----------------------------------------
            # COMPROBACIÓN (DEBUG VISUAL)
            # -----------------------------------------
            if os.path.exists("data/empleados.csv"):
                st.success("📄 empleados.csv EXISTE en el sistema")
            else:
                st.warning("📄 empleados.csv todavía NO existe")

    except Exception as e:
        st.error("❌ Error al leer el Excel")
        st.exception(e)

else:
    st.info("⬆️ Sube un archivo Excel para comenzar")
