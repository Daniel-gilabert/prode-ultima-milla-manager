import streamlit as st
import json
from pathlib import Path
from datetime import date

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
st.set_page_config(page_title="Ficha de Vehículos", layout="wide")
st.title("🚗 Ficha de Vehículos")

DATA = Path("data")
VEH_FILE = DATA / "vehiculos.json"
EMP_FILE = DATA / "empleados.json"

# --------------------------------------------------
# CARGA DE DATOS
# --------------------------------------------------
def load_json(path):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return []

vehiculos = load_json(VEH_FILE)
empleados = load_json(EMP_FILE)

if not vehiculos:
    st.warning("No hay vehículos cargados.")
    st.stop()

# --------------------------------------------------
# ORDENAR POR ID
# --------------------------------------------------
vehiculos = sorted(
    vehiculos,
    key=lambda x: int(x["id_vehiculo"]) if x.get("id_vehiculo") else 9999
)

# --------------------------------------------------
# SELECTOR VEHÍCULO
# --------------------------------------------------
labels = [
    f'{v.get("id_vehiculo", "-")} - {v["matricula"]} ({v["marca"]})'
    for v in vehiculos
]

if "veh_index" not in st.session_state:
    st.session_state.veh_index = 0

selected = st.selectbox(
    "Selecciona un vehículo",
    range(len(labels)),
    format_func=lambda i: labels[i],
    index=st.session_state.veh_index
)

vehiculo = vehiculos[selected]
st.session_state.veh_index = selected

# --------------------------------------------------
# NAVEGACIÓN (COMPACTA Y A LA DERECHA)
# --------------------------------------------------
_, _, nav = st.columns([6, 1, 2])

with nav:
    c1, c2, c3, c4 = st.columns([1,1,1,1], gap="small")

    with c1:
        if st.button("⏮", key="first"):
            st.session_state.veh_index = 0
            st.rerun()
    with c2:
        if st.button("◀", key="prev"):
            st.session_state.veh_index = max(0, selected - 1)
            st.rerun()
    with c3:
        if st.button("▶", key="next"):
            st.session_state.veh_index = min(len(vehiculos)-1, selected + 1)
            st.rerun()
    with c4:
        if st.button("⏭", key="last"):
            st.session_state.veh_index = len(vehiculos)-1
            st.rerun()

st.divider()

# --------------------------------------------------
# INFO PRINCIPAL
# --------------------------------------------------
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### 📄 Datos del vehículo")
    st.write(f"**ID:** {vehiculo.get('id_vehiculo','-')}")
    st.write(f"**Matrícula:** {vehiculo['matricula']}")
    st.write(f"**Bastidor:** {vehiculo.get('bastidor','-')}")
    st.write(f"**Marca:** {vehiculo['marca']}")
    st.write(f"**Modelo:** {vehiculo.get('modelo','-')}")
    st.write(f"**Tipo:** {vehiculo['tipo']}")
    st.write(f"**Estado:** {vehiculo.get('estado','OPERATIVO')}")

with col2:
    st.markdown("### 👤 Asignación a empleado")

    emp_map = {None: "— Sin asignar —"}
    for e in empleados:
        emp_map[e["id_empleado"]] = f'{e["id_empleado"]} - {e["nombre"]}'

    empleado_actual = vehiculo.get("empleado_id")

    nuevo_emp = st.selectbox(
        "Empleado asignado",
        options=list(emp_map.keys()),
        format_func=lambda x: emp_map[x],
        index=list(emp_map.keys()).index(empleado_actual)
        if empleado_actual in emp_map else 0
    )

    if nuevo_emp != empleado_actual:
        vehiculo["empleado_id"] = nuevo_emp

# --------------------------------------------------
# ITV
# --------------------------------------------------
st.divider()
st.markdown("### 🛠️ ITV")

vehiculo["itv_vigente_hasta"] = st.date_input(
    "Vigente hasta",
    value=date.fromisoformat(vehiculo["itv_vigente_hasta"])
    if vehiculo.get("itv_vigente_hasta") else None
)

vehiculo["itv_cita_fecha"] = st.date_input(
    "Fecha cita ITV",
    value=date.fromisoformat(vehiculo["itv_cita_fecha"])
    if vehiculo.get("itv_cita_fecha") else None
)

vehiculo["itv_estacion"] = st.text_input(
    "Estación ITV",
    vehiculo.get("itv_estacion","")
)

st.link_button(
    "🌐 Pedir cita ITV Junta de Andalucía",
    "https://www.juntadeandalucia.es/organismos/itv.html"
)

# --------------------------------------------------
# SEGURO
# --------------------------------------------------
st.divider()
st.markdown("### 🛡️ Seguro")

vehiculo["seguro_aseguradora"] = st.text_input(
    "Aseguradora",
    vehiculo.get("seguro_aseguradora","")
)

vehiculo["seguro_poliza"] = st.text_input(
    "Número de póliza",
    vehiculo.get("seguro_poliza","")
)

vehiculo["seguro_vigente_hasta"] = st.date_input(
    "Seguro vigente hasta",
    value=date.fromisoformat(vehiculo["seguro_vigente_hasta"])
    if vehiculo.get("seguro_vigente_hasta") else None
)

# --------------------------------------------------
# GUARDAR
# --------------------------------------------------
st.divider()

if st.button("💾 Guardar cambios del vehículo"):
    with open(VEH_FILE, "w", encoding="utf-8") as f:
        json.dump(vehiculos, f, indent=2, ensure_ascii=False)
    st.success("✅ Vehículo actualizado correctamente")
