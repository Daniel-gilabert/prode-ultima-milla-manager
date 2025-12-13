# pages/9_Dashboard.py

import streamlit as st
import pandas as pd
from datetime import date, datetime
from pathlib import Path

# --------------------------------------------------------------
# CONFIGURACIÓN GENERAL
# --------------------------------------------------------------
st.set_page_config(layout="wide")
st.title("📊 Dashboard General — PRODE Última Milla Manager")

# --------------------------------------------------------------
# RUTAS
# --------------------------------------------------------------
BASE = Path.cwd()
DATA = BASE / "data"

EMP_FILE = DATA / "empleados.csv"
SERV_FILE = DATA / "servicios.csv"
VEH_FILE = DATA / "vehiculos.csv"
AUS_FILE = DATA / "ausencias.csv"
EPI_FILE = DATA / "epis.csv"
MAN_FILE = DATA / "mantenimiento.csv"

# --------------------------------------------------------------
# FUNCIÓN DE CARGA SEGURA DE CSV
# --------------------------------------------------------------
def load_csv(path):
    if path.exists():
        try:
            return pd.read_csv(path, encoding="utf-8-sig")
        except Exception as e:
            st.error(f"❌ Error leyendo {path.name}")
            st.exception(e)
            return pd.DataFrame()
    return pd.DataFrame()

# --------------------------------------------------------------
# CARGA DE DATOS
# --------------------------------------------------------------
empleados = load_csv(EMP_FILE)
servicios = load_csv(SERV_FILE)
vehiculos = load_csv(VEH_FILE)
ausencias = load_csv(AUS_FILE)
epis = load_csv(EPI_FILE)
mantenimientos = load_csv(MAN_FILE)

st.markdown("---")

# --------------------------------------------------------------
# MÉTRICAS / CARDS
# --------------------------------------------------------------

# EMPLEADOS
total_emp = len(empleados)

if not empleados.empty and "estado" in empleados.columns:
    emp_activos = len(empleados[empleados["estado"].str.lower() == "activo"])
    emp_baja = total_emp - emp_activos
else:
    emp_activos = 0
    emp_baja = 0

# SERVICIOS
if not servicios.empty and "estado" in servicios.columns:
    serv_activos = len(servicios[servicios["estado"].str.lower() == "activo"])
    serv_fin = len(servicios) - serv_activos
else:
    serv_activos = 0
    serv_fin = 0

# VEHÍCULOS
if not vehiculos.empty and "estado" in vehiculos.columns:
    veh_operativos = len(vehiculos[vehiculos["estado"].str.lower() != "taller"])
    veh_taller = len(vehiculos) - veh_operativos
else:
    veh_operativos = 0
    veh_taller = 0

# ITV PRÓXIMAS (<20 DÍAS)
hoy = date.today()
itv_proximas = []

if not mantenimientos.empty:
    for _, m in mantenimientos.iterrows():
        if (
            str(m.get("tipo", "")).lower() == "itv"
            and pd.notna(m.get("proxima_revision"))
        ):
            try:
                prox = pd.to_datetime(m["proxima_revision"]).date()
                if 0 <= (prox - hoy).days <= 20:
                    itv_proximas.append(m)
            except:
                pass

# EPIs PENDIENTES
epi_pendientes = []

if not epis.empty and not empleados.empty:
    epi_oblig = ["pantalon", "camiseta", "calzado", "chubasquero"]

    for _, emp in empleados.iterrows():
        entregados = epis[
            (epis.get("id_empleado") == emp["id_empleado"]) &
            (epis.get("estado", "").str.lower() == "entregado")
        ]

        tipos_entregados = [
            str(t).lower() for t in entregados.get("nombre_epi", [])
        ]

        faltan = [e for e in epi_oblig if e not in tipos_entregados]

        if faltan:
            epi_pendientes.append(emp)

# AUSENCIAS HOY
ausencias_hoy = []

if not ausencias.empty:
    for _, a in ausencias.iterrows():
        try:
            desde = pd.to_datetime(a["desde"]).date()
            hasta = pd.to_datetime(a["hasta"]).date()
            if desde <= hoy <= hasta:
                ausencias_hoy.append(a)
        except:
            pass

# --------------------------------------------------------------
# MOSTRAR CARDS
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
# AUSENCIAS HOY
# --------------------------------------------------------------
st.header("🏖️ Empleados ausentes hoy")

if not ausencias_hoy:
    st.success("Todos los empleados están activos hoy.")
else:
    for a in ausencias_hoy:
        st.warning(f"Empleado ID {a.get('id_empleado')} — {a.get('motivo')}")

st.markdown("---")

# --------------------------------------------------------------
# ITV PRÓXIMAS
# --------------------------------------------------------------
st.header("🚨 ITV Próximas (menos de 20 días)")

if not itv_proximas:
    st.success("No hay ITV próximas.")
else:
    for m in itv_proximas:
        st.error(
            f"Vehículo ID {m.get('id_vehiculo')} — "
            f"Fecha: {m.get('proxima_revision')}"
        )

st.markdown("---")

# --------------------------------------------------------------
# EPIs PENDIENTES
# --------------------------------------------------------------
st.header("🧰 EPIs pendientes por empleado")

if not epi_pendientes:
    st.success("Todos los empleados tienen EPIs obligatorios.")
else:
    for emp in epi_pendientes:
        st.warning(f"{emp['nombre']} — EPIs pendientes")

st.markdown("---")

# --------------------------------------------------------------
# DEBUG (PUEDES BORRARLO CUANDO QUIERAS)
# --------------------------------------------------------------
st.subheader("🧪 Debug rápido")
st.write("Empleados cargados:", len(empleados))

- [Documentación](?page=documentacion)
- [Papelera](?page=papelera)
""")
