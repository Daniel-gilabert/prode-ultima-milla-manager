import streamlit as st
import json
from pathlib import Path

# --------------------------------------------------
# CONFIGURACIÓN
# --------------------------------------------------
st.set_page_config(layout="wide")

DATA = Path("data")
VEH_FILE = DATA / "vehiculos.json"
EMP_FILE = DATA / "empleados.json"
FOTOS_EMP = DATA / "fotos_empleados"
FOTOS_VEH = DATA / "fotos_vehiculos"

# --------------------------------------------------
# FUNCIONES
# --------------------------------------------------
def load_json_safe(path):
    if not path.exists():
        return []
    try:
        contenido = path.read_text(encoding="utf-8").strip()
        if not contenido:
            return []
        return json.loads(contenido)
    except Exception:
        return []

def limpiar(valor):
    if valor is None:
        return ""
    if isinstance(valor, float):
        return ""
    return str(valor)

# --------------------------------------------------
# CARGA DE DATOS
# --------------------------------------------------
vehiculos = load_json_safe(VEH_FILE)
empleados = load_json_safe(EMP_FILE)

if not vehiculos:
    st.warning("⚠️ No hay vehículos cargados en el sistema.")
    st.info("👉 Cárgalos desde **Administrar Vehículos**.")
    st.stop()

# Indexar empleados por id
empleados_por_id = {
    int(e["id_empleado"]): e for e in empleados if str(e.get("id_empleado", "")).isdigit()
}

# --------------------------------------------------
# SELECTOR VEHÍCULO
# --------------------------------------------------
vehiculos = sorted(vehiculos, key=lambda x: x.get("id_vehiculo", 0))

opciones = {
    f'{v["id_vehiculo"]} - {v.get("matricula", "")}': v
    for v in vehiculos
}

st.title("🚗 Ficha de Vehículos")

clave = st.selectbox(
    "Selecciona un vehículo",
    opciones.keys()
)

veh = opciones[clave]

# --------------------------------------------------
# DATOS PRINCIPALES
# --------------------------------------------------
id_veh = veh.get("id_vehiculo")
matricula = limpiar(veh.get("matricula"))
marca = limpiar(veh.get("marca"))
modelo = limpiar(veh.get("modelo"))
bastidor = limpiar(veh.get("bastidor"))
tipo = limpiar(veh.get("tipo")).lower()
estado = limpiar(veh.get("estado", "OPERATIVO"))
id_emp = veh.get("id_empleado")

# --------------------------------------------------
# EMPLEADO ASIGNADO
# --------------------------------------------------
empleado = empleados_por_id.get(id_emp)
nombre_emp = empleado["nombre"] if empleado else "No asignado"

# Foto empleado
foto_emp = None
if empleado:
    posible = FOTOS_EMP / f'{empleado["id_empleado"]}.jpg'
    if posible.exists():
        foto_emp = posible

# --------------------------------------------------
# FOTO VEHÍCULO (POR MARCA)
# --------------------------------------------------
foto_veh = None
marca_lower = marca.lower()

if "paxster" in marca_lower:
    foto_veh = FOTOS_VEH / "paxster.jpg"
elif "scoobic" in marca_lower:
    foto_veh = FOTOS_VEH / "scoobic.jpg"
elif "renault" in marca_lower:
    foto_veh = FOTOS_VEH / "renault.jpg"

# --------------------------------------------------
# UI
# --------------------------------------------------
st.markdown("---")

col_foto_emp, col_info, col_foto_veh = st.columns([1.2, 2.2, 1.4])

# FOTO EMPLEADO
with col_foto_emp:
    if foto_emp:
        st.image(str(foto_emp), width=160)
    else:
        st.info("Empleado sin foto")

# INFO VEHÍCULO
with col_info:
    st.subheader(matricula)
    st.caption(f"{marca} {modelo}")

    st.markdown(f"🆔 **ID vehículo:** {id_veh}")
    st.markdown(f"🏷️ **Tipo:** {tipo}")
    st.markdown(f"⚙️ **Estado:** {estado}")
    st.markdown(f"🔩 **Bastidor:** {bastidor or '—'}")
    st.markdown(f"👤 **Asignado a:** {nombre_emp}")

# FOTO VEHÍCULO
with col_foto_veh:
    if foto_veh and foto_veh.exists():
        st.image(str(foto_veh), use_container_width=True)
    else:
        st.info("Imagen vehículo no disponible")

st.markdown("---")

# --------------------------------------------------
# FUTURAS SECCIONES
# --------------------------------------------------
st.subheader("📌 Información adicional")
st.info("Aquí se integrarán: ITV, seguros, averías, multas y documentación.")

