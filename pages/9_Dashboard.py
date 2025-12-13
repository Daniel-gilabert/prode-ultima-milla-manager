# pages/9_Dashboard.py

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date

# --------------------------------------------------
# CONFIGURACIÓN
# --------------------------------------------------
st.set_page_config(layout="wide")
st.title("Dashboard General - PRODE Ultima Milla Manager")

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
# FUNCIÓN CARGA CSV
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
# METRICAS
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
else:
    serv_activos = 0

if not vehiculos.empty and "estado" in vehiculos.columns:
    veh_operativos = len(vehiculos[vehiculos["estado"].str.lower() != "taller"])
else:
    veh_operativos = 0

epi_pendientes = 0
if not epis.empty:
    epi_pendientes = len(epis[epis["estado"].str.lower() != "entregado"])

# --------------------------------------------------
# MOSTRAR METRICAS
# --------------------------------------------------
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Empleados activos", emp_activos)
    st.metric("Empleados de baja", emp_baja)

with c2:
    st.metric("Servicios activos", serv_activos)

with c3:
    st.metric("Vehiculos operativos", veh_operativos)

with c4:
    st.metric("EPIs pendientes", epi_pendientes)

# --------------------------------------------------
# DEBUG VISUAL
# --------------------------------------------------
st.markdown("---")
st.subheader("Debug")
st.write("Empleados cargados:", len(empleados))

