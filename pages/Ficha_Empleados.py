import streamlit as st
import pandas as pd
from pathlib import Path

# -----------------------------------------
# CONFIGURACIÓN
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

df = pd.read_csv(EMP_FILE, encoding="utf-8-sig", dtype={"telefono": str})


if df.empty:
    st.warning("No hay empleados para mostrar.")
    st.stop()

df = df.sort_values("id_empleado").reset_index(drop=True)

# -----------------------------------------
# BUSCADOR
# -----------------------------------------
busqueda = st.text_input(
    "Buscar empleado (nombre, DNI, email, teléfono, puesto, ubicación...)"
)

df_filtrado = df.copy()

if busqueda:
    b = busqueda.lower()
    df_filtrado = df[
        df.astype(str)
        .apply(lambda fila: fila.str.lower().str.contains(b))
        .any(axis=1)
    ].reset_index(drop=True)

if df_filtrado.empty:
    st.warning("No se encontró ningún empleado.")
    st.stop()

# -----------------------------------------
# ESTADO DE NAVEGACIÓN
# -----------------------------------------
if "idx_emp" not in st.session_state:
    st.session_state.idx_emp = 0

max_idx = len(df_filtrado) - 1
st.session_state.idx_emp = max(0, min(st.session_state.idx_emp, max_idx))

# -----------------------------------------
# BOTONES DE NAVEGACIÓN (ULTRA COMPACTOS, DERECHA)
# -----------------------------------------
espacio, c1, c2, c3, c4 = st.columns([12, 0.6, 0.6, 0.6, 0.6])

with c1:
    if st.button("⏮", help="Primero"):
        st.session_state.idx_emp = 0

with c2:
    if st.button("◀", help="Anterior"):
        if st.session_state.idx_emp > 0:
            st.session_state.idx_emp -= 1

with c3:
    if st.button("▶", help="Siguiente"):
        if st.session_state.idx_emp < max_idx:
            st.session_state.idx_emp += 1

with c4:
    if st.button("⏭", help="Último"):
        st.session_state.idx_emp = max_idx


# -----------------------------------------
# EMPLEADO ACTUAL
# -----------------------------------------
emp = df_filtrado.iloc[st.session_state.idx_emp]
id_empleado = int(emp["id_empleado"])

# -----------------------------------------
# LAYOUT
# -----------------------------------------
col_foto, col_datos = st.columns([1, 3])

# ---------- FOTO ----------
with col_foto:
    foto_jpg = FOTOS_DIR / f"{id_empleado}.jpg"
    foto_png = FOTOS_DIR / f"{id_empleado}.png"

    if foto_jpg.exists():
        st.image(str(foto_jpg), width=150)
    elif foto_png.exists():
        st.image(str(foto_png), width=150)
    else:
        st.info("Sin foto")

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
# INFO RELACIONADA (FUTURO)
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




