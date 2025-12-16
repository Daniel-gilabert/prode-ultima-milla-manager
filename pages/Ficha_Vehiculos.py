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
        txt = path.read_text(encoding="utf-8").strip()
        if not txt:
            return []
        return json.loads(txt)
    except Exception:
        return []

def clean(v):
    if v is None:
        return ""
    if isinstance(v, float):
        return ""
    return str(v)

# --------------------------------------------------
# CARGA DE DATOS
# --------------------------------------------------
vehiculos = load_json_safe(VEH_FILE)
empleados = load_json_safe(EMP_FILE)

if not vehiculos:
    st.warning("⚠️ No hay vehículos cargados en el sistema.")
    st.info("👉 Cárgalos una sola vez desde **Administrar Vehículos**.")
    st.stop()

vehiculos = sorted(vehiculos, key=lambda x: x.get("id_vehiculo", 0))

emp_by_id = {
    int(e["id_empleado"]): e
    for e in empleados
    if str(e.get("id_empleado", "")).isdigit()
}

# --------------------------------------------------
# STATE DE NAVEGACIÓN
# --------------------------------------------------
if "veh_index" not in st.session_state:
    st.session_state.veh_index = 0

def ir_primero():
    st.session_state.veh_index = 0

def ir_anterior():
    if st.session_state.veh_index > 0:
        st.session_state.veh_index -= 1

def ir_siguiente():
    if st.session_state.veh_index < len(vehiculos) - 1:
        st.session_state.veh_index += 1

def ir_ultimo():
    st.session_state.veh_index = len(vehiculos) - 1

# --------------------------------------------------
# SELECTOR + BOTONES
# --------------------------------------------------
st.title("🚗 Ficha de Vehículos")

col_sel, col_btns = st.columns([5, 2])

with col_sel:
    opciones = [
        f'{v["id_vehiculo"]} - {v.get("matricula","")}'
        for v in vehiculos
    ]
    seleccion = st.selectbox(
        "Selecciona un vehículo",
        opciones,
        index=st.session_state.veh_index
    )
    st.session_state.veh_index = opciones.index(seleccion)

with col_btns:
    b1, b2, b3, b4 = st.columns(4)
    with b1:
        st.button("⏮", on_click=ir_primero)
    with b2:
        st.button("⬅", on_click=ir_anterior)
    with b3:
        st.button("➡", on_click=ir_siguiente)
    with b4:
        st.button("⏭", on_click=ir_ultimo)

veh = vehiculos[st.session_state.veh_index]

# --------------------------------------------------
# DATA VEHÍCULO
# --------------------------------------------------
id_veh = veh.get("id_vehiculo")
matricula = clean(veh.get("matricula"))
marca = clean(veh.get("marca"))
modelo = clean(veh.get("modelo"))
bastidor = clean(veh.get("bastidor"))
tipo = clean(veh.get("tipo")).lower()
estado = clean(veh.get("estado", "OPERATIVO"))
id_emp = veh.get("id_empleado")

# --------------------------------------------------
# EMPLEADO
# --------------------------------------------------
emp = emp_by_id.get(id_emp)
nombre_emp = emp["nombre"] if emp else "No asignado"

foto_emp = None
if emp:
    f = FOTOS_EMP / f'{emp["id_empleado"]}.jpg'
    if f.exists():
        foto_emp = f

# --------------------------------------------------
# FOTO VEHÍCULO
# --------------------------------------------------
foto_veh = None
m = marca.lower()
if "paxster" in m:
    foto_veh = FOTOS_VEH / "paxster.jpg"
elif "scoobic" in m:
    foto_veh = FOTOS_VEH / "scoobic.jpg"
elif "renault" in m:
    foto_veh = FOTOS_VEH / "renault.jpg"

# --------------------------------------------------
# UI PRINCIPAL
# --------------------------------------------------
st.markdown("---")

c1, c2, c3 = st.columns([1.2, 2.2, 1.6])

with c1:
    if foto_emp:
        st.image(str(foto_emp), width=160)
    else:
        st.info("Empleado sin foto")

with c2:
    st.subheader(matricula)
    st.caption(f"{marca} {modelo}")

    st.markdown(f"🆔 **ID vehículo:** {id_veh}")
    st.markdown(f"🏷️ **Tipo:** {tipo}")
    st.markdown(f"⚙️ **Estado:** {estado}")
    st.markdown(f"🔩 **Bastidor:** {bastidor or '—'}")
    st.markdown(f"👤 **Asignado a:** {nombre_emp}")

with c3:
    if foto_veh and foto_veh.exists():
        st.image(str(foto_veh), use_container_width=True)
    else:
        st.info("Imagen vehículo no disponible")

# --------------------------------------------------
# HISTORIAL ASIGNACIONES (oculto por defecto)
# --------------------------------------------------
if st.button("Mostrar historial de asignaciones"):
    st.subheader("📝 Historial de asignaciones")
    historial = veh.get("historial_asignaciones", [])
    if not historial:
        st.info("No hay historial de asignaciones para este vehículo.")
    else:
        for h in historial:
            st.markdown(f"**Empleado:** {h['empleado_nombre']}")
            st.markdown(f"**Fecha inicio:** {h['fecha_inicio']}")
            st.markdown(f"**Fecha fin:** {h['fecha_fin']}")
            st.markdown("---")

# --------------------------------------------------
# BLOQUES FUNCIONALES (YA PREPARADOS)
# --------------------------------------------------
st.markdown("---")

st.subheader("📋 ITV")
st.info("• Fecha última ITV\n• Próxima ITV\n• Estación ITV\n• Avisos automáticos")

st.subheader("🛡️ Seguro")
st.info("• Aseguradora\n• Nº póliza\n• Vigencia\n• Documentación")

st.subheader("📂 Documentación")
st.info("• Ficha técnica\n• Permiso circulación\n• Multas")

