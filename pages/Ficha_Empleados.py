


import streamlit as st
import pandas as pd
from pathlib import Path

# -----------------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# -----------------------------------------
st.set_page_config(layout="wide")
st.title("Ficha de Empleado")

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
    st.error("No hay empleados cargados.")
    st.stop()

df = pd.read_csv(EMP_FILE, encoding="utf-8-sig")

if df.empty:
    st.warning("No hay empleados para mostrar.")
    st.stop()

# -----------------------------------------
# BUSCADOR GLOBAL
# -----------------------------------------
busqueda = st.text_input(
    "Buscar empleado (nombre, DNI, email, teléfono, puesto, ubicación...)"
)

if busqueda:
    busqueda = busqueda.lower()
    df = df[
        df.astype(str)
        .apply(lambda fila: fila.str.lower().str.contains(busqueda))
        .any(axis=1)
    ]

if df.empty:
    st.warning("No se encontró ningún empleado.")
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
# LAYOUT EN COLUMNAS
# -----------------------------------------
col_foto, col_datos = st.columns([1, 3])

# ---------- FOTO (MUY COMPACTA) ----------
with col_foto:
    foto_jpg = FOTOS_DIR / f"{id_empleado}.jpg"
    foto_png = FOTOS_DIR / f"{id_empleado}.png"

    if foto_jpg.exists():
        st.image(str(foto_jpg), width=150)
    elif foto_png.exists():
        st.image(str(foto_png), width=150)
    else:
        st.info("Sin foto")

# ---------- DATOS DEL EMPLEADO ----------
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
# ZONA CENTRAL (PARA CRECER)
# -----------------------------------------
st.header("Información relacionada")

with st.expander("🚚 Vehículo asignado"):
    st.info("Pendiente de implementar")

with st.expander("📦 EPIs"):
    st.info("Pendiente de implementar")

with st.expander("📌 Servicios"):
    st.info("Pendiente de implementar")

with st.expander("📄 Documentación"):
    st.info("Pendiente de implementar")
