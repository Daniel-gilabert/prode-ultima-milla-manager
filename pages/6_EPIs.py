# pages/6_EPIs.py
import streamlit as st
from pathlib import Path
import json
from datetime import date, datetime

# -------------------------
# Rutas y ficheros
# -------------------------
BASE_DIR = Path.cwd()
DATA_DIR = BASE_DIR / "data"
EPIS_FILE = DATA_DIR / "epis.json"
EMP_FILE = DATA_DIR / "empleados.json"
PAPELERA_FILE = DATA_DIR / "papelera.json"
DOCS_DIR = DATA_DIR / "documents" / "epis"

LOGO_PATH = Path("/mnt/data/ccc6eb30-0a2e-47ae-a93f-08dc1d55755d.jpg")  # ruta del logo que confirmaste

# Asegurar existencia de carpetas y ficheros
DATA_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)
for f in [EPIS_FILE, EMP_FILE, PAPELERA_FILE]:
    if not f.exists():
        f.write_text("[]", encoding="utf-8")

# -------------------------
# Helpers JSON / archivos
# -------------------------
def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except:
        return []

def save_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def next_id(items):
    if not items:
        return 1
    return max([int(i.get("id", 0)) for i in items]) + 1

def epis_folder(emp_id: int) -> Path:
    p = DOCS_DIR / f"emp_{emp_id}"
    p.mkdir(parents=True, exist_ok=True)
    return p

def save_epi_doc(emp_id: int, uploaded_file):
    if not uploaded_file:
        return None
    folder = epis_folder(emp_id)
    fname = uploaded_file.name.replace(" ", "_")
    dest = folder / fname
    if dest.exists():
        stamp = datetime.now().strftime("%Y%m%d%H%M%S")
        dest = folder / f"{dest.stem}_{stamp}{dest.suffix}"
    with open(dest, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return str(dest.relative_to(BASE_DIR))

# -------------------------
# Cargar datos
# -------------------------
epis = load_json(EPIS_FILE)
empleados = load_json(EMP_FILE)
papelera = load_json(PAPELERA_FILE)

# Tipos oficiales de EPI (tal como pediste)
EPI_TIPOS = [
    "Pantalón corto", "Pantalón largo", "Camiseta", "Polo",
    "Sudadera", "Chaqueta", "Chubasquero", "Calzado"
]

# Campos obligatorios por política (puedes modificar)
EPI_OBLIGATORIOS = ["Pantalón largo", "Camiseta", "Calzado", "Chubasquero"]

# Session state temporales
if "epi_edit_id" not in st.session_state:
    st.session_state.epi_edit_id = None

# -------------------------
# Interfaz
# -------------------------
st.title("🧰 Gestión de EPIs — PRODE Última Milla Manager")
if LOGO_PATH.exists():
    st.image(str(LOGO_PATH), width=160)
st.markdown("---")
st.info("Registra entrega de EPIs (tipo, talla, calzado, fecha y justificante).")

# Si no hay empleados, avisar
if not empleados:
    st.warning("No hay empleados registrados. Ve a Empleados y crea alguno antes.")
    st.stop()

# Map empleado id -> nombre
empleados_map = {e["id"]: f"{e.get('nombre','')} {e.get('apellidos','')}" for e in empleados}

# -------------------------
# Formulario: Añadir / Editar EPI
# -------------------------
st.header("➕ Registrar / Editar entrega de EPI")

edit_mode = False
epi_edit = None
if st.session_state.epi_edit_id:
    edit_mode = True
    epi_edit = next((x for x in epis if x.get("id") == st.session_state.epi_edit_id), None)

# Prefill values
pref = epi_edit.copy() if epi_edit else {}

with st.form("form_epi"):
    col1, col2 = st.columns(2)

    with col1:
        emp_sel = st.selectbox("Empleado", options=list(empleados_map.keys()), format_func=lambda x: empleados_map[x], index=list(empleados_map.keys()).index(pref.get("empleado_id")) if pref.get("empleado_id") else 0)
        tipo = st.selectbox("Tipo de EPI", EPI_TIPOS, index=EPI_TIPOS.index(pref.get("tipo")) if pref.get("tipo") in EPI_TIPOS else 0)
        entregado = st.selectbox("¿Entregado?", ["Sí", "No"], index=0 if pref.get("entregado", True) else 1)
        fecha_entrega = st.date_input("Fecha de entrega", value=datetime.fromisoformat(pref["fecha_entrega"]).date() if pref.get("fecha_entrega") else date.today())

    with col2:
        talla = st.text_input("Talla (si aplica)", value=pref.get("talla",""))
        observaciones = st.text_area("Observaciones (opcional)", value=pref.get("observaciones",""))
        justificante = st.file_uploader("Subir justificante / foto (opcional)", type=["pdf","jpg","png","jpeg"])

    submitted = st.form_submit_button("Guardar EPI")

    if submitted:
        if not emp_sel:
            st.error("Debe seleccionar un empleado.")
        else:
            record = {
                "id": pref.get("id") or next_id(epis),
                "empleado_id": int(emp_sel),
                "tipo": tipo,
                "entregado": True if entregado == "Sí" else False,
                "talla": talla or None,
                "fecha_entrega": fecha_entrega.isoformat(),
                "observaciones": observaciones or None,
                "documento": None,
                "creado_en": datetime.now().isoformat()
            }

            # guardar documento si se sube
            if justificante:
                ruta = save_epi_doc(record["empleado_id"], justificante)
                if ruta:
                    record["documento"] = {"nombre": justificante.name, "ruta": ruta}

            if edit_mode and epi_edit:
                # actualizar
                for i, r in enumerate(epis):
                    if r.get("id") == epi_edit.get("id"):
                        epis[i].update(record)
                        st.success("Registro EPI actualizado.")
                        break
            else:
                epis.append(record)
                st.success("Entrega de EPI registrada.")

            save_json(EPIS_FILE, epis)
            # limpiar edición
            st.session_state.epi_edit_id = None
            st.experimental_rerun()

st.markdown("---")

# -------------------------
# Panel resumen / alertas por empleado
# -------------------------
st.header("📣 Resumen y alertas")

# Select empleado para ver sus EPIs
emp_view = st.selectbox("Ver EPIs de empleado", options=[None] + list(empleados_map.keys()), format_func=lambda x: "— Todos —" if x is None else empleados_map[x])

filtered = [r for r in epis if (emp_view is None or r.get("empleado_id") == emp_view)]

# Mostrar alertas por empleado seleccionado
if emp_view:
    emp_epis = [r for r in epis if r.get("empleado_id") == emp_view]
    tipos_entregados = [r["tipo"] for r in emp_epis if r.get("entregado")]
    faltan = [t for t in EPI_OBLIGATORIOS if t not in tipos_entregados]
    if faltan:
        st.warning(f"⚠ Faltan EPIs obligatorios para {empleados_map[emp_view]}: {', '.join(faltan)}")
    else:
        st.success(f"✅ {empleados_map[emp_view]} tiene los EPIs obligatorios entregados.")

# Contadores globales
total_epis = len(epis)
total_entregados = len([x for x in epis if x.get("entregado")])
st.metric("Registros EPI", total_epis)
st.metric("Entregas registradas", total_entregados)

st.markdown("---")

# -------------------------
# Listado detallado
# -------------------------
st.header("📋 Listado de entregas de EPIs")

if not filtered:
    st.info("No hay registros EPI para mostrar.")
else:
    for r in sorted(filtered, key=lambda x: (x["empleado_id"], x["tipo"])):
        emp_name = empleados_map.get(r["empleado_id"], f"ID {r.get('empleado_id')}")
        with st.expander(f"{emp_name} — {r['tipo']} ({'Entregado' if r['entregado'] else 'No entregado'})"):
            st.write(f"**Empleado:** {emp_name}")
            st.write(f"**Tipo:** {r['tipo']}")
            st.write(f"**Entregado:** {'Sí' if r['entregado'] else 'No'}")
            st.write(f"**Talla:** {r.get('talla') or '-'}")
            st.write(f"**Fecha entrega:** {r.get('fecha_entrega')}")
            if r.get("observaciones"):
                st.write(f"**Observaciones:** {r.get('observaciones')}")
            if r.get("documento"):
                docpath = BASE_DIR / r["documento"]["ruta"]
                if docpath.exists():
                    with open(docpath, "rb") as f:
                        st.download_button(f"📎 Descargar {r['documento']['nombre']}", data=f.read(), file_name=r["documento"]["nombre"], key=f"dl_epi_{r['id']}")
                else:
                    st.warning("Documento asociado no encontrado en disco.")

            c1, c2, c3 = st.columns([1,1,1])
            with c1:
                if st.button(f"✏️ Editar #{r['id']}", key=f"edit_epi_{r['id']}"):
                    st.session_state.epi_edit_id = r["id"]
                    st.experimental_rerun()
            with c2:
                if st.button(f"🗑️ Mover a papelera #{r['id']}", key=f"del_epi_{r['id']}"):
                    papelera.append({"tipo":"epi","contenido": r, "fecha": datetime.now().isoformat()})
                    save_json(PAPELERA_FILE, papelera)
                    epis = [x for x in epis if x.get("id") != r.get("id")]
                    save_json(EPIS_FILE, epis)
                    st.warning("Registro EPI movido a papelera.")
                    st.experimental_rerun()
            with c3:
                # marcar como entregado/no entregado rápido
                if st.button(f"🔁 Toggle entregado #{r['id']}", key=f"toggle_{r['id']}"):
                    for i,rr in enumerate(epis):
                        if rr.get("id")==r.get("id"):
                            epis[i]["entregado"] = not bool(rr.get("entregado"))
                            save_json(EPIS_FILE, epis)
                            st.experimental_rerun()

st.markdown("---")

# -------------------------
# Funcionalidad extra: Reporte por empleado (descargar CSV simple)
# -------------------------
st.header("📥 Exportar / Informes")

emp_for_export = st.selectbox("Selecciona empleado para exportar", options=[None] + list(empleados_map.keys()), format_func=lambda x: "— Todos —" if x is None else empleados_map[x])
if st.button("Exportar CSV de EPIs"):
    import csv, io
    rows = [r for r in epis if (emp_for_export is None or r.get("empleado_id")==emp_for_export)]
    if not rows:
        st.warning("No hay registros para exportar.")
    else:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["id","empleado_id","empleado","tipo","entregado","talla","fecha_entrega","observaciones"])
        for r in rows:
            writer.writerow([r.get("id"), r.get("empleado_id"), empleados_map.get(r.get("empleado_id")), r.get("tipo"), r.get("entregado"), r.get("talla"), r.get("fecha_entrega"), r.get("observaciones")])
        st.download_button("⬇️ Descargar CSV", data=output.getvalue(), file_name=f"epis_export_{emp_for_export or 'all'}.csv", mime="text/csv")

st.markdown("---")
st.success("Módulo EPIs cargado. Usa las opciones para registrar, editar, mover a papelera y exportar.")
