import streamlit as st
import pandas as pd
from pathlib import Path

# -----------------------------------------
# CONFIGURACIÓN
# -----------------------------------------
st.set_page_config(layout="wide")
st.title("Ficha de Empleado")
st.info(
    "Zona de consulta central. Desde aquí se accede a toda la información "
    "relacionada con un empleado."
)

# -----------------------------------------
# RUTAS
# -----------------------------------------
BASE = Path.cwd()
DATA = BASE / "data"
EMP_FILE = DATA / "empleados.csv"
FOTOS_DIR = DATA / "fotos_empleados"

# -----------------------------------------
# CARGA DE EMPLEADOS
# -----------------------------------------
if not EMP_FILE.exists():
    st.error("No hay empleados cargados todavía.")
    st.stop()

df = pd.read_csv(EMP_FILE, encoding="utf-8-sig")

if df.empty:
    st.warning("El archivo de empleados está vacío.")
    st.stop()

# -----------------------------------------
# BUSCADOR GLOBAL
# -----------------------------------------
st.subheader("Buscar empleado")

busqueda = st.text_input(
    "Busca por nombre, DNI, email, teléfono, puesto, ubicación, estado o ID",
    placeholder="Escribe cualquier dato del empleado..."
)

df_busqueda = df.copy()

if busqueda:
    busqueda_lower = busqueda.lower()

    df_busqueda = df[
        df.astype(str)
        .apply(lambda fila: fila.str.lower().str.contains(busqueda_lower))
        .any(axis=1)
    ]

if df_busqueda.empty:
    st.warning("No se encontraron empleados con ese criterio.")
    st.stop()

# -----------------------------------------
# SELECTOR DE EMPLEADO (FILTRADO)
# -----------------------------------------
df_busqueda["selector"] = (
    df_busqueda["id_empleado"].astype(str)
    + " - "
    + df_busqueda["nombre"]
)

empleado_sel = st.selectbox(
    "Selecciona un empleado",
    df_busqueda["selector"].tolist()
)

id_empleado = int(empleado_sel.split(" - ")[0])
emp = df[df["id_empleado"] == id_empleado].iloc[0]

st.markdown("---")

# -----------------------------------------
# LAYOUT FICHA
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
# ZONA CENTRAL DEL EMPLEADO (FUTURO)
# -----------------------------------------
st.header("Información relacionada")

with st.expander("🚚 Vehículo asignado"):
    st.info("Aquí se mostrará el vehículo del empleado.")

with st.expander("📌 Servicios"):
    st.info("Aquí se mostrarán los servicios relacionados.")

with st.expander("📦 EPIs"):
    st.info("Aquí se mostrarán los EPIs entregados.")

with st.expander("📄 Documentación"):
    st.info("Aquí se mostrará la documentación del empleado.")




