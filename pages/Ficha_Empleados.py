import streamlit as st
import pandas as pd
from pathlib import Path

st.title("👤 Ficha de Empleados")

DATA_FILE = Path("data/empleados.json")
FOTOS_DIR = Path("data/fotos_empleados")

# -----------------------------------------
# ESTADO
# -----------------------------------------
if "modo_edicion" not in st.session_state:
    st.session_state["modo_edicion"] = False

# -----------------------------------------
# CARGA DATOS
# -----------------------------------------
if not DATA_FILE.exists():
    st.warning("No hay empleados cargados.")
    st.stop()

df = pd.read_json(DATA_FILE).fillna("")
df["id_empleado"] = df["id_empleado"].astype(int)

# -----------------------------------------
# SELECCIÓN EMPLEADO
# -----------------------------------------
st.subheader("Selecciona un empleado")

opciones = {
    f"{row['nombre']} ({row['dni']})": row["id_empleado"]
    for _, row in df.iterrows()
}

label = st.selectbox("Empleado", list(opciones.keys()))
id_empleado = opciones[label]

empleado = df[df["id_empleado"] == id_empleado].iloc[0]

st.divider()

# -----------------------------------------
# BOTÓN EDITAR (SOLO ADMIN)
# -----------------------------------------
if st.session_state.get("rol") == "admin":
    if not st.session_state["modo_edicion"]:
        if st.button("✏️ Editar datos"):
            st.session_state["modo_edicion"] = True
            st.rerun()

# -----------------------------------------
# MODO EDICIÓN
# -----------------------------------------
if st.session_state["modo_edicion"]:

    st.subheader("✏️ Editar ficha del empleado")

    with st.form("editar_empleado"):
        nombre = st.text_input("Nombre", empleado["nombre"])
        dni = st.text_input("DNI", empleado["dni"])
        email = st.text_input("Email", empleado["email"])
        telefono = st.text_input("Teléfono", empleado["telefono"])
        puesto = st.text_input("Puesto", empleado["puesto"])
        ubicacion = st.text_input("Ubicación", empleado["ubicacion"])
        estado = st.selectbox(
            "Estado",
            ["activo", "baja"],
            index=0 if empleado["estado"] == "activo" else 1
        )
        observaciones = st.text_area(
            "Observaciones",
            empleado.get("observaciones", "")
        )

        guardar = st.form_submit_button("💾 Guardar cambios")
        cancelar = st.form_submit_button("❌ Cancelar")

    if cancelar:
        st.session_state["modo_edicion"] = False
        st.rerun()

    if guardar:
        df.loc[df["id_empleado"] == id_empleado, [
            "nombre",
            "dni",
            "email",
            "telefono",
            "puesto",
            "ubicacion",
            "estado",
            "observaciones"
        ]] = [
            nombre,
            dni,
            email,
            telefono,
            puesto,
            ubicacion,
            estado,
            observaciones
        ]

        df.to_json(DATA_FILE, orient="records", indent=2, force_ascii=False)

        st.success("✅ Cambios guardados correctamente")
        st.session_state["modo_edicion"] = False
        st.rerun()

# -----------------------------------------
# MODO FICHA NORMAL
# -----------------------------------------
else:
    col_foto, col_info = st.columns([1, 3])

    with col_foto:
        foto = FOTOS_DIR / f"{id_empleado}.jpg"
        if foto.exists():
            st.image(str(foto), width=150)
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

        if empleado.get("observaciones"):
            st.markdown("### 📝 Observaciones")
            st.write(empleado["observaciones"])

    st.divider()
    st.subheader("📦 EPIs")
    st.info("EPIs se mostrarán aquí")

    st.subheader("🚗 Vehículo asignado")
    st.info("Vehículo se mostrará aquí")

