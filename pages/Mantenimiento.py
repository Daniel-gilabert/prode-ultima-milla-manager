# pages/8_Mantenimiento.py

import streamlit as st
import json
from datetime import date, datetime, timedelta
from pathlib import Path

# --------------------------------------------------------
# RUTAS
# --------------------------------------------------------
BASE = Path.cwd()
DATA = BASE / "data"
VEH_FILE = DATA / "vehiculos.json"
MAN_FILE = DATA / "mantenimiento.json"
PAPELERA = DATA / "papelera.json"

DOC_DIR = DATA / "documents" / "mantenimiento"
DOC_DIR.mkdir(parents=True, exist_ok=True)

# Asegurar existencia de ficheros
for f in [VEH_FILE, MAN_FILE, PAPELERA]:
    if not f.exists():
        f.write_text("[]", encoding="utf-8")

# --------------------------------------------------------
# HELPERS
# --------------------------------------------------------
def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except:
        return []

def save_json(path, data):
    path.write_text(json.dumps(data, indent=4, ensure_ascii=False))

def next_id(records):
    if not records:
        return 1
    return max([r["id"] for r in records]) + 1

def save_doc(vehicle_id, uploaded_file):
    folder = DOC_DIR / str(vehicle_id)
    folder.mkdir(parents=True, exist_ok=True)

    name = uploaded_file.name.replace(" ", "_")
    dest = folder / name

    if dest.exists():
        stamp = datetime.now().strftime("%Y%m%d%H%M%S")
        dest = folder / f"{dest.stem}_{stamp}{dest.suffix}"

    dest.write_bytes(uploaded_file.getbuffer())
    return str(dest.relative_to(BASE))


# --------------------------------------------------------
# CARGA DE DATA
# --------------------------------------------------------
vehiculos = load_json(VEH_FILE)
mantenimientos = load_json(MAN_FILE)
papelera = load_json(PAPELERA)

# --------------------------------------------------------
# UI
# --------------------------------------------------------
st.title("🔧 Mantenimiento, Revisiones, ITV y Averías")
st.markdown("Registrar, controlar y alertar sobre necesidades de mantenimiento de los vehículos.")
st.markdown("---")

if not vehiculos:
    st.error("⚠ No hay vehículos registrados. Añade primero vehículos en el módulo correspondiente.")
    st.stop()

veh_map = {v["id"]: f"{v['matricula']} — {v['marca']}" for v in vehiculos}

# --------------------------------------------------------
# FORMULARIO AÑADIR / EDITAR MANTENIMIENTO
# --------------------------------------------------------
st.header("➕ Registrar mantenimiento / revisión / avería")

TIPOS = [
    "ITV",
    "Revisión general",
    "Cambio de aceite",
    "Neumáticos",
    "Avería mecánica",
    "Golpe / Carrocería",
    "Otro"
]

c1, c2 = st.columns(2)
with c1:
    veh_sel = st.selectbox("Vehículo", options=list(veh_map.keys()), format_func=lambda x: veh_map[x])

with c2:
    tipo = st.selectbox("Tipo de mantenimiento", TIPOS)

col3, col4 = st.columns(2)
with col3:
    fecha = st.date_input("Fecha del mantenimiento", value=date.today())

with col4:
    proxima = st.date_input("Próxima revisión (si aplica)", value=None)

taller = st.text_input("Taller (opcional)")
descripcion = st.text_area("Descripción / Observaciones")

doc = st.file_uploader("Adjuntar justificante (factura, parte, informe)", type=["pdf","jpg","jpeg","png"])

if st.button("💾 Guardar mantenimiento"):
    reg = {
        "id": next_id(mantenimientos),
        "vehiculo_id": veh_sel,
        "tipo": tipo,
        "fecha": fecha.isoformat(),
        "proxima": proxima.isoformat() if proxima else None,
        "taller": taller,
        "descripcion": descripcion,
        "archivo": save_doc(veh_sel, doc) if doc else None,
        "registrado_en": datetime.now().isoformat()
    }

    mantenimientos.append(reg)
    save_json(MAN_FILE, mantenimientos)
    st.success("Mantenimiento registrado correctamente.")
    st.experimental_rerun()

st.markdown("---")

# --------------------------------------------------------
# ALERTAS AUTOMÁTICAS
# --------------------------------------------------------
st.header("🚨 Alertas automáticas")

hoy = date.today()
alertas = []

for m in mantenimientos:
    if m["proxima"]:
        prox = datetime.fromisoformat(m["proxima"]).date()
        dias = (prox - hoy).days
        if dias <= 15:
            alertas.append((m, dias))

if alertas:
    for m, d in alertas:
        veh = veh_map[m["vehiculo_id"]]
        st.warning(f"⚠ {veh}: Próxima revisión de **{m['tipo']}** en **{d} días** ({m['proxima']})")
else:
    st.success("No hay alertas próximas.")

st.markdown("---")

# --------------------------------------------------------
# LISTADO DE MANTENIMIENTOS
# --------------------------------------------------------
st.header("📋 Historial completo de mantenimientos")

veh_filter = st.selectbox("Filtrar por vehículo", ["Todos"] + list(veh_map.keys()), format_func=lambda x: "Todos" if x == "Todos" else veh_map[x])

if veh_filter == "Todos":
    listado = mantenimientos
else:
    listado = [m for m in mantenimientos if m["vehiculo_id"] == veh_filter]

for m in sorted(listado, key=lambda x: x["fecha"], reverse=True):
    veh = veh_map[m["vehiculo_id"]]
    with st.expander(f"{veh} — {m['tipo']} — {m['fecha']}"):
        st.write(f"**Fecha:** {m['fecha']}")
        st.write(f"**Próxima:** {m.get('proxima', '-')}")
        st.write(f"**Taller:** {m.get('taller','-')}")
        st.write(f"**Descripción:** {m.get('descripcion','-')}")

        # ARCHIVO
        if m.get("archivo"):
            ruta = BASE / m["archivo"]
            if ruta.exists():
                with open(ruta, "rb") as f:
                    st.download_button("📎 Descargar documento", data=f.read(), file_name=ruta.name)
            else:
                st.error("Archivo no encontrado en disco.")

        c1, c2 = st.columns(2)

        # 🗑️ Mover a papelera
        with c1:
            if st.button(f"🗑️ Eliminar #{m['id']}", key=f"del_{m['id']}"):
                papelera.append({"tipo": "mantenimiento", "contenido": m, "fecha": datetime.now().isoformat()})
                save_json(PAPELERA, papelera)
                mantenimientos = [x for x in mantenimientos if x["id"] != m["id"]]
                save_json(MAN_FILE, mantenimientos)
                st.warning("Mantenimiento movido a papelera.")
                st.experimental_rerun()

st.markdown("---")

# --------------------------------------------------------
# BOTÓN IR A PAPELERA
# --------------------------------------------------------
if st.button("🗑️ Ver Papelera"):
    st.experimental_set_query_params(page="papelera")
    st.experimental_rerun()
