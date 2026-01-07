import streamlit as st
import json
from pathlib import Path
from datetime import date, datetime

# -----------------------------------------
# CONFIG
# -----------------------------------------
st.set_page_config(page_title="Dashboard", layout="wide")

DATA_DIR = Path("data")

EMP_FILE = DATA_DIR / "empleados.json"
EPI_FILE = DATA_DIR / "epis.json"
PRL_FILE = DATA_DIR / "prl.json"
MED_FILE = DATA_DIR / "medicos.json"

EPIS_OBLIGATORIOS = [
    "Pantalón largo",
    "Camiseta",
    "Calzado de seguridad",
    "Chaleco reflectante",
    "Chubasquero",
]

# -----------------------------------------
# HELPERS
# -----------------------------------------
def load_json(path):
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []

# -----------------------------------------
# LOAD DATA
# -----------------------------------------
empleados = load_json(EMP_FILE)
epis = load_json(EPI_FILE)
prl = load_json(PRL_FILE)
medicos = load_json(MED_FILE)

st.title("📊 Dashboard General")

if not empleados:
    st.warning("No hay empleados cargados.")
    st.stop()

hoy = date.today()

# -----------------------------------------
# EPIs INCOMPLETOS
# -----------------------------------------
empleados_epi_incompleto = []

for emp in empleados:
    emp_id = emp["id_empleado"]
    entregados = [e["tipo"] for e in epis if e["id_empleado"] == emp_id]
    faltan = [e for e in EPIS_OBLIGATORIOS if e not in entregados]
    if faltan:
        empleados_epi_incompleto.append((emp, faltan))

# -----------------------------------------
# PRL CADUCADA / PRÓXIMA
# -----------------------------------------
empleados_prl_alerta = []

for c in prl:
    if c["caduca"] and c["fecha_caducidad"]:
        cad = datetime.fromisoformat(c["fecha_caducidad"]).date()
        if cad < hoy or (cad - hoy).days <= 30:
            empleados_prl_alerta.append(c)

# -----------------------------------------
# MÉDICOS CADUCADOS / PRÓXIMOS
# -----------------------------------------
empleados_med_alerta = []

for m in medicos:
    if m["fecha_caducidad"]:
        cad = datetime.fromisoformat(m["fecha_caducidad"]).date()
        if cad < hoy or (cad - hoy).days <= 30:
            empleados_med_alerta.append(m)

# -----------------------------------------
# MÉTRICAS
# -----------------------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("👥 Empleados", len(empleados))

with col2:
    st.metric("🦺 EPIs incompletos", len(empleados_epi_incompleto))

with col3:
    st.metric("🎓 PRL en alerta", len(empleados_prl_alerta))

with col4:
    st.metric("🩺 Médicos en alerta", len(empleados_med_alerta))

# -----------------------------------------
# DETALLES
# -----------------------------------------
st.divider()

st.subheader("🦺 Empleados con EPIs incompletos")
if not empleados_epi_incompleto:
    st.success("Todos los empleados tienen EPIs completos.")
else:
    for emp, faltan in empleados_epi_incompleto:
        st.warning(
            f"**{emp['nombre']}** → faltan: {', '.join(faltan)}"
        )

st.divider()

st.subheader("🎓 Formación PRL caducada o próxima")
if not empleados_prl_alerta:
    st.success("No hay PRL en alerta.")
else:
    for c in empleados_prl_alerta:
        emp = next(e for e in empleados if e["id_empleado"] == c["id_empleado"])
        st.warning(
            f"**{emp['nombre']}** | {c['curso']} | Caduca: {c['fecha_caducidad']}"
        )

st.divider()

st.subheader("🩺 Reconocimientos médicos caducados o próximos")
if not empleados_med_alerta:
    st.success("No hay reconocimientos médicos en alerta.")
else:
    for m in empleados_med_alerta:
        emp = next(e for e in empleados if e["id_empleado"] == m["id_empleado"])
        st.error(
            f"**{emp['nombre']}** | Resultado: {m['resultado']} | Caduca: {m['fecha_caducidad']}"
        )

st.divider()
st.caption("Dashboard de control — PRODE Última Milla Manager")


