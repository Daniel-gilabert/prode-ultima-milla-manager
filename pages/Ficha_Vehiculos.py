import streamlit as st
import json
from pathlib import Path
from datetime import date

# ----------------------------------
# CONFIG
# ----------------------------------
VEH_FILE = Path("data/vehiculos.json")
EMP_FILE = Path("data/empleados.json")
FOTOS_EMP = Path("data/fotos_empleados")
FOTOS_VEH = Path("data/fotos_vehiculos")

st.set_page_config(page_title="Ficha de Vehículos", layout="wide")

# ----------------------------------
# HELPERS
# ----------------------------------
def load_json(path, default):
    if not path.exists():
        return default
    content = path.read_text(encoding="utf-8").strip()
    if not content:
        return default
    return json.loads(content)

def save_json(path, data):
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

def foto_empleado(id_emp):
    if not id_emp:
        return None
    for ext in ["jpg", "png", "jpeg"]:
        f = FOTOS_EMP / f"{id_emp}.{ext}"
        if f.exists():
            return f
    return None

def foto_vehiculo(marca):
    if not marca:
        return None
    marca = marca.lower()
    if "paxster" in marca:
        return FOTOS_VEH / "paxster.png"
    if "scoobic" in marca:
        return FOTOS_VEH / "scoobic.png"
    if "renault" in marca:
        return FOTOS_VEH / "renault.png"
    return None

# ----------------------------------
# DATA
# ----------------------------------
vehiculos = load_json(VEH_FILE, [])
empleados = load_json(EMP_FILE, [])

if not vehiculos:
    st.warning("⚠️ No hay vehículos cargados en el sistema.")
    st.stop()

vehiculos = sorted(vehiculos, key=lambda x: x.get("id_vehiculo", 0))

# ----------------------------------
# SESSION STATE
# ----------------------------------
if "veh_idx" not in st.session_state:
    st.session_state.veh_idx = 0

# ----------------------------------
# HEADER
# ----------------------------------
st.title("🚗 Ficha de Vehículos")

labels = [
    f'{v["id_vehiculo"]} - {v["matricula"]}'
    for v in vehiculos
]

sel = st.selectbox(
    "Selecciona un vehículo",
    range(len(labels)),
    format_func=lambda i: labels[i],
    index=st.session_state.veh_idx
)

st.session_state.veh_idx = sel
veh = vehiculos[sel]

# ----------------------------------
# NAV BUTTONS
# ----------------------------------
c1, c2, c3, c4, _ = st.columns([1, 1, 1, 1, 6])

if c1.button("⏮"):
    st.session_state.veh_idx = 0
    st.experimental_rerun()

if c2.button("◀"):
    st.session_state.veh_idx = max(0, st.session_state.veh_idx - 1)
    st.experimental_rerun()

if c3.button("▶"):
    st.session_state.veh_idx = min(len(vehiculos) - 1, st.session_state.veh_idx + 1)
    st.experimental_rerun()

if c4.button("⏭"):
    st.session_state.veh_idx = len(vehiculos) - 1
    st.experimental_rerun()

st.divider()

# ----------------------------------
# MAIN LAYOUT
# ----------------------------------
col_emp, col_info, col_veh = st.columns([2, 4, 3])

# EMPLEADO FOTO
with col_emp:
    emp_id = veh.get("id_empleado")
    foto_emp = foto_empleado(emp_id)
    if foto_emp:
        st.image(str(foto_emp), width=180)
    else:
        st.info("Empleado sin foto")

# INFO
with col_info:
    st.subheader(veh["matricula"])
    st.caption(f'{veh.get("marca", "")} {veh.get("modelo", "")}')

    st.markdown(f"🆔 **ID vehículo:** {veh['id_vehiculo']}")
    st.markdown(f"🏷️ **Tipo:** {veh.get('tipo','')}")
    st.markdown(f"⚙️ **Estado:** {veh.get('estado','OPERATIVO')}")
    st.markdown(f"🔩 **Bastidor:** {veh.get('bastidor','')}")

    emp_actual = next(
        (e for e in empleados if e["id_empleado"] == emp_id),
        None
    )

    if emp_actual:
        st.markdown(f"👤 **Asignado a:** {emp_actual['nombre']}")
    else:
        st.markdown("👤 **Asignado a:** No asignado")

# VEH FOTO
with col_veh:
    fv = foto_vehiculo(veh.get("marca", ""))
    if fv:
        st.image(str(fv), use_container_width=True)

st.divider()

# ----------------------------------
# ASIGNACIÓN
# ----------------------------------
st.subheader("🔗 Asignar vehículo")

opciones = ["No asignado"] + [
    f'{e["id_empleado"]} - {e["nombre"]}'
    for e in empleados
]

sel_emp = st.selectbox("Empleado", opciones)

if st.button("💾 Guardar asignación"):
    hoy = str(date.today())

    # cerrar asignación anterior
    if veh.get("id_empleado"):
        veh.setdefault("historial_asignaciones", []).append({
            "id_empleado": veh["id_empleado"],
            "fecha_fin": hoy
        })

    if sel_emp == "No asignado":
        veh["id_empleado"] = None
    else:
        id_emp = int(sel_emp.split(" - ")[0])
        veh["id_empleado"] = id_emp
        veh.setdefault("historial_asignaciones", []).append({
            "id_empleado": id_emp,
            "fecha_inicio": hoy
        })

    save_json(VEH_FILE, vehiculos)
    st.success("✅ Asignación actualizada")
    st.experimental_rerun()

# ----------------------------------
# HISTORIAL
# ----------------------------------
if st.button("📜 Mostrar historial de asignaciones"):
    hist = veh.get("historial_asignaciones", [])
    if not hist:
        st.info("Sin historial")
    else:
        for h in hist:
            emp = next(
                (e for e in empleados if e["id_empleado"] == h["id_empleado"]),
                {}
            )
            st.markdown(
                f"👤 **{emp.get('nombre','')}** | "
                f"{h.get('fecha_inicio','')} → {h.get('fecha_fin','Actual')}"
            )


