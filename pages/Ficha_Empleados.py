import streamlit as st
import pandas as pd
from pathlib import Path
import json

st.title("🛠️ Administrar Empleados")

DATA_FILE = Path("data/empleados.json")

# -----------------------------------------
# CARGA
# -----------------------------------------
if not DATA_FILE.exists():
    st.error("No existe empleados.json")
    st.stop()

df = pd.read_json(DATA_FILE).fillna("")
df["id_empleado"] = df["id_empleado"].astype(int)

st.success(f"Hay {len(df)} empleados guardados en el sistema.")

# -----------------------------------------
# SELECCIÓN
# -----------------------------------------
st.subheader("Selecciona empleado a editar")

opciones = {
    f"{row['nombre']} ({row['dni']})": row["id_empleado"]
    for _, row in df.iterrows()
}

label = st.selectbox("Empleado", list(opciones.keys()))
id_empleado = opciones[label]

empleado = df[df["id_empleado"] == id_empleado].iloc[0]

st.divider()

# -----------------------------------------
# FORMULARIO EDICIÓN
# -----------------------------------------
st.subheader("✏️ Editar datos del empleado")

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

# -----------------------------------------
# GUARDADO
# -----------------------------------------
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
    st.rerun()

