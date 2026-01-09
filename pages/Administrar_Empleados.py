import streamlit as st
import pandas as pd
import json
from pathlib import Path

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
st.set_page_config(page_title="Administrar Empleados", layout="wide")

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

EMP_JSON = DATA_DIR / "empleados.json"

# --------------------------------------------------
# FUNCIONES
# --------------------------------------------------
def guardar_empleados_json(df: pd.DataFrame):
    empleados = []

    for _, row in df.iterrows():
        empleados.append({
            "id_empleado": int(row["id_empleado"]),
            "nombre": str(row["nombre"]).strip(),
            "dni": None if pd.isna(row.get("dni")) else str(row.get("dni")),
            "email": None if pd.isna(row.get("email")) else str(row.get("email")),
            "telefono": None if pd.isna(row.get("telefono")) else str(row.get("telefono")),
            "puesto": None if pd.isna(row.get("puesto")) else str(row.get("puesto")),
            "ubicacion": None if pd.isna(row.get("ubicacion")) else str(row.get("ubicacion")),
            "estado": str(row.get("estado", "activo")).lower()
        })

    EMP_JSON.write_text(
        json.dumps(empleados, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

def validar_columnas(df: pd.DataFrame):
    obligatorias = ["id_empleado", "nombre"]
    faltan = [c for c in obligatorias if c not in df.columns]
    return faltan

# --------------------------------------------------
# UI
# --------------------------------------------------
st.title("👥 Administrar Empleados")
st.caption("Carga masiva de empleados desde Excel")

uploaded = st.file_uploader(
    "📤 Sube el Excel de empleados",
    type=["xlsx"]
)

if uploaded:
    try:
        df = pd.read_excel(uploaded)

        # Limpieza básica
        df.columns = df.columns.str.strip().str.lower()

        faltan = validar_columnas(df)
        if faltan:
            st.error(f"❌ Faltan columnas obligatorias: {', '.join(faltan)}")
            st.stop()

        # Conversión id_empleado
        df["id_empleado"] = pd.to_numeric(df["id_empleado"], errors="coerce")

        if df["id_empleado"].isna().any():
            st.error("❌ Hay valores no numéricos en id_empleado")
            st.stop()

        df["id_empleado"] = df["id_empleado"].astype(int)

        st.success("✅ Excel válido")

        st.subheader("📋 Vista previa")
        st.dataframe(df, use_container_width=True)

        if st.button("💾 Guardar empleados en el sistema"):
            guardar_empleados_json(df)
            st.success("✅ Empleados guardados correctamente en data/empleados.json")

            if EMP_JSON.exists():
                st.info("📄 empleados.json EXISTE en el sistema")

    except Exception as e:
        st.error("❌ Error al procesar el Excel")
        st.exception(e)

# --------------------------------------------------
# INFO ESTADO ACTUAL
# --------------------------------------------------
st.divider()
st.subheader("📂 Estado actual del sistema")

if EMP_JSON.exists():
    try:
        empleados = json.loads(EMP_JSON.read_text(encoding="utf-8"))
        st.success(f"👤 Empleados cargados en sistema: {len(empleados)}")
    except:
        st.warning("⚠️ empleados.json existe pero no se puede leer")
else:
    st.warning("⚠️ No existe data/empleados.json todavía")

