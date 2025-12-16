import streamlit as st
import json
from pathlib import Path
from datetime import datetime

# ------------------------
# CONFIG
# ------------------------
DATA_DIR = Path("data")
VEH_FILE = DATA_DIR / "vehiculos.json"
EMP_FILE = DATA_DIR / "empleados.json"
FOTOS_VEH = DATA_DIR / "fotos_vehiculos"
FOTOS_EMP = DATA_DIR / "fotos_empleados"

st.set_page_config(page_title="Ficha de Vehículos", layout="wide")

# ------------------------
# HELPERS
# ------------------------
def load_json(path, default):
    if not path.exists():
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def foto_vehiculo(marca):
    if not marca:
        return None
    fname = marca.lower().strip() + ".png"
    fpath = FOTOS_VEH / fname
    return fpath if fpath.exists() else None

def foto_empleado(emp_id):
    if not emp_id:
        return None
    for ext in ["jpg", "png", "jpeg"]:
        f = FOTOS_EMP / f"{emp_id}.{ext}"
        if f.exists():
            return f
    return None

# ------------------------
# DATA
# ------------------------
vehiculos = load_json(VEH_FILE, [])
empleados = load_json(EMP_FILE, [])

if not vehiculos:
    st.warning("⚠️ No hay vehículos cargados. Usa **Administrar Vehículos** para cargarlos.")
    st.stop()

# ------------------------
# SESSION STATE
# ------------------------
if "veh_index" not in st.session_state:
    st.session_state.veh_index = 0

# ------------------------
# HEADER
# ------------------------
st.title("🚗 Ficha de Vehículos")

ids = [f"{v['id_vehiculo']} - {v['matricula']}" for v in vehiculos]

col_sel, col_btns = st.columns([6, 2])

with col_sel:
    selected = st.selectbox(
        "Selecciona un vehículo",
        range(len(ids)),
        format_func=lambda i: ids[i],
        index=st.session_state.veh_index
    )
    st.session_state.veh_index = selected

with col_btns:
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("⏮"):
            st.session_state.veh_index = 0
            st.rerun()
    with c2:
        if st.button("◀"):
            st.session_state.veh_index = max(0, st.session_state.veh_index - 1)
            st.rerun()
    with c3:
        if st.button("▶"):
            st.session_state.veh_index = min(len(vehiculos) - 1, st.session_state.veh_index + 1)
            st.rerun()
    with c4:
        if st.button("⏭"):
            st.session_state.veh_index = len(vehiculos) - 1
            st.rerun()

veh = vehiculos[st.session_state.veh_index]

st.divider()

# ------------------------
# MAIN INFO
# ------------------------
c_left, c_mid, c_right = st.columns([3, 4, 5])

# FOTO EMPLEADO
with c_left:
    f_emp = foto_empleado(veh.get("id_empleado"))
    if f_emp:
        st.image(str(f_emp), use_container_width=True)
    else:
        st.info("Empleado sin foto")

# TEXTO CENTRAL
with c_mid:
    st.markdown(f"## **{veh['matricula']}**")
    st.markdown(f"### **{veh.get('marca','')} {veh.get('modelo','')}**")

    st.markdown(f"🆔 **ID vehículo:** {veh['id_vehiculo']}")
    st.markdown(f"🏷 **Tipo:** {veh.get('tipo','')}")
    st.markdown(f"⚙️ **Estado:** {veh.get('estado','OPERATIVO')}")
    st.markdown(f"🔩 **Bastidor:** {veh.get('bastidor','')}")

    emp = next((e for e in empleados if e["id_empleado"] == veh.get("id_empleado")), None)
    if emp:
        st.markdown(f"👤 **Asignado a:** {emp['nombre']}")
    else:
        st.markdown("👤 **Asignado a:** No asignado")

# FOTO VEHÍCULO
with c_right:
    f_veh = foto_vehiculo(veh.get("marca"))
    if f_veh:
        st.image(str(f_veh), use_container_width=True)
    else:
        st.info("Imagen del vehículo no disponible")

st.divider()

# ------------------------
# ASIGNACIÓN
# ------------------------
st.subheader("🔗 Asignar vehículo a empleado")

emp_options = ["— Sin asignar —"] + [
    f"{e['id_empleado']} - {e['nombre']}" for e in empleados
]

sel_emp = st.selectbox("Empleado", emp_options)

if st.button("Guardar asignación"):
    if sel_emp == "— Sin asignar —":
        veh["id_empleado"] = None
    else:
        veh["id_empleado"] = int(sel_emp.split(" - ")[0])

    veh.setdefault("historial_asignaciones", []).append({
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "empleado": sel_emp
    })

    save_json(VEH_FILE, vehiculos)
    st.success("Asignación guardada correctamente")
    st.rerun()

# ------------------------
# HISTORIAL
# ------------------------
with st.expander("📜 Historial de asignaciones"):
    hist = veh.get("historial_asignaciones", [])
    if not hist:
        st.info("Sin historial")
    else:
        for h in reversed(hist):
            st.write(f"{h['fecha']} → {h['empleado']}")

