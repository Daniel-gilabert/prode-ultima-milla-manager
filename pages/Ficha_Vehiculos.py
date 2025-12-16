import streamlit as st
import json
from pathlib import Path
from datetime import datetime

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
BASE_PATH = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_PATH / "data"

VEH_FILE = DATA_PATH / "vehiculos.json"
EMP_FILE = DATA_PATH / "empleados.json"

FOTOS_EMP = DATA_PATH / "fotos_empleados"
FOTOS_VEH = DATA_PATH / "fotos_vehiculos"

st.set_page_config(page_title="Ficha de Vehículos", layout="wide")

# --------------------------------------------------
# HELPERS
# --------------------------------------------------
def load_json(path):
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []

def save_json(path, data):
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

def clean(v):
    if v is None:
        return ""
    v = str(v).strip()
    return "" if v.lower() in ("nan", "none") else v

def safe_int(v):
    try:
        return int(v)
    except Exception:
        return None

def foto_empleado(emp_id):
    emp_id = safe_int(emp_id)
    if not emp_id:
        return None
    for ext in (".jpg", ".png", ".jpeg"):
        f = FOTOS_EMP / f"{emp_id}{ext}"
        if f.exists():
            return f
    return None

def foto_vehiculo(marca):
    if not marca:
        return None

    m = marca.lower().strip()

    posibles = []
    if "pax" in m:
        posibles = ["paxster.png", "paxster.jpg"]
    elif "scoob" in m:
        posibles = ["scoobic.png", "scoobic.jpg"]
    elif "rena" in m:
        posibles = ["renault.png", "renault.jpg"]

    for p in posibles:
        f = FOTOS_VEH / p
        if f.exists():
            return f

    return None

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
vehiculos = load_json(VEH_FILE)
empleados_raw = load_json(EMP_FILE)

# Normalizar empleados
empleados = []
for e in empleados_raw:
    emp_id = safe_int(e.get("id_empleado"))
    nombre = clean(e.get("nombre"))
    if emp_id and nombre:
        e["id_empleado"] = emp_id
        empleados.append(e)

st.title("🚗 Ficha de Vehículos")

if not vehiculos:
    st.warning("No hay vehículos cargados en el sistema.")
    st.stop()

vehiculos = sorted(vehiculos, key=lambda x: safe_int(x.get("id_vehiculo")) or 0)

# --------------------------------------------------
# STATE
# --------------------------------------------------
if "veh_idx" not in st.session_state:
    st.session_state.veh_idx = 0

# --------------------------------------------------
# SELECTOR + NAV
# --------------------------------------------------
labels = [
    f"{v['id_vehiculo']} - {clean(v.get('matricula'))}"
    for v in vehiculos
]

c1, c2, c3, c4 = st.columns([8, 1, 1, 1])

with c1:
    idx = st.selectbox(
        "Selecciona un vehículo",
        range(len(labels)),
        index=st.session_state.veh_idx,
        format_func=lambda i: labels[i]
    )
    st.session_state.veh_idx = idx

with c2:
    if st.button("⏮"):
        st.session_state.veh_idx = 0
        st.rerun()

with c3:
    if st.button("◀"):
        st.session_state.veh_idx = max(0, st.session_state.veh_idx - 1)
        st.rerun()

with c4:
    if st.button("▶"):
        st.session_state.veh_idx = min(len(vehiculos) - 1, st.session_state.veh_idx + 1)
        st.rerun()

veh = vehiculos[st.session_state.veh_idx]
veh["id_empleado"] = safe_int(veh.get("id_empleado"))

emp_asignado = next(
    (e for e in empleados if e["id_empleado"] == veh.get("id_empleado")),
    None
)

# --------------------------------------------------
# FICHA
# --------------------------------------------------
st.divider()
left, mid, right = st.columns([3, 4, 5])

with left:
    fe = foto_empleado(veh.get("id_empleado"))
    if fe:
        st.image(str(fe), width=220)
    else:
        st.info("Empleado sin foto")

with mid:
    st.markdown(
        f"<h1 style='margin-bottom:0'>{clean(veh.get('matricula'))}</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"<strong style='font-size:20px'>{clean(veh.get('marca'))} {clean(veh.get('modelo'))}</strong>",
        unsafe_allow_html=True
    )

    st.markdown(f"🆔 **ID vehículo:** {veh.get('id_vehiculo')}")
    st.markdown(f"🏷️ **Tipo:** {clean(veh.get('tipo'))}")
    st.markdown(f"⚙️ **Estado:** {clean(veh.get('estado','OPERATIVO'))}")
    st.markdown(f"🔩 **Bastidor:** {clean(veh.get('bastidor'))}")
    st.markdown(
        f"👤 **Asignado a:** {emp_asignado['nombre'] if emp_asignado else 'No asignado'}"
    )

with right:
    fv = foto_vehiculo(veh.get("marca"))
    if fv:
        st.image(str(fv), use_container_width=True)
    else:
        st.info("Imagen del vehículo no disponible")

# --------------------------------------------------
# ASIGNACIÓN
# --------------------------------------------------
st.divider()
st.subheader("🔗 Asignar vehículo a empleado")

options = ["— Sin asignar —"] + [
    f"{e['id_empleado']} - {e['nombre']}" for e in empleados
]

current = "— Sin asignar —"
if emp_asignado:
    current = f"{emp_asignado['id_empleado']} - {emp_asignado['nombre']}"

sel = st.selectbox("Empleado", options, index=options.index(current))

if st.button("Guardar asignación"):
    if sel == "— Sin asignar —":
        veh["id_empleado"] = None
    else:
        veh["id_empleado"] = int(sel.split(" - ")[0])

    veh.setdefault("historial_asignaciones", []).append({
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "id_empleado": veh.get("id_empleado")
    })

    save_json(VEH_FILE, vehiculos)
    st.success("Asignación guardada correctamente")
    st.rerun()

# --------------------------------------------------
# HISTORIAL
# --------------------------------------------------
if veh.get("historial_asignaciones"):
    with st.expander("📜 Historial de asignaciones"):
        for h in reversed(veh["historial_asignaciones"]):
            emp = next(
                (e for e in empleados if e["id_empleado"] == h.get("id_empleado")),
                None
            )
            st.write(f"{h['fecha']} → {emp['nombre'] if emp else 'Sin asignar'}")

st.divider()
st.info("Aquí se integrarán ITV, seguros, averías, multas y documentación.")


