import streamlit as st
import pandas as pd
from pathlib import Path

# -----------------------------------------
# CONFIGURACIÓN
# -----------------------------------------
DATA_DIR = Path("data")
VEHICULOS_FILE = DATA_DIR / "vehiculos.json"
EMPLEADOS_FILE = DATA_DIR / "empleados.json"
FOTOS_DIR = DATA_DIR / "fotos_vehiculos"

st.title("🚚 Ficha de Vehículos")

# -----------------------------------------
# CARGA DE DATOS
# -----------------------------------------
def cargar_json_seguro(path):
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_json(path, dtype=False)
    except Exception:
        return pd.DataFrame()

df_vehiculos = cargar_json_seguro(VEHICULOS_FILE)
df_empleados = cargar_json_seguro(EMPLEADOS_FILE)

# -----------------------------------------
# VALIDACIONES BÁSICAS
# -----------------------------------------
if df_vehiculos.empty:
    st.warning("⚠️ No hay vehículos cargados en el sistema.")
    st.stop()

# Normalizar columnas esperadas
for col in ["id_vehiculo", "matricula", "marca", "modelo", "tipo", "estado", "bastidor", "id_empleado"]:
    if col not in df_vehiculos.columns:
        df_vehiculos[col] = ""

# -----------------------------------------
# SELECTOR DE VEHÍCULO
# -----------------------------------------
df_vehiculos["label"] = (
    df_vehiculos["id_vehiculo"].astype(str) + " - " + df_vehiculos["matricula"].astype(str)
)

vehiculo_sel = st.selectbox(
    "Selecciona un vehículo",
    df_vehiculos["label"].tolist()
)

vehiculo = df_vehiculos[df_vehiculos["label"] == vehiculo_sel].iloc[0]

st.markdown("---")

# -----------------------------------------
# CABECERA + FOTO
# -----------------------------------------
col_info, col_foto = st.columns([3, 1])

with col_info:
    st.subheader(vehiculo["matricula"])
    st.write(f"**Marca:** {vehiculo['marca']}")
    st.write(f"**Modelo:** {vehiculo['modelo']}")
    st.write(f"**Tipo:** {vehiculo['tipo']}")
    st.write(f"**Estado:** {vehiculo['estado']}")
    st.write(f"**Bastidor:** {vehiculo['bastidor']}")

with col_foto:
    foto_path = FOTOS_DIR / f"{vehiculo['id_vehiculo']}.jpg"

    # DEBUG visual (puedes borrar estas dos líneas cuando quieras)
    # st.write(foto_path)
    # st.write("Existe:", foto_path.exists())

    if foto_path.exists():
        st.image(str(foto_path), use_container_width=True)
    else:
        st.info("📷 Imagen del vehículo no disponible")

# -----------------------------------------
# EMPLEADO ASIGNADO
# -----------------------------------------
st.markdown("---")
st.subheader("👤 Empleado asignado")

id_emp = str(vehiculo["id_empleado"]).strip()

if id_emp and not df_empleados.empty and "id_empleado" in df_empleados.columns:
    emp = df_empleados[df_empleados["id_empleado"].astype(str) == id_emp]

    if not emp.empty:
        emp = emp.iloc[0]
        st.success(
            f"Asignado a **{emp['nombre']}** "
            f"({emp.get('puesto', 'Sin puesto')})"
        )
        st.caption("👉 Puedes ver el detalle completo en la ficha de empleados.")
    else:
        st.info("No asignado a ningún empleado")
else:
    st.info("No asignado a ningún empleado")


