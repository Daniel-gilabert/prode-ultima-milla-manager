import streamlit as st
import pandas as pd
from pathlib import Path

# -----------------------------------------
# CONFIG
# -----------------------------------------
DATA_FILE = Path("data/empleados.json")
FOTOS_DIR = Path("data/fotos_empleados")

st.title("👤 Ficha de Empleados")

# -----------------------------------------
# CARGA SEGURA DE DATOS
# -----------------------------------------
if not DATA_FILE.exists() or DATA_FILE.stat().st_size == 0:
    st.warning("⚠️ No hay empleados cargados en el sistema.")
    st.stop()

try:
    df = pd.read_json(DATA_FILE)
except ValueError:
    st.error("❌ El archivo empleados.json está corrupto.")
    st.stop()

df = df.fillna("")

if "id_empleado" not in df.columns:
    st.error("❌ Falta la columna id_empleado.")
    st.stop()

df["id_empleado"] = df["id_empleado"].astype(int)

# -----------------------------------------
# SELECTOR DE EMPLEADO
# -----------------------------------------
df["label"] = df["nombre"] + " (" + df["dni"] + ")"

empleado_sel = st.selectbox(
    "Selecciona un empleado",
    df["label"].tolist()
)

empleado = df[df["label"] == empleado_sel].iloc[0]

# -----------------------------------------
# MODO EDICIÓN
# -----------------------------------------
if "editando_empleado" not in st.session_state:
    st.session_state.editando_empleado = False

# -----------------------------------------
# VISTA NORMAL (FICHA)
# -----------------------------------------
if not st.session_state.editando_empleado:

    col_foto, col_info = st.columns([1, 3])

    with col_foto:
        foto_path = FOTOS_DIR / f"{empleado['id_empleado']}.jpg"
        if foto_path.exists():
            st.image(str(foto_path), width=160)
        else:
            st.info("📷 Sin foto")

    with col_info:
        st.markdown(f"## {empleado['nombre']}")
        st.write(f"**DNI:** {empleado['dni']}")
        st.write(f"**Email:** {empleado['email']}")
        st.write(f"**Teléfono:** {empleado['telefono']}")
        st.write(f"**Puesto:** {empleado['puesto']}")
        st.write(f"**Ubicación:** {empleado['ubicacion']}")
        st.write(f"**Estado:** {empleado['estado']}")

    st.divider()

    # -------- BOTÓN EDITAR --------
    if st.session_state.get("rol") == "admin":
        if st.button("✏️ Editar ficha del empleado"):
            st.session_state.editando_empleado = True
            st.rerun()

# -----------------------------------------
# MODO EDICIÓN
# -----------------------------------------
else:
    st.subheader("✏️ Editar ficha del empleado")

    with st.form("form_editar_empleado"):

        nombre = st.text_input("Nombre", empleado["nombre"])
        dni = st.text_input("DNI", empleado["dni"])
        email = st.text_input("Email", empleado["email"])
        telefono = st.text_input("Teléfono", empleado["telefono"])
        puesto = st.text_input("Puesto", empleado["puesto"])
        ubicacion = st.text_input("Ubicación", empleado["ubicacion"])
        estado = st.selectbox(
            "Estado",
            ["activo", "baja", "vacaciones"],
            index=["activo", "baja", "vacaciones"].index(empleado["estado"])
            if empleado["estado"] in ["activo", "baja", "vacaciones"] else 0
        )

        col1, col2 = st.columns(2)

        with col1:
            guardar = st.form_submit_button("💾 Guardar cambios")

        with col2:
            cancelar = st.form_submit_button("❌ Cancelar")

    # -------- GUARDAR --------
    if guardar:
        df.loc[df["id_empleado"] == empleado["id_empleado"], [
            "nombre", "dni", "email", "telefono",
            "puesto", "ubicacion", "estado"
        ]] = [
            nombre, dni, email, telefono,
            puesto, ubicacion, estado
        ]

        df.drop(columns=["label"], errors="ignore") \
          .to_json(DATA_FILE, orient="records", indent=2, force_ascii=False)

        st.success("✅ Ficha actualizada correctamente")
        st.session_state.editando_empleado = False
        st.rerun()

    # -------- CANCELAR --------
    if cancelar:
        st.session_state.editando_empleado = False
        st.rerun()

