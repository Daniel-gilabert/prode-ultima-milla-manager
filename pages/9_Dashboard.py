# pages/9_Dashboard.py

import streamlit as st
import json
from datetime import date, datetime
from pathlib import Path

# --------------------------------------------------------------
# RUTAS Y ARCHIVOS
# --------------------------------------------------------------
BASE = Path.cwd()
DATA = BASE / "data"

EMP_FILE = DATA / "empleados.json"
SERV_FILE = DATA / "servicios.json"
VEH_FILE = DATA / "vehiculos.json"
AUS_FILE = DATA / "ausencias.json"
EPI_FILE = DATA / "epis.json"
MAN_FILE = DATA / "mantenimiento.json"

LOGO_PATH = Path("/mnt/data/ccc6eb30-0a2e-47ae-a93f-08dc1d55755d.jpg")

FILES = [EMP_FILE, SERV_FILE, VEH_FILE, AUS_FILE, EPI_FILE, MAN_FILE]

def load(path):
    if path.exists():
        try:
            return json.loads(path.read_text())
        except:
            return []
    return []

# --------------------------------------------------------------
# CARGA DE DATA
# --------------------------------------------------------------
empleados = load(EMP_FILE)
servicios = load(SERV_FILE)
vehiculos = load(VEH_FILE)
ausencias = load(AUS_FILE)
epis = load(EPI_FILE)
mantenimientos = load(MAN_FILE)

# --------------------------------------------------------------
# UI PRINCIPAL
# --------------------------------------------------------------
st.set_page_config(layout="wide")
st.title("📊 Dashboard General — PRODE Última Milla Manager")

if LOGO_PATH.exists():
    st.image(str(LOGO_PATH), width=170)

st.markdown("---")

# --------------------------------------------------------------
# CARDS / INDICADORES RÁPIDOS
# --------------------------------------------------------------

# EMPLEADOS
total_emp = len(empleados)
emp_activos = len([e for e in empleados if not e.get("fecha_baja")])
emp_baja = total_emp - emp_activos

# SERVICIOS
serv_activos = len([s for s in servicios if not s.get("fin")])
serv_fin = len(servicios) - serv_activos

# VEHÍCULOS
veh_operativos = len([v for v in vehiculos if v.get("estado") != "Taller"])
veh_taller = len(vehiculos) - veh_operativos

# MANTENIMIENTO (ITV próximas)
hoy = date.today()
itv_proximas = [
    m for m in mantenimientos 
    if m["tipo"] == "ITV" and m["proxima"] and
       (datetime.fromisoformat(m["proxima"]).date() - hoy).days <= 20
]

# EPIs pendientes
epi_oblig = ["Pantalón largo","Camiseta","Calzado","Chubasquero"]
epi_pendientes = []

for e in empleados:
    entregados = [r["tipo"] for r in epis if r["empleado_id"] == e["id"] and r["entregado"]]
    faltan = [t for t in epi_oblig if t not in entregados]
    if faltan:
        epi_pendientes.append({"emp": e, "faltan": faltan})

# AUSENCIAS HOY
ausencias_hoy = [
    a for a in ausencias
    if datetime.fromisoformat(a["desde"]).date() <= hoy <= datetime.fromisoformat(a["hasta"]).date()
]

# --------------------------------------------------------------
# MOSTRAR LOS CARDS
# --------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("👥 Empleados activos", emp_activos)
    st.metric("Empleados de baja", emp_baja)

with col2:
    st.metric("📌 Servicios activos", serv_activos)
    st.metric("Servicios finalizados", serv_fin)

with col3:
    st.metric("🚗 Vehículos operativos", veh_operativos)
    st.metric("En taller", veh_taller)

with col4:
    st.metric("📅 ITV próximas (<20 días)", len(itv_proximas))
    st.metric("📦 EPIs pendientes", len(epi_pendientes))

st.markdown("---")

# --------------------------------------------------------------
# SECCIÓN DETALLADA: AUSENCIAS HOY
# --------------------------------------------------------------
st.header("🏖️ Empleados ausentes hoy")

if not ausencias_hoy:
    st.success("Todos los empleados están activos hoy.")
else:
    for a in ausencias_hoy:
        empleado = next(e for e in empleados if e["id"] == a["empleado_id"])
        st.warning(f"**{empleado['nombre']} {empleado['apellidos']}** — {a['motivo']}")

st.markdown("---")

# --------------------------------------------------------------
# SECCIÓN: ITV PRÓXIMAS
# --------------------------------------------------------------
st.header("🚨 ITV Próximas (menos de 20 días)")

if not itv_proximas:
    st.success("No hay ITV próximas.")
else:
    for m in itv_proximas:
        veh = next(v for v in vehiculos if v["id"] == m["vehiculo_id"])
        prox = datetime.fromisoformat(m["proxima"]).date()
        dias = (prox - hoy).days
        st.error(f"**{veh['matricula']} — {veh['marca']}** | Falta: {dias} días | Fecha: {prox}")

st.markdown("---")

# --------------------------------------------------------------
# SECCIÓN: EPIs PENDIENTES
# --------------------------------------------------------------
st.header("🧰 EPIs pendientes por empleado")

if not epi_pendientes:
    st.success("Todos los empleados tienen EPIs obligatorios entregados.")
else:
    for e in epi_pendientes:
        emp = e["emp"]
        faltan = ", ".join(e["faltan"])
        st.warning(f"**{emp['nombre']} {emp['apellidos']}** — faltan: {faltan}")

st.markdown("---")

# --------------------------------------------------------------
# BOTONES DE ACCESO RÁPIDO A LOS MÓDULOS
# --------------------------------------------------------------
st.header("🔗 Accesos directos")

url_base = st.experimental_get_query_params()

st.markdown("""
### 👉 Navega rápidamente:
- [Empleados](?page=empleados)
- [Servicios](?page=servicios)
- [Vehículos](?page=vehiculos)
- [Ausencias](?page=ausencias)
- [EPIs](?page=epis)
- [Mantenimiento](?page=mantenimiento)
- [Documentación](?page=documentacion)
- [Papelera](?page=papelera)
""")
