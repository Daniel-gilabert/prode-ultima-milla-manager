import streamlit as st
import pandas as pd
from pathlib import Path
import streamlit.components.v1 as components

# -----------------------------------------
# CONFIGURACIÓN
# -----------------------------------------
st.set_page_config(layout="wide")
st.title("👤 Ficha de Empleado")

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

# -----------------------------------------
# CARGA DE DATOS (BLINDADA)
# -----------------------------------------
df = pd.read_csv(
    EMP_FILE,
    encoding="utf-8-sig",
    dtype={
        "id_empleado": str,
        "dni": str,
        "telefono": str
    }
).fillna("")

df["telefono"] = (
    df["telefono"]
    .astype(str)
    .str.replace(".0", "", regex=False)
    .str.strip()
)

df["id_empleado"] = df["id_empleado"].str.strip()
df["dni"] = df["dni"].str.strip()

df = df.sort_values("id_empleado").reset_index(drop=True)

# -----------------------------------------
# BUSCADOR GLOBAL
# -----------------------------------------
busqueda = st.text_input(
    "🔍 Buscar empleado (nombre, DNI, email, teléfono, puesto, ubicación...)"
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
# BOTONES DE NAVEGACIÓN (ULTRA COMPACTOS)
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

st.markdown("---")

# -----------------------------------------
# EMPLEADO ACTUAL
# -----------------------------------------
emp = df_filtrado.iloc[st.session_state.idx_emp]
id_empleado = emp["id_empleado"]

# -----------------------------------------
# LAYOUT
# -----------------------------------------
col_foto, col_datos = st.columns([1, 3])

# ---------- FOTO ----------
with col_foto:
    foto_jpg = FOTOS_DIR / f"{id_empleado}.jpg"
    foto_png = FOTOS_DIR / f"{id_empleado}.png"

    if foto_jpg.exists():
        st.image(str(foto_jpg), width=140)
    elif foto_png.exists():
        st.image(str(foto_png), width=140)
    else:
        st.info("Sin foto")

# ---------- DATOS ----------
with col_datos:
    st.subheader(emp["nombre"])

    st.markdown(f"**🆔 ID empleado:** {emp['id_empleado']}")
    st.markdown(f"**🪪 DNI:** {emp['dni']}")

    # EMAIL
    if emp["email"]:
        st.markdown(
            f"**✉️ Email:** <a href='mailto:{emp['email']}'>{emp['email']}</a>",
            unsafe_allow_html=True
        )

    # TELÉFONO + WHATSAPP
    if emp["telefono"]:
        tel = emp["telefono"]
        st.markdown(
            f"""
            **📞 Teléfono:** 
            <a href='tel:{tel}'>{tel}</a>
            &nbsp;&nbsp;|&nbsp;&nbsp;
            <a href='https://wa.me/34{tel}' target='_blank'>💬 WhatsApp</a>
            """,
            unsafe_allow_html=True
        )

    st.markdown(f"**💼 Puesto:** {emp['puesto']}")
    st.markdown(f"**📍 Ubicación:** {emp['ubicacion']}")
    st.markdown(f"**✅ Estado:** {emp['estado']}")

    # -----------------------------------------
    # BOTÓN IMPRIMIR (VISTA PREVIA REAL)
    # -----------------------------------------
    components.html(
        """
        <div style="margin-top:12px;">
            <button onclick="window.print()" style="
                padding:6px 14px;
                border-radius:6px;
                border:1px solid #ccc;
                background:#f5f5f5;
                cursor:pointer;
                font-size:14px;
            ">
                🖨 Imprimir ficha
            </button>
        </div>
        """,
        height=60
    )

st.markdown("---")

# -----------------------------------------
# INFORMACIÓN RELACIONADA
# -----------------------------------------
st.header("📂 Información relacionada")

with st.expander("🚚 Vehículo asignado"):
    st.info("Aquí se mostrará el vehículo asignado al empleado.")

with st.expander("📦 EPIs"):
    st.info("Listado de EPIs entregados y pendientes.")

with st.expander("📌 Servicios"):
    st.info("Servicios en los que ha participado el empleado.")

with st.expander("📄 Documentación"):
    st.info("Contratos, reconocimientos médicos, certificados, etc.")








