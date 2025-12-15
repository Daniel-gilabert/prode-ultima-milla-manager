import streamlit as st
import pandas as pd
from pathlib import Path
import base64
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
    dtype={"id_empleado": str, "dni": str, "telefono": str}
).fillna("")

df["telefono"] = df["telefono"].str.replace(".0", "", regex=False).str.strip()
df["id_empleado"] = df["id_empleado"].str.strip()
df["dni"] = df["dni"].str.strip()
df = df.sort_values("id_empleado").reset_index(drop=True)

# -----------------------------------------
# BUSCADOR
# -----------------------------------------
busqueda = st.text_input("🔍 Buscar empleado")

df_filtrado = df
if busqueda:
    b = busqueda.lower()
    df_filtrado = df[
        df.astype(str).apply(lambda r: r.str.lower().str.contains(b)).any(axis=1)
    ].reset_index(drop=True)

if df_filtrado.empty:
    st.warning("No se encontraron empleados.")
    st.stop()

# -----------------------------------------
# NAVEGACIÓN
# -----------------------------------------
if "idx_emp" not in st.session_state:
    st.session_state.idx_emp = 0

max_idx = len(df_filtrado) - 1
st.session_state.idx_emp = max(0, min(st.session_state.idx_emp, max_idx))

_, c1, c2, c3, c4 = st.columns([12, .6, .6, .6, .6])
with c1:
    if st.button("⏮"): st.session_state.idx_emp = 0
with c2:
    if st.button("◀") and st.session_state.idx_emp > 0: st.session_state.idx_emp -= 1
with c3:
    if st.button("▶") and st.session_state.idx_emp < max_idx: st.session_state.idx_emp += 1
with c4:
    if st.button("⏭"): st.session_state.idx_emp = max_idx

st.markdown("---")

emp = df_filtrado.iloc[st.session_state.idx_emp]
id_empleado = emp["id_empleado"]

# -----------------------------------------
# FICHA VISUAL
# -----------------------------------------
col_foto, col_datos = st.columns([1, 3])

with col_foto:
    foto_path = FOTOS_DIR / f"{id_empleado}.jpg"
    if foto_path.exists():
        st.image(str(foto_path), width=140)
    else:
        st.info("Sin foto")

with col_datos:
    st.subheader(emp["nombre"])
    st.write("ID:", emp["id_empleado"])
    st.write("DNI:", emp["dni"])
    st.write("Email:", emp["email"])
    st.write("Teléfono:", emp["telefono"])
    st.write("Puesto:", emp["puesto"])
    st.write("Ubicación:", emp["ubicacion"])
    st.write("Estado:", emp["estado"])

# -----------------------------------------
# HTML PARA IMPRESIÓN
# -----------------------------------------
def generar_html_impresion(emp, foto_path):
    foto_html = ""
    if foto_path.exists():
        img_bytes = foto_path.read_bytes()
        img_b64 = base64.b64encode(img_bytes).decode()
        foto_html = f"<img src='data:image/jpeg;base64,{img_b64}' width='120'>"

    return f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial; padding: 30px; }}
            h1 {{ border-bottom: 1px solid #ccc; }}
            .fila {{ margin-bottom: 8px; }}
        </style>
    </head>
    <body onload="window.print()">
        {foto_html}
        <h1>{emp['nombre']}</h1>
        <div class="fila"><b>ID:</b> {emp['id_empleado']}</div>
        <div class="fila"><b>DNI:</b> {emp['dni']}</div>
        <div class="fila"><b>Email:</b> {emp['email']}</div>
        <div class="fila"><b>Teléfono:</b> {emp['telefono']}</div>
        <div class="fila"><b>Puesto:</b> {emp['puesto']}</div>
        <div class="fila"><b>Ubicación:</b> {emp['ubicacion']}</div>
        <div class="fila"><b>Estado:</b> {emp['estado']}</div>
    </body>
    </html>
    """

# -----------------------------------------
# BOTÓN IMPRIMIR REAL
# -----------------------------------------
if st.button("🖨 Imprimir ficha"):
    html = generar_html_impresion(emp, foto_path)
    components.html(html, height=1)
