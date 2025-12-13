# pages/9_Dashboard.py

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date

# --------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# --------------------------------------------------
st.set_page_config(
    page_title="Dashboard — PRODE Última Milla",
    layout="wide"
)

st.title("Dashboard General — PRODE Última Milla Manager")
st.markdown("---")

# --------------------------------------------------
# RUTAS
# --------------------------------------------------
BASE = Path.cwd()
DATA = BASE / "data"

EMP_FILE = DATA / "empleados.csv"
SERV_FILE = DATA / "servicios.csv"
VEH_FILE = DATA / "vehiculos.csv"
EPI_FILE = DATA / "epis.csv"

# --------------------------------------------------
# FUNCIÓN SEGURA DE CARGA
# --------------------------------------------------
def load_csv(path):
    if path.exists():
        try:
            return pd.read_csv(path, encoding="utf-8-sig")
        except:
            return pd.DataFrame()
    return pd.DataFrame()

# --------------------------------------------------
# CARGA DE DATOS
# --------------------------------------------------
empleados = load_csv(EMP_FILE)
servicios = load_csv(SERV_FILE)
vehiculos = load_csv(VEH_FILE)
epis = load_csv(EPI_FILE)

# --------------------------------------------------
# CÁLCULOS
# --------------------------------------------------
total_emp = len(empleados)

if not empleados.empty and "estado" in empleados.columns:
    emp_activos = len(empleados[empleados["estado"].str.lower() == "activo"])
    emp_baja = total_emp - emp_activos
else:
    emp_activos = 0
    emp_baja = 0

if not servicios.empty and "estado" in servicios.columns:
    serv_activos = len(servicios[servicios["estado"].str.lower() == "activo"])
    serv_fin = len(servicios) - serv_activos
else:
    serv_activos = 0
    serv_fin = 0

if not vehiculos.empty and "estado" in vehiculos.columns:
    veh_operativos = len(vehiculos[vehiculos["estado"].str.lower() != "taller"])
    veh_taller = len(vehiculos) - veh_operativos
else:
    veh_operativos = 0
    veh_taller = 0

epi_pendientes = 0
if not epis.empty and "estado" in epis.columns:
    epi_pendientes = len(epis[epis["estado"].str.lower() != "entregado"])

# --------------------------------------------------
# TARJETAS SUPERIORES
# --------------------------------------------------
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.subheader("Empleados")
    st.metric("Activos", emp_activos)
    st.metric("De baja", emp_baja)

with c2:
    st.subheader("Servicios")
    st.metric("Activos", serv_activos)
    st.metric("Finalizados", serv_fin)

with c3:
    st.subheader("Vehículos")
    st.metric("Operativos", veh_operativos)
    st.metric("En taller", veh_taller)

with c4:
    st.subheader("EPIs")
    st.metric("Pendientes", epi_pendientes)

st.markdown("---")

# --------------------------------------------------
# SECCIÓN ESTADO GENERAL
# --------------------------------------------------
st.header("Estado general del sistema")

if emp_activos == 0:
    st.warning("No hay empleados activos registrados.")
else:
    st.success("Sistema operativo con empleados activos.")

if serv_activos == 0:
    st.info("No hay servicios activos en este momento.")

if veh_operativos == 0:
    st.warning("No hay vehículos operativos registrados.")

# --------------------------------------------------
# SECCIÓN RESUMEN
# --------------------------------------------------
st.header("Resumen rápido")

st.write("Total empleados:", total_emp)
st.write("Total servicios:", len(servicios))
st.write("Total vehículos:", len(vehiculos))
st.write("Total EPIs:", len(epis))

st.markdown("---")

# --------------------------------------------------
# DEBUG CONTROLADO (PUEDES QUITARLO CUANDO QUIERAS)
# --------------------------------------------------
with st.expander("Ver información técnica"):
    st.write("Archivo empleados:", EMP_FILE.exists())
    st.write("Archivo servicios:", SERV_FILE.exists())
    st.write("Archivo vehículos:", VEH_FILE.exists())
    st.write("Archivo EPIs:", EPI_FILE.exists())


