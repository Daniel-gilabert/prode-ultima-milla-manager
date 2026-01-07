import streamlit as st
import json
from pathlib import Path
from datetime import date, datetime

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
st.set_page_config(page_title="Ficha de Empleados", layout="wide")

DATA_DIR = Path("data")
EMP_FILE = DATA_DIR / "empleados.json"
EPI_FILE = DATA_DIR / "epis.json"
PRL_FILE = DATA_DIR / "prl.json"
MED_FILE = DATA_DIR / "medicos.json"
DOC_FILE = DATA_DIR / "documentos.json"

FOTOS_EMP = DATA_DIR / "fotos_empleados"
DOCS_PRL = DATA_DIR / "documentos_prl"
DOCS_MED = DATA_DIR / "documentos_medicos"
DOCS_EMP = DATA_DIR / "documentos_empleados"

# EPIs obligatorios
EPIS_OBLIGATORIOS = [
    "Pantalón largo",
    "Camiseta",
    "Calzado de seguridad",
    "Chaleco reflectante",
    "Chubasquero",
]

# --------------------------------------------------
# CONTROL DE ROL
# --------------------------------------------------
ES_ADMIN = st.session_state.get("rol") == "admin"

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
prl = load_json(PRL_FILE)
medicos = load_json(MED_FILE)
documentos = load_json(DOC_FILE)

st.title("🗂️ Ficha de Empleados")

if not empleados:
    st.warning("⚠️ No hay empleados cargados.")
    st.stop()

empleados = sorted(empleados, key=lambda e: int(e.get("id_empleado", 0)))

opciones = {
    f"{e['id_empleado']} - {e['nombre']}": e
    for e in empleados
}

seleccion = st.selectbox("Selecciona un empleado", list(opciones.keys()))
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
        st.image(str(foto), width=130)
    else:
        st.info("Empleado sin foto")

with col_info:
    st.subheader(emp.get("nombre", ""))
    st.markdown(f"**🆔 ID:** {emp_id}")
    st.markdown(f"**🪪 DNI:** {emp.get('dni','')}")
    st.markdown(f"**📧 Email:** {emp.get('email','')}")
    st.markdown(f"**📞 Teléfono:** {emp.get('telefono','')}")
    st.markdown(f"**💼 Puesto:** {emp.get('puesto','')}")
    st.markdown(f"**📍 Ubicación:** {emp.get('ubicacion','')}")
    st.markdown(f"**✅ Estado:** {emp.get('estado','activo')}")

# --------------------------------------------------
# EPIs
# --------------------------------------------------
st.divider()
st.header("🦺 EPIs")

epis_emp = [e for e in epis if e["id_empleado"] == emp_id]
entregados = [e["tipo"] for e in epis_emp]
pendientes = [e for e in EPIS_OBLIGATORIOS if e not in entregados]

col1, col2 = st.columns(2)

with col1:
    st.subheader("Entregados")
    if not epis_emp:
        st.info("No hay EPIs registrados.")
    else:
        for e in epis_emp:
            st.markdown(f"- **{e['tipo']}** | {e['fecha_entrega']}")

with col2:
    st.subheader("Pendientes")
    if not pendientes:
        st.success("Todos los EPIs entregados")
    else:
        for p in pendientes:
            st.markdown(f"- {p}")

if ES_ADMIN:
    with st.form("nuevo_epi"):
        st.subheader("➕ Registrar EPI")
        tipo = st.selectbox("Tipo", EPIS_OBLIGATORIOS)
        fecha = st.date_input("Fecha", value=date.today())
        obs = st.text_input("Observaciones")
        if st.form_submit_button("Guardar EPI"):
            epis.append({
                "id_epi": len(epis) + 1,
                "id_empleado": emp_id,
                "tipo": tipo,
                "fecha_entrega": str(fecha),
                "observaciones": obs
            })
            save_json(EPI_FILE, epis)
            st.success("EPI registrado")
            st.rerun()
else:
    st.info("🔒 Solo el administrador puede registrar EPIs")

# --------------------------------------------------
# FORMACIÓN PRL
# --------------------------------------------------
st.divider()
st.header("🎓 Formación PRL")

prl_emp = [c for c in prl if c["id_empleado"] == emp_id]
hoy = date.today()

if not prl_emp:
    st.info("No hay cursos PRL registrados.")
else:
    for c in prl_emp:
        estado = "✅ Vigente"
        if c["caduca"] and c["fecha_caducidad"]:
            cad = datetime.fromisoformat(c["fecha_caducidad"]).date()
            if cad < hoy:
                estado = "❌ Caducado"
            elif (cad - hoy).days <= 30:
                estado = "⚠️ Próximo a caducar"
        st.markdown(f"- **{c['curso']}** | {c['fecha']} | {estado}")

if ES_ADMIN:
    with st.form("nuevo_prl"):
        st.subheader("➕ Registrar curso PRL")
        curso = st.text_input("Curso")
        fecha = st.date_input("Fecha realización", value=date.today())
        caduca = st.checkbox("¿Caduca?")
        fecha_cad = st.date_input("Fecha caducidad") if caduca else None
        doc = st.file_uploader("Certificado (PDF)", type=["pdf"])
        obs = st.text_input("Observaciones")
        if st.form_submit_button("Guardar curso PRL"):
            nombre_doc = ""
            if doc:
                ruta = DOCS_PRL / str(emp_id)
                ruta.mkdir(parents=True, exist_ok=True)
                nombre_doc = doc.name
                (ruta / nombre_doc).write_bytes(doc.read())
            prl.append({
                "id_prl": len(prl) + 1,
                "id_empleado": emp_id,
                "curso": curso,
                "fecha": str(fecha),
                "caduca": caduca,
                "fecha_caducidad": str(fecha_cad) if caduca else "",
                "documento": nombre_doc,
                "observaciones": obs
            })
            save_json(PRL_FILE, prl)
            st.success("Curso PRL registrado")
            st.rerun()
else:
    st.info("🔒 Solo el administrador puede registrar formación PRL")

# --------------------------------------------------
# RECONOCIMIENTOS MÉDICOS
# --------------------------------------------------
st.divider()
st.header("🩺 Reconocimientos médicos")

med_emp = [m for m in medicos if m["id_empleado"] == emp_id]

if not med_emp:
    st.info("No hay reconocimientos médicos.")
else:
    for m in med_emp:
        estado = "✅ Vigente"
        if m["fecha_caducidad"]:
            cad = datetime.fromisoformat(m["fecha_caducidad"]).date()
            if cad < hoy:
                estado = "❌ Caducado"
            elif (cad - hoy).days <= 30:
                estado = "⚠️ Próximo a caducar"
        st.markdown(f"- **{m['fecha']}** | {m['resultado']} | {estado}")

if ES_ADMIN:
    with st.form("nuevo_medico"):
        st.subheader("➕ Registrar reconocimiento médico")
        fecha = st.date_input("Fecha", value=date.today())
        resultado = st.selectbox("Resultado", ["Apto", "Apto con limitaciones", "No apto"])
        caduca = st.checkbox("¿Tiene caducidad?")
        fecha_cad = st.date_input("Fecha caducidad") if caduca else None
        doc = st.file_uploader("Informe médico (PDF)", type=["pdf"])
        obs = st.text_input("Observaciones")
        if st.form_submit_button("Guardar reconocimiento"):
            nombre_doc = ""
            if doc:
                ruta = DOCS_MED / str(emp_id)
                ruta.mkdir(parents=True, exist_ok=True)
                nombre_doc = doc.name
                (ruta / nombre_doc).write_bytes(doc.read())
            medicos.append({
                "id_medico": len(medicos) + 1,
                "id_empleado": emp_id,
                "fecha": str(fecha),
                "resultado": resultado,
                "fecha_caducidad": str(fecha_cad) if caduca else "",
                "documento": nombre_doc,
                "observaciones": obs
            })
            save_json(MED_FILE, medicos)
            st.success("Reconocimiento médico registrado")
            st.rerun()
else:
    st.info("🔒 Solo el administrador puede registrar reconocimientos médicos")

# --------------------------------------------------
# DOCUMENTACIÓN
# --------------------------------------------------
st.divider()
st.header("📎 Documentación")

docs_emp = [d for d in documentos if d["id_empleado"] == emp_id]

if not docs_emp:
    st.info("No hay documentación.")
else:
    for d in docs_emp:
        st.markdown(f"- **{d['tipo']}** | {d['nombre']} | {d['fecha']}")

if ES_ADMIN:
    with st.form("nuevo_documento"):
        st.subheader("➕ Añadir documento")
        tipo = st.selectbox("Tipo", ["Contrato", "Certificado", "Anexo", "Sanción", "Otro"])
        nombre = st.text_input("Nombre / descripción")
        fecha = st.date_input("Fecha", value=date.today())
        archivo = st.file_uploader("Archivo", type=["pdf", "doc", "docx", "jpg", "png"])
        obs = st.text_input("Observaciones")
        if st.form_submit_button("Guardar documento"):
            nombre_archivo = ""
            if archivo:
                ruta = DOCS_EMP / str(emp_id)
                ruta.mkdir(parents=True, exist_ok=True)
                nombre_archivo = archivo.name
                (ruta / nombre_archivo).write_bytes(archivo.read())
            documentos.append({
                "id_documento": len(documentos) + 1,
                "id_empleado": emp_id,
                "tipo": tipo,
                "nombre": nombre,
                "fecha": str(fecha),
                "archivo": nombre_archivo,
                "observaciones": obs
            })
            save_json(DOC_FILE, documentos)
            st.success("Documento guardado")
            st.rerun()
else:
    st.info("🔒 Solo el administrador puede subir documentación")


