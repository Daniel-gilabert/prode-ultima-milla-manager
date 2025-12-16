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
    except json.JSONDecodeError:
        return []

def save_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def foto_empleado(emp_id):
    if not emp_id:
        return None
    for ext in [".jpg", ".png", ".jpeg"]:
        f = FOTOS_EMP / f"{emp_id}{ext}"
        if f.exists():
            return f
    return None

def foto_vehiculo(marca):
    if not marca:
        return None

    marca = str(marca).lower().strip()

    mapping = {
        "paxster": "paxster.png",
        "scoobic": "scoobic.png",
        "renault": "renault.png",
    }

    for key, img in mapping.items():
        if key in marca:
            f = FOTOS_VEH / img
            if f.exists():
                return f
    return None

def clean(value):
    if value is None:
        return ""
    v = str(value)
    return "" if v.lower() == "nan" else v

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
vehiculos = load_json(VEH_FILE)
empleados = load_json(EMP_FILE)

st.title("🚗 Ficha de Vehículos")

if not vehiculos:
    st.warning("No hay vehículos cargados en el sistema.")
    st.stop()

vehiculos = sorted(vehiculos, key=lambda x: x.get("id_vehiculo", 0))

# --------------------------------------------------
# STATE
# --------------------------------------------------
if "veh_idx" not in st.session_state:
    st.session_state.veh_idx = 0

# --------------------------------------------------
# SELECTOR + NAV
# --------------------------------------------------
labels = [
    f"{v['id_vehiculo']} - {v.get('matricula','')}"
    for v in vehiculos
]

c1, c2, c3, c4 = st.columns([8, 1, 1, 1])

with c1:
    sel = st.selectbox(
        "Selecciona un vehículo",
        range(len(labels)),
        index=st.session_state.veh_idx,
        format_func=lambda i: labels[i],
    )
    st.session_state.veh_idx = sel

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

# --------------------------------------------------
# ASSIGNMENT
# --------------------------------------------------
emp_asignado = next(
    (e for e in empleados if e.get("id_empleado") == veh.get("id_empleado")),
    None
)

# --------------------------------------------------
# FICHA
# --------------------------------------------------
st.divider()

left, mid, right = st.columns([3, 4, 5])

with left:
    fe = foto_empleado(veh.get("id_empleado"))
    if fe and fe.exists():
        st.image(str(fe), width=200)
    else:
        st.info("Empleado sin foto")

with mid:
    st.subheader(clean(veh.get("matricula")))
    st.caption(f"{clean(veh.get('marca'))} {clean(veh.get('modelo'))}")

    st.markdown(f"🆔 **ID vehículo:** {veh.get('id_vehiculo')}")
    st.markdown(f"🏷️ **Tipo:** {clean(veh.get('tipo'))}")
    st.markdown(f"⚙️ **Estado:** {clean(veh.get('estado','OPERATIVO'))}")
    st.markdown(f"🔩 **Bastidor:** {clean(veh.get('bastidor'))}")

    if emp_asignado:
        st.markdown(f"👤 **Asignado a:** {emp_asignado.get('nombre')}")
    else:
        st.markdown("👤 **Asignado a:** No asignado")

with right:
    fv = foto_vehiculo(veh.get("marca"))
    if fv and fv.exists():
        try:
            st.image(str(fv), use_container_width=True)
        except Exception:
            st.info("Imagen del vehículo no disponible")
    else:
        st.info("Imagen del vehículo no disponible")

# --------------------------------------------------
# ASIGNAR VEHÍCULO
# --------------------------------------------------
st.divider()
st.subheader("🔗 Asignar vehículo a empleado")

emp_options = ["— Sin asignar —"] + [
    f"{e['id_empleado']} - {e['nombre']}" for e in empleados
]

current = (
    f"{emp_asignado['id_empleado']} - {emp_asignado['nombre']}"
    if emp_asignado else "— Sin asignar —"
)

new = st.selectbox("Empleado", emp_options, index=emp_options.index(current))

if st.button("Guardar asignación"):
    if new == "— Sin asignar —":
        veh["id_empleado"] = None
    else:
        veh["id_empleado"] = int(new.split(" - ")[0])

    veh.setdefault("historial_asignaciones", []).append({
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "id_empleado": veh.get("id_empleado"),
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
            nombre = emp["nombre"] if emp else "Sin asignar"
            st.write(f"{h['fecha']} → {nombre}")

# --------------------------------------------------
# INFO FUTURA
# --------------------------------------------------
st.divider()
st.info("Aquí se integrarán: ITV, seguros, averías, multas y documentación.")



