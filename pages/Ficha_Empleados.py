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

st.title("🗂️ Ficha de Empleados")

# --------------------------------------------------
# CARGA DE DATOS
# --------------------------------------------------
if not CSV_FILE.exists():
    st.error("❌ No existe empleados.csv")
    st.stop()

df = pd.read_csv(CSV_FILE, dtype=str).fillna("")

df["id_empleado"] = df["id_empleado"].astype(int)

# Limpiar teléfono → SOLO números
df["telefono"] = (
    df["telefono"]
    .str.replace(".0", "", regex=False)
    .str.replace(" ", "", regex=False)
)

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
# SELECTOR + BOTONES (MUY JUNTOS Y A LA DERECHA)
# --------------------------------------------------
col_sel, col_nav = st.columns([8, 4])

with col_sel:
    opciones = [f"{r.id_empleado} - {r.nombre}" for _, r in df.iterrows()]
    seleccion = st.selectbox(
        "Selecciona un empleado",
        range(total),
        format_func=lambda i: opciones[i],
        index=st.session_state.idx_emp
    )
    st.session_state.idx_emp = seleccion

with col_nav:
    b1, b2, b3, b4 = st.columns([0.2, 0.2, 0.2, 0.2])
    b1.button("⏮", on_click=ir_primero)
    b2.button("◀", on_click=ir_anterior)
    b3.button("▶", on_click=ir_siguiente)
    b4.button("⏭", on_click=ir_ultimo)

st.markdown("---")

# --------------------------------------------------
# EMPLEADO ACTUAL
# --------------------------------------------------
emp = df.iloc[st.session_state.idx_emp]

telefono_tel = emp.telefono
if telefono_tel and not telefono_tel.startswith("34"):
    telefono_tel = "34" + telefono_tel

# --------------------------------------------------
# FICHA VISUAL
# --------------------------------------------------
col_foto, col_datos = st.columns([2, 6])

with col_foto:
    foto = FOTOS_DIR / f"{emp.id_empleado}.jpg"
    if foto.exists():
        st.image(str(foto), width=110)
    else:
        st.image("https://via.placeholder.com/110x110?text=Sin+Foto")

with col_datos:
    st.subheader(emp.nombre)

    st.markdown(f"""
🆔 **ID empleado:** {emp.id_empleado}  
🪪 **DNI:** {emp.dni}  
✉ **Email:** <a href="mailto:{emp.email}">{emp.email}</a>  
📞 **Teléfono:** {emp.telefono}
&nbsp;&nbsp;
<a href="tel:+{telefono_tel}">📞 Llamar</a>
&nbsp;&nbsp;
<a href="https://wa.me/{telefono_tel}" target="_blank">💬 WhatsApp</a>

💼 **Puesto:** {emp.puesto}  
📍 **Ubicación:** {emp.ubicacion}  
✅ **Estado:** {emp.estado}
""", unsafe_allow_html=True)

st.markdown("---")

# --------------------------------------------------
# EXPORTAR PDF (SOLO ESTA FICHA)
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
# SECCIONES FUTURAS (YA PREPARADAS)
# --------------------------------------------------
st.markdown("---")
st.subheader("🧰 EPIs del empleado")
st.info("Próximamente: EPIs asociados a este empleado")

st.subheader("🚗 Vehículos asignados")
st.info("Próximamente: vehículos vinculados al empleado")

st.subheader("📋 Servicios")
st.info("Próximamente: servicios realizados por el empleado")

