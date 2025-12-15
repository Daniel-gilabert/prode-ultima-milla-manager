import streamlit as st
import pandas as pd
from pathlib import Path

# --------------------------------------------------
# CONFIGURACIÓN
# --------------------------------------------------
st.set_page_config(page_title="Administrar Vehículos", layout="wide")
st.title("🚗 Administrar Vehículos")

DATA_DIR = Path("data")
CSV_VEH = DATA_DIR / "vehiculos.csv"
CSV_ESTADO = DATA_DIR / "estado_vehiculos.csv"

# --------------------------------------------------
# COLUMNAS OBLIGATORIAS (EXCEL DEFINITIVO)
# --------------------------------------------------
COLUMNAS_OBLIGATORIAS = [
    "id_vehiculo",
    "matricula",
    "bastidor",
    "marca",
    "modelo",
    "tipo",                   # propiedad / renting
    "itv_vigente_hasta",
    "seguro_vigente_hasta",
    "aseguradora",
    "poliza",
]

# --------------------------------------------------
# SUBIDA DE EXCEL
# --------------------------------------------------
archivo = st.file_uploader(
    "📥 Sube el Excel de vehículos",
    type=["xlsx"]
)

if archivo:
    try:
        df = pd.read_excel(archivo, dtype=str)

        # Normalizar columnas
        df.columns = (
            df.columns.str.lower()
            .str.strip()
            .str.replace(" ", "_")
        )

        faltan = set(COLUMNAS_OBLIGATORIAS) - set(df.columns)

        if faltan:
            st.error("❌ El Excel NO es válido")
            st.write("Faltan estas columnas obligatorias:")
            st.write(list(faltan))
            st.stop()

        # Limpiar datos
        df = df[COLUMNAS_OBLIGATORIAS].fillna("")

        df["id_vehiculo"] = df["id_vehiculo"].astype(int)
        df["matricula"] = df["matricula"].str.upper().str.strip()
        df["tipo"] = df["tipo"].str.lower().str.strip()

        # Validar tipo
        tipos_validos = {"propiedad", "renting"}
        tipos_erroneos = set(df["tipo"]) - tipos_validos
        if tipos_erroneos:
            st.error("❌ Valores incorrectos en columna 'tipo'")
            st.write("Solo se permite: propiedad / renting")
            st.write(list(tipos_erroneos))
            st.stop()

        st.success("✅ Excel válido")
        st.dataframe(df, use_container_width=True)

        # --------------------------------------------------
        # GUARDAR
        # --------------------------------------------------
        if st.button("💾 Guardar vehículos en el sistema"):
            DATA_DIR.mkdir(exist_ok=True)

            # Guardar vehículos
            df.to_csv(CSV_VEH, index=False, encoding="utf-8-sig")

            # Inicializar estado si no existe
            if not CSV_ESTADO.exists():
                df_estado = pd.DataFrame({
                    "id_vehiculo": df["id_vehiculo"],
                    "estado": ["operativo"] * len(df)
                })
                df_estado.to_csv(CSV_ESTADO, index=False, encoding="utf-8-sig")

            st.success("🚗 Vehículos guardados correctamente")
            st.info("Estado inicial asignado: OPERATIVO")

    except Exception as e:
        st.error("❌ Error al procesar el Excel")
        st.exception(e)
else:
    st.info("⬆️ Sube el Excel para comenzar")


