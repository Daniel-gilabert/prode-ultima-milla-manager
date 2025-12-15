import streamlit as st
import pandas as pd
import json
from pathlib import Path

# --------------------------------------------------
# CONFIGURACIÓN
# --------------------------------------------------
st.set_page_config(page_title="Administrar Vehículos", layout="wide")
st.title("🚗 Administrar Vehículos")
st.write("Sube el Excel de vehículos")

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

VEH_FILE = DATA_DIR / "vehiculos.json"

# --------------------------------------------------
# SUBIDA DE EXCEL
# --------------------------------------------------
archivo = st.file_uploader(
    "Sube el Excel de vehículos",
    type=["xlsx"]
)

if archivo is None:
    st.info("⬆️ Sube un archivo Excel para comenzar")
    st.stop()

# --------------------------------------------------
# LECTURA DEL EXCEL
# --------------------------------------------------
try:
    df = pd.read_excel(archivo)
except Exception as e:
    st.error("❌ Error al leer el Excel")
    st.exception(e)
    st.stop()

# --------------------------------------------------
# NORMALIZAR COLUMNAS
# --------------------------------------------------
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

# --------------------------------------------------
# COLUMNAS OBLIGATORIAS
# --------------------------------------------------
columnas_obligatorias = {
    "id_vehiculo",
    "matricula",
    "bastidor",
    "marca",
    "modelo",
    "tipo",
}

faltan = columnas_obligatorias - set(df.columns)
if faltan:
    st.error("❌ Faltan columnas obligatorias")
    st.write(list(faltan))
    st.stop()

# --------------------------------------------------
# LIMPIEZA DE DATOS
# --------------------------------------------------

# id_vehiculo → permitir vacío
df["id_vehiculo"] = (
    df["id_vehiculo"]
    .astype(str)
    .str.strip()
    .replace("", None)
)

# tipo → normalizar y validar
df["tipo"] = df["tipo"].astype(str).str.lower().str.strip()

valores_validos_tipo = {"propiedad", "renting"}
tipos_invalidos = df.loc[~df["tipo"].isin(valores_validos_tipo), "tipo"].unique()

if len(tipos_invalidos) > 0:
    st.error("❌ Valores incorrectos en columna 'tipo'")
    st.write("Solo se permite: propiedad / renting")
    st.json(tipos_invalidos.tolist())
    st.stop()

# --------------------------------------------------
# AÑADIR CAMPOS INTERNOS DEL SISTEMA
# --------------------------------------------------
df["estado"] = "OPERATIVO"               # editable luego desde ficha
df["empleado_id"] = None                 # asignación posterior
df["itv_cita_fecha"] = None
df["itv_estacion"] = None
df["seguro_aseguradora"] = None
df["seguro_poliza"] = None

# --------------------------------------------------
# MOSTRAR PREVISUALIZACIÓN
# --------------------------------------------------
st.success("✅ Excel válido")
st.dataframe(df, use_container_width=True)

# --------------------------------------------------
# GUARDAR EN JSON
# --------------------------------------------------
if st.button("💾 Guardar vehículos en el sistema"):
    try:
        vehiculos = df.to_dict(orient="records")

        with open(VEH_FILE, "w", encoding="utf-8") as f:
            json.dump(vehiculos, f, indent=2, ensure_ascii=False)

        st.success("🚗 Vehículos guardados correctamente")
        st.info("Estado inicial asignado: OPERATIVO")

    except Exception as e:
        st.error("❌ Error al guardar vehículos")
        st.exception(e)

# --------------------------------------------------
# COMPROBACIÓN
# --------------------------------------------------
if VEH_FILE.exists():
    st.success("📄 vehiculos.json EXISTE en el sistema")
else:
    st.warning("📄 vehiculos.json todavía NO existe")

