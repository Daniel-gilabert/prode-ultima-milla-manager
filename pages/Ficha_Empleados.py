import streamlit as st
import json
from pathlib import Path
from datetime import date

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
st.set_page_config(page_title="Ficha de Empleados", layout="wide")

DATA_DIR = Path("data")
EMP_FILE = DATA_DIR / "empleados.json"
EPI_FILE = DATA_DIR / "epis.json"
FOTOS_EMP = DATA_DIR / "fotos_empleados"

# EPIs obligatorios (base)
EPIS_OBLIGATORIOS = [
    "Pantalón largo",
    "Camiseta",
    "Calzado de seguridad",
    "Chaleco reflectante",
    "Chubasquero",
]

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

def foto_empleado(emp_id):
    for ext in (".jpg", ".jpeg", ".png"):
        f = FOTOS_EMP / f"{emp_id}{ext}"
        if f.exists():
            return f
    return None

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
empleados = load_json(EMP_FILE)
epis = load_json(EPI_FILE)

st.title("🗂️ Ficha de Empleados")

if not empleados:
    st.warning("⚠️ No hay empleados cargados en el sistema.")
    st.stop()

# --------------------------------------------------
# SELECTOR DE EMPLEADO
# --------------------------------------------------
empleados = sorted(empleados, key=lambda e: int(e.get("id_empleado", 0)))

opciones = {
    f"{e['id_empleado']} - {e['nombre']}": e
    for e in empleados
}

seleccion = st.selectbox(
    "Selecciona un empleado",
    list(opciones.keys())
)

emp = opciones[seleccion]
emp_id = emp["id_empleado"]

# --------------------------------------------------
# FICHA BÁSICA
# --------------------------------------------------
st.divider()

col_foto, col_info = st.columns([1, 3])

with col_foto:
    foto = foto_empleado(emp_id)
    if foto:
        st.image(
            str(foto),
            width=130,          # tamaño carnet
            caption="Foto empleado"
        )
    else:
        st.info("Empleado sin foto")

with col_info:
    st.subheader(emp.get("nombre", ""))
    st.markdown(f"**🆔 ID empleado:** {emp_id}")
    st.markdown(f"**🪪 DNI:** {emp.get('dni','')}")
    st.markdown(f"**📧 Email:** {emp.get('email','')}")
    st.markdown(f"**📞 Teléfono:** {emp.get('telefono','')}")
    st.markdown(f"**💼 Puesto:** {emp.get('puesto','')}")
    st.markdown(f"**📍 Ubicación:** {emp.get('ubicacion','')}")
    st.markdown(f"**✅ Estado:** {emp.get('estado','activo')}")

# --------------------------------------------------
# EPIs DEL EMPLEADO
# --------------------------------------------------
st.divider()
st.header("🦺 EPIs (Prevención de Riesgos Laborales)")

# EPIs entregados a este empleado
epis_emp = [e for e in epis if e.get("id_empleado") == emp_id]

tipos_entregados = [e["tipo"] for e in epis_emp]

# EPIs pendientes
epis_pendientes = [
    epi for epi in EPIS_OBLIGATORIOS
    if epi not in tipos_entregados
]

# ---- Estado general
col_ok, col_bad = st.columns(2)

with col_ok:
    st.success(f"EPIs entregados: {len(tipos_entregados)}")

with col_bad:
    st.warning(f"EPIs pendientes: {len(epis_pendientes)}")

# ---- Listados
col1, col2 = st.columns(2)

with col1:
    st.subheader("✅ EPIs entregados")
    if not epis_emp:
        st.info("No hay EPIs registrados.")
    else:
        for e in epis_emp:
            st.markdown(
                f"- **{e['tipo']}** | {e['fecha_entrega']} | {e.get('observaciones','')}"
            )

with col2:
    st.subheader("❌ EPIs pendientes")
    if not epis_pendientes:
        st.success("Todos los EPIs obligatorios están entregados.")
    else:
        for p in epis_pendientes:
            st.markdown(f"- {p}")

# --------------------------------------------------
# REGISTRAR NUEVA ENTREGA DE EPI
# --------------------------------------------------
st.divider()
st.subheader("➕ Registrar nueva entrega de EPI")

with st.form("form_epi"):
    tipo = st.selectbox(
        "Tipo de EPI",
        EPIS_OBLIGATORIOS
    )
    fecha = st.date_input("Fecha de entrega", value=date.today())
    obs = st.text_input("Observaciones")

    guardar = st.form_submit_button("Guardar entrega")

if guardar:
    nuevo = {
        "id_epi": len(epis) + 1,
        "id_empleado": emp_id,
        "tipo": tipo,
        "fecha_entrega": str(fecha),
        "observaciones": obs
    }

    epis.append(nuevo)
    save_json(EPI_FILE, epis)

    st.success("EPI registrado correctamente")
    st.rerun()

# --------------------------------------------------
# FUTURO
# --------------------------------------------------
st.divider()
st.info(
    "Aquí se integrarán próximamente: formación PRL, reconocimientos médicos y documentación."
)





