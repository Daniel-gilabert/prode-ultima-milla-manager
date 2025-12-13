import streamlit as st
import pandas as pd
from pathlib import Path

# -----------------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# -----------------------------------------
st.set_page_config(layout="wide")
st.title("Ficha de Empleado")
st.info("Zona de consulta. Aquí se visualiza la información completa del empleado.")

# -----------------------------------------
# RUTAS
# -----------------------------------------
BASE = Path.cwd()
DATA = BASE / "data"
EMP_FILE = DATA / "empleados.csv"
FOTOS_DIR = DATA / "fotos_empleados"

# -----------------------------------------
# COMPROBACIONES
# -----------------------------------------
if not EMP_FILE.exists():
    st.error("No hay empleados cargados todavía.")
    st.stop()

df = pd.read_csv(EMP_FILE, encoding="utf-8-sig")

if df.empty:
    st.warning("El archivo de empleados está vacío.")
    st.stop()

# -----------------------------------------
# SELECTOR DE EMPLEADO
# -----------------------------------------
df["selector"] = df["id_empleado"].astype(str) + " - " + df["nombre"]

empleado_sel = st.selectbox(
    "Selecciona un empleado",
    df["selector"].tolist()
)

id_empleado = int(empleado_sel.split(" - ")[0])
emp = df[df["id_empleado"] == id_empleado].iloc[0]

st.markdown("---")

# -----------------------------------------
# LAYOUT PRINCIPAL
# -----------------------------------------
col_foto, col_datos = st.columns([1, 2])

# ---------- FOTO ----------
with col_foto:
    foto = FOTOS_DIR / f"{id_empleado}.jpg"

    if foto.exists():
        st.image(str(foto), use_container_width=True)
    else:
        st.info("Sin foto disponible")

# ---------- DATOS ----------
with col_datos:
    st.subheader(emp["nombre"])

    st.write("**ID empleado:**", emp["id_empleado"])
    st.write("**DNI:**", emp["dni"])
    st.write("**Email:**", emp["email"])
    st.write("**Teléfono:**", emp["telefono"])
    st.write("**Puesto:**", emp["puesto"])
    st.write("**Ubicación:**", emp["ubicacion"])
    st.write("**Estado:**", emp["estado"])

st.markdown("---")

# -----------------------------------------
# SECCIÓN FUTURA (PREPARADA PARA CRECER)
# -----------------------------------------
with st.expander("Información adicional (próximamente)"):
    st.write("- Vehículo asignado")
    st.write("- EPIs entregados")
    st.write("- Historial de ausencias")
    st.write("- Documentación")


