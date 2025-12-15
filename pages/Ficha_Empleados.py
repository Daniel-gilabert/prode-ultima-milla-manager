import streamlit as st
import pandas as pd
from pathlib import Path
import tempfile
from utils.pdf_empleados import generar_pdf_empleados

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
st.set_page_config(page_title="Ficha Empleados", layout="wide")

DATA_DIR = Path("data")
FOTOS_DIR = DATA_DIR / "fotos_empleados"
CSV_FILE = DATA_DIR / "empleados.csv"

st.title("📇 Ficha de Empleados")

# --------------------------------------------------
# CARGA DE DATOS
# --------------------------------------------------
if not CSV_FILE.exists():
    st.error("❌ No existe empleados.csv")
    st.stop()

df = pd.read_csv(CSV_FILE, dtype=str).fillna("")

# Normalizar tipos
df["id_empleado"] = df["id_empleado"].astype(int)
df["telefono"] = df["telefono"].str.replace(".0", "", regex=False)

# ORDENAR POR ID
df = df.sort_values("id_empleado").reset_index(drop=True)

# --------------------------------------------------
# ESTADO DE NAVEGACIÓN
# --------------------------------------------------
if "idx_emp" not in st.session_state:
    st.session_state.idx_emp = 0

total = len(df)

def ir_primero(): st.session_state.idx_emp = 0
def ir_anterior(): st.session_state.idx_emp = max(0, st.session_state.idx_emp - 1)
def ir_siguiente(): st.session_state.idx_emp = min(total - 1, st.session_state.idx_emp + 1)
def ir_ultimo(): st.session_state.idx_emp = total - 1

# --------------------------------------------------
# SELECTOR + NAVEGACIÓN
# --------------------------------------------------
col_sel, col_nav = st.columns([7, 5])

with col_sel:
    opciones = [f"{row.id_empleado} - {row.nombre}" for _, row in df.iterrows()]
    seleccion = st.selectbox(
        "Selecciona un empleado",
        range(total),
        format_func=lambda i: opciones[i],
        index=st.session_state.idx_emp
    )
    st.session_state.idx_emp = seleccion

with col_nav:
    # Empujar botones a la derecha y muy juntos
    st.markdown("<div style='text-align:right'>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([0.4, 0.4, 0.4, 0.4])
    c1.button("⏮", on_click=ir_primero)
    c2.button("◀", on_click=ir_anterior)
    c3.button("▶", on_click=ir_siguiente)
    c4.button("⏭", on_click=ir_ultimo)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# --------------------------------------------------
# EMPLEADO ACTUAL
# --------------------------------------------------
emp = df.iloc[st.session_state.idx_emp]

# --------------------------------------------------
# FICHA VISUAL
# --------------------------------------------------
col_foto, col_datos = st.columns([2, 6])

with col_foto:
    foto = FOTOS_DIR / f"{emp.id_empleado}.jpg"
    if foto.exists():
        st.image(str(foto), width=120)
    else:
        st.image("https://via.placeholder.com/120x120?text=Sin+Foto")

with col_datos:
    st.subheader(emp.nombre)

    st.markdown(f"""
🆔 **ID empleado:** {emp.id_empleado}  
🪪 **DNI:** {emp.dni}  
✉ **Email:** <a href="mailto:{emp.email}">{emp.email}</a>  
📞 **Teléfono:** <a href="tel:{emp.telefono}">{emp.telefono}</a>  
💼 **Puesto:** {emp.puesto}  
📍 **Ubicación:** {emp.ubicacion}  
✅ **Estado:** {emp.estado}
""", unsafe_allow_html=True)

st.markdown("---")

# --------------------------------------------------
# PDF INDIVIDUAL
# --------------------------------------------------
st.subheader("📄 Exportar ficha")

if st.button("📄 Generar PDF de esta ficha"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        generar_pdf_empleados(
            [emp.to_dict()],
            FOTOS_DIR,
            tmp.name
        )
        with open(tmp.name, "rb") as f:
            st.download_button(
                "⬇ Descargar PDF",
                f,
                file_name=f"Ficha_{emp.nombre}.pdf",
                mime="application/pdf"
            )

# --------------------------------------------------
# PDF MÚLTIPLE
# --------------------------------------------------
st.subheader("📑 Exportar varias fichas")

seleccionados = st.multiselect(
    "Selecciona empleados",
    [f"{row.id_empleado} - {row.nombre}" for _, row in df.iterrows()]
)

if seleccionados and st.button("📄 Generar PDF múltiple"):
    ids = [int(s.split(" - ")[0]) for s in seleccionados]
    empleados_sel = df[df["id_empleado"].isin(ids)].to_dict("records")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        generar_pdf_empleados(
            empleados_sel,
            FOTOS_DIR,
            tmp.name
        )
        with open(tmp.name, "rb") as f:
            st.download_button(
                "⬇ Descargar PDF",
                f,
                file_name="Fichas_Empleados_PRODE.pdf",
                mime="application/pdf"
            )

