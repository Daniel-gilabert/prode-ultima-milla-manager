import streamlit as st
import json
from pathlib import Path
from datetime import datetime

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"

VEH_FILE = DATA / "vehiculos.json"
EMP_FILE = DATA / "empleados.json"

FOTOS_EMP = DATA / "fotos_empleados"
FOTOS_VEH = DATA / "fotos_vehiculos"

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
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def s(v):
    if v is None:
        return ""
    v = str(v).strip()
    return "" if v.lower() in ("nan", "none") else v

def to_int(v):
    try:
        return int(v)
    except Exception:
        return None

def foto_empleado(emp_id):
    emp_id = to_int(emp_id)
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
    m = marca.lower()
    if "pax" in m:
        name = "paxster"
    elif "scoob" in m:
        name = "scoobic"
    elif "rena" in m:
        name = "renault"
    else:
        return None

    for ext in (".png", ".jpg", ".jpeg"):
        f = FOTOS_VEH / f"{name}{ext}"
        if f.exists():
            return f
    return None

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
vehiculos = load_json(VEH_FILE)
empleados_raw = load_json(EMP_FILE)

# Normalizar empleados (NO filtramos agresivo)
empleados = []
for e in empleados_raw:
    emp_id = to_int(e.get("id_empleado"))
    nombre = s(e.get("nombre"))
    if emp_id and nombre:
        empleados.append({
            "id_empleado": emp_id,
            "nombre": nombre
        })

st.title("🚗 Ficha de Vehículos")

if not vehiculos:
    st.warning("No hay vehículos cargados en el sistema.")
    st.stop()

vehiculos = sorted(vehiculos, key=lambda v: to_int(v.get("id_vehiculo")) or 0)

# --------------------------------------------------
# STATE
# --------------------------------------------------
if "veh_idx" not in st.session_state:
    st.session_state.veh_idx = 0

# --------------------------------------------------
# SELECTOR + NAV
# --------------------------------------------------
labels = [f"{v['id_vehiculo']} - {s(v.get('matricula'))}" for v in vehiculos]

c1, c2, c3, c4, c5 = st.columns([8, 1, 1, 1, 1])

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

with c5:
    if st.button("⏭"):
        st.session_state.veh_idx = len(vehiculos) - 1
        st.rerun()

veh = vehiculos[st.session_state.veh_idx]
veh["id_empleado"] = to_int(veh.get("id_empleado"))

emp_asignado = next(
    (e for e in empleados if e["id_empleado"] == veh.get("id_empleado")),
    None
)

# --------------------------------------------------
# FICHA
# --------------------------------------------------
st.divider()
l, m, r = st.columns([3, 4, 5])

with l:
    fe = foto_empleado(veh.get("id_empleado"))
    if fe:
        st.image(str(fe), width=220)
    else:
        st.info("Empleado sin foto")

with m:
    st.markdown(f"<h1>{s(veh.get('matricula'))}</h1>", unsafe_allow_html=True)
    st.markdown(
        f"<strong style='font-size:20px'>{s(veh.get('marca'))} {s(veh.get('modelo'))}</strong>",
        unsafe_allow_html=True
    )

    st.markdown(f"🆔 **ID vehículo:** {veh.get('id_vehiculo')}")
    st.markdown(f"🏷️ **Tipo:** {s(veh.get('tipo'))}")
    st.markdown(f"⚙️ **Estado:** {s(veh.get('estado','OPERATIVO'))}")
    st.markdown(f"🔩 **Bastidor:** {s(veh.get('bastidor'))}")
    st.markdown(
        f"👤 **Asignado a:** {emp_asignado['nombre'] if emp_asignado else 'No asignado'}"
    )

with r:
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

opts = ["— Sin asignar —"] + [
    f"{e['id_empleado']} - {e['nombre']}" for e in empleados
]

current = "— Sin asignar —"
if emp_asignado:
    current = f"{emp_asignado['id_empleado']} - {emp_asignado['nombre']}"

sel = st.selectbox("Empleado", opts, index=opts.index(current))

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
    st.success("Asignación guardada")
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



