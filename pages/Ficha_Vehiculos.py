import streamlit as st
import json
from pathlib import Path
import math

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
st.set_page_config(page_title="Ficha Vehículos", layout="wide")

BASE_PATH = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_PATH / "data"

VEH_FILE = DATA_PATH / "vehiculos.json"
EMP_FILE = DATA_PATH / "empleados.json"
FOTOS_EMP = DATA_PATH / "fotos_empleados"
FOTOS_VEH = DATA_PATH / "fotos_vehiculos"

# --------------------------------------------------
# MAPA FOTOS VEHÍCULOS (CORREGIDO)
# --------------------------------------------------
MAPA_FOTOS_VEHICULOS = {
    "paxster": "paxster.jpg",
    "scoobic": "scoobic.jpg",
    "renault": "renault.jpg",
}

# --------------------------------------------------
# HELPERS
# --------------------------------------------------
def load_json(path: Path):
    if not path.exists():
        return []
    try:
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            return []
        return json.loads(content)
    except Exception:
        return []

def clean(value):
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    return str(value)

def obtener_foto_vehiculo(marca):
    if not marca:
        return None
    clave = marca.strip().lower()
    nombre = MAPA_FOTOS_VEHICULOS.get(clave)
    if not nombre:
        return None
    ruta = FOTOS_VEH / nombre
    return ruta if ruta.exists() else None

# --------------------------------------------------
# DATA
# --------------------------------------------------
vehiculos = load_json(VEH_FILE)
empleados = load_json(EMP_FILE)

if not vehiculos:
    st.warning("No hay vehículos cargados en el sistema.")
    st.stop()

# --------------------------------------------------
# SESSION
# --------------------------------------------------
if "veh_index" not in st.session_state:
    st.session_state.veh_index = 0

st.session_state.veh_index = max(
    0, min(st.session_state.veh_index, len(vehiculos) - 1)
)

vehiculo = vehiculos[st.session_state.veh_index]

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown("## 🚗 Ficha de Vehículos")

# --------------------------------------------------
# SELECTOR + NAV
# --------------------------------------------------
c1, c2, c3, c4, c5 = st.columns([5, 1, 1, 1, 1])

with c1:
    opciones = [
        f"{v.get('id_vehiculo')} - {v.get('matricula', '')}"
        for v in vehiculos
    ]
    seleccion = st.selectbox(
        "Selecciona un vehículo",
        opciones,
        index=st.session_state.veh_index
    )
    st.session_state.veh_index = opciones.index(seleccion)

with c2:
    if st.button("⏮"):
        st.session_state.veh_index = 0
        st.rerun()
with c3:
    if st.button("◀"):
        st.session_state.veh_index -= 1
        st.rerun()
with c4:
    if st.button("▶"):
        st.session_state.veh_index += 1
        st.rerun()
with c5:
    if st.button("⏭"):
        st.session_state.veh_index = len(vehiculos) - 1
        st.rerun()

vehiculo = vehiculos[st.session_state.veh_index]

st.divider()

# --------------------------------------------------
# EMPLEADO ASIGNADO
# --------------------------------------------------
empleado = None
empleado_id = vehiculo.get("empleado_id")

if empleado_id:
    empleado = next(
        (e for e in empleados if e.get("id_empleado") == empleado_id),
        None
    )

# --------------------------------------------------
# LAYOUT PRINCIPAL
# --------------------------------------------------
c_left, c_mid, c_right = st.columns([1.2, 2.6, 1.2])

# ---------- FOTO EMPLEADO ----------
with c_left:
    if empleado:
        foto_emp = FOTOS_EMP / f"{empleado_id}.jpg"
        if foto_emp.exists():
            st.image(str(foto_emp), width=130)
        else:
            st.image(
                "https://cdn-icons-png.flaticon.com/512/4140/4140037.png",
                width=130
            )
    else:
        st.image(
            "https://cdn-icons-png.flaticon.com/512/149/149071.png",
            width=130
        )

# ---------- DATOS VEHÍCULO ----------
with c_mid:
    st.markdown(f"### 🚘 {clean(vehiculo.get('matricula'))}")

    st.markdown(f"""
- 🆔 **ID vehículo:** {clean(vehiculo.get('id_vehiculo'))}
- 🏷 **Marca / Modelo:** {clean(vehiculo.get('marca'))} {clean(vehiculo.get('modelo'))}
- 🔑 **Bastidor:** {clean(vehiculo.get('bastidor')) or "—"}
- 📄 **Tipo:** {clean(vehiculo.get('tipo')).capitalize()}
- 🚦 **Estado:** {clean(vehiculo.get('estado', 'OPERATIVO'))}
- 👤 **Asignado a:** {empleado.get('nombre') if empleado else "No asignado"}
    """)

# ---------- IMAGEN VEHÍCULO ----------
with c_right:
    foto_veh = obtener_foto_vehiculo(vehiculo.get("marca"))
    if foto_veh:
        st.image(str(foto_veh), width=160, caption="Vehículo")
    else:
        st.image(
            "https://cdn-icons-png.flaticon.com/512/741/741407.png",
            width=160,
            caption="Vehículo"
        )

# --------------------------------------------------
# ITV
# --------------------------------------------------
st.divider()
st.subheader("🛠 ITV")

st.markdown(f"""
- 📅 **ITV vigente hasta:** {clean(vehiculo.get('itv_vigente_hasta')) or "No indicada"}
- 🏢 **Estación ITV:** {clean(vehiculo.get('itv_estacion')) or "No indicada"}
""")

if st.button("🌐 Pedir cita ITV (Junta de Andalucía)"):
    st.markdown(
        "[Abrir web ITV Andalucía]"
        "(https://www.citaprevia.veiasa.es/)"
    )

# --------------------------------------------------
# SEGURO
# --------------------------------------------------
st.divider()
st.subheader("🛡 Seguro")

st.markdown(f"""
- 🏢 **Aseguradora:** {clean(vehiculo.get('aseguradora')) or "No indicada"}
- 📄 **Nº póliza:** {clean(vehiculo.get('poliza')) or "No indicado"}
- 📅 **Vigencia:** {clean(vehiculo.get('seguro_vigente_hasta')) or "No indicada"}
""")

# --------------------------------------------------
# FUTURO
# --------------------------------------------------
st.divider()
st.subheader("📂 Documentación")
st.info("ITV, seguro, multas y documentos del vehículo.")

st.divider()
st.subheader("🧰 Historial de averías")
st.info("Historial de incidencias, talleres y reparaciones.")



