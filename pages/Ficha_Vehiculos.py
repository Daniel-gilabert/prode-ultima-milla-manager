import streamlit as st
import json
from pathlib import Path
from datetime import date

# --------------------------------------------------
# CONFIGURACIÓN PÁGINA
# --------------------------------------------------
st.set_page_config(page_title="Ficha de Vehículos", layout="wide")

# --------------------------------------------------
# RUTAS
# --------------------------------------------------
BASE = Path.cwd()
DATA = BASE / "data"

VEH_FILE = DATA / "vehiculos.json"
EMP_FILE = DATA / "empleados.json"

# --------------------------------------------------
# FUNCIONES SEGURAS
# --------------------------------------------------
def load_json(path: Path):
    """Carga JSON aunque esté vacío o roto"""
    if not path.exists():
        return []
    try:
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            return []
        return json.loads(content)
    except Exception:
        return []

# --------------------------------------------------
# CARGA DE DATOS
# --------------------------------------------------
vehiculos = load_json(VEH_FILE)
empleados = load_json(EMP_FILE)

# --------------------------------------------------
# MAPA EMPLEADOS
# --------------------------------------------------
emp_map = {e.get("id_empleado"): e for e in empleados}

# --------------------------------------------------
# UI
# --------------------------------------------------
st.title("🚗 Ficha de Vehículos")

if not vehiculos:
    st.warning("No hay vehículos cargados en el sistema.")
    st.stop()

# Ordenar por id_vehiculo
vehiculos = sorted(vehiculos, key=lambda x: x.get("id_vehiculo", 0))

# Inicializar índice
if "veh_index" not in st.session_state:
    st.session_state.veh_index = 0

# Selector
opciones = [
    f"{v.get('id_vehiculo')} - {v.get('matricula')}"
    for v in vehiculos
]

selected = st.selectbox(
    "Selecciona un vehículo",
    opciones,
    index=st.session_state.veh_index
)

st.session_state.veh_index = opciones.index(selected)
veh = vehiculos[st.session_state.veh_index]

# --------------------------------------------------
# BOTONES NAVEGACIÓN (muy juntos y a la derecha)
# --------------------------------------------------
_, _, nav = st.columns([6, 1, 3])
with nav:
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
    with c1:
        if st.button("⏮", key="first"):
            st.session_state.veh_index = 0
            st.rerun()
    with c2:
        if st.button("◀", key="prev"):
            st.session_state.veh_index = max(0, st.session_state.veh_index - 1)
            st.rerun()
    with c3:
        if st.button("▶", key="next"):
            st.session_state.veh_index = min(len(vehiculos) - 1, st.session_state.veh_index + 1)
            st.rerun()
    with c4:
        if st.button("⏭", key="last"):
            st.session_state.veh_index = len(vehiculos) - 1
            st.rerun()

st.divider()

# --------------------------------------------------
# FICHA VEHÍCULO
# --------------------------------------------------
col1, col2 = st.columns([1, 3])

with col1:
    st.markdown("### 🚘")
    st.info("Imagen vehículo\n(próximamente)")

with col2:
    st.markdown(f"## {veh.get('marca', '')} {veh.get('modelo', '')}")
    st.markdown(f"**🆔 ID vehículo:** {veh.get('id_vehiculo')}")
    st.markdown(f"**🔢 Matrícula:** {veh.get('matricula')}")
    st.markdown(f"**🏷️ Bastidor:** {veh.get('bastidor', '—')}")
    st.markdown(f"**📄 Tipo:** {veh.get('tipo', '—')}")
    st.markdown(f"**⚙️ Estado:** {veh.get('estado', 'OPERATIVO')}")

    # Asignación empleado
    emp_id = veh.get("empleado_id")
    if emp_id and emp_id in emp_map:
        emp = emp_map[emp_id]
        st.markdown(
            f"**👤 Asignado a:** {emp.get('nombre')} "
            f"({emp.get('email')})"
        )
    else:
        st.markdown("**👤 Asignado a:** No asignado")

st.divider()

# --------------------------------------------------
# ITV / SEGURO
# --------------------------------------------------
st.subheader("📅 ITV y Seguro")

col_itv, col_seg = st.columns(2)

with col_itv:
    st.markdown(f"**ITV vigente hasta:** {veh.get('itv_vigente_hasta', '—')}")
    st.markdown(f"**Estación ITV:** {veh.get('itv_estacion', '—')}")
    if veh.get("itv_cita"):
        st.markdown(f"**📌 Cita ITV:** {veh.get('itv_cita')}")
        st.link_button(
            "Pedir cita ITV Andalucía",
            "https://www.itvcita.com"
        )

with col_seg:
    st.markdown(f"**Aseguradora:** {veh.get('aseguradora', '—')}")
    st.markdown(f"**Póliza:** {veh.get('poliza', '—')}")
    st.markdown(f"**Seguro vigente hasta:** {veh.get('seguro_vigente_hasta', '—')}")

st.divider()

# --------------------------------------------------
# BLOQUES FUTUROS
# --------------------------------------------------
st.subheader("📂 Documentación")
st.info("Repositorio por matrícula (pendiente de implementación)")

st.subheader("🛠️ Historial de averías")
st.info("Se gestionará desde mantenimiento")

st.subheader("🚨 Avisos automáticos")
st.info("Avisos por email 30 días antes ITV y 7 días antes de cita")

