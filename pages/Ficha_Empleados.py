import streamlit as st
import pandas as pd
from pathlib import Path

# -----------------------------------------
# CONFIGURACIÓN
# -----------------------------------------
st.set_page_config(
    page_title="Ficha de Empleados",
    layout="wide"
)

CSV_FILE = Path("data/empleados.csv")

# -----------------------------------------
# CARGA ROBUSTA DE EMPLEADOS
# -----------------------------------------
def cargar_empleados():
    if not CSV_FILE.exists():
        return pd.DataFrame()

    # Intentos progresivos: encoding + separador
    for encoding in ["utf-8-sig", "latin1"]:
        for sep in [",", ";"]:
            try:
                df = pd.read_csv(
                    CSV_FILE,
                    dtype=str,
                    encoding=encoding,
                    sep=sep,
                    engine="python"
                ).fillna("")
                return df
            except Exception:
                pass

    st.error("❌ No se pudo leer empleados.csv. El archivo tiene un formato inválido.")
    return pd.DataFrame()

df = cargar_empleados()

# -----------------------------------------
# UI
# -----------------------------------------
st.title("🗂️ Ficha de Empleados")

if df.empty:
    st.warning("⚠️ No hay empleados cargados en el sistema.")
    st.stop()

# Normalizar columnas (por si vienen con nombres raros)
df.columns = [c.strip().lower() for c in df.columns]

# Columnas esperadas mínimas
COLUMNAS_MINIMAS = ["id", "nombre"]

for col in COLUMNAS_MINIMAS:
    if col not in df.columns:
        st.error(f"❌ Falta la columna obligatoria: {col}")
        st.stop()

# -----------------------------------------
# SELECTOR DE EMPLEADO
# -----------------------------------------
df = df.sort_values("id")

opciones = [
    f'{row["id"]} - {row["nombre"]}'
    for _, row in df.iterrows()
]

if "empleado_index" not in st.session_state:
    st.session_state.empleado_index = 0

col_sel, col_prev, col_next = st.columns([8, 1, 1])

with col_sel:
    seleccionado = st.selectbox(
        "Selecciona un empleado",
        opciones,
        index=st.session_state.empleado_index
    )

with col_prev:
    if st.button("◀"):
        st.session_state.empleado_index = max(
            0, st.session_state.empleado_index - 1
        )
        st.rerun()

with col_next:
    if st.button("▶"):
        st.session_state.empleado_index = min(
            len(opciones) - 1,
            st.session_state.empleado_index + 1
        )
        st.rerun()

st.session_state.empleado_index = opciones.index(seleccionado)

empleado = df.iloc[st.session_state.empleado_index]

# -----------------------------------------
# FICHA DEL EMPLEADO
# -----------------------------------------
st.divider()

col_img, col_info = st.columns([2, 6])

with col_img:
    foto = Path(f"data/fotos_empleados/{empleado['id']}.jpg")
    if foto.exists():
        st.image(str(foto), use_container_width=True)
    else:
        st.info("Empleado sin foto")

with col_info:
    st.markdown(
        f"""
        <h2 style="margin-bottom:0">{empleado['nombre']}</h2>
        <p style="color:gray">ID empleado: {empleado['id']}</p>
        """,
        unsafe_allow_html=True
    )

    for campo in df.columns:
        if campo in ["id", "nombre"]:
            continue
        valor = empleado[campo]
        if valor:
            st.markdown(f"**{campo.capitalize()}**: {valor}")

st.divider()

# -----------------------------------------
# INFO FINAL
# -----------------------------------------
st.caption(
    f"Total empleados cargados en sistema: {len(df)}"
)
