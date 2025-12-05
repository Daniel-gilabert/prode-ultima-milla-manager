# pages/7_Documentacion.py

import streamlit as st
import json
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------
# RUTAS
# ---------------------------------------------------------
BASE = Path.cwd()
DATA = BASE / "data"
DOC_FILE = DATA / "documentacion.json"
EMP_FILE = DATA / "empleados.json"
SERV_FILE = DATA / "servicios.json"
VEH_FILE = DATA / "vehiculos.json"
PAPELERA = DATA / "papelera.json"

DOCS_DIR = DATA / "documents"
DOCS_DIR.mkdir(parents=True, exist_ok=True)

for f in [DOC_FILE, EMP_FILE, SERV_FILE, VEH_FILE, PAPELERA]:
    if not f.exists():
        f.write_text("[]", encoding="utf-8")

# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------
def load_json(path, default=[]):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except:
        return default

def save_json(path, data):
    path.write_text(json.dumps(data, indent=4, ensure_ascii=False))

def next_id(rows):
    if not rows:
        return 1
    return max([r["id"] for r in rows]) + 1

def save_doc(category, uploaded_file, entity_id):
    """Guarda el documento en una carpeta según categoría y asignación."""
    folder = DOCS_DIR / category / str(entity_id)
    folder.mkdir(parents=True, exist_ok=True)

    filename = uploaded_file.name.replace(" ", "_")
    dest = folder / filename

    if dest.exists():
        stamp = datetime.now().strftime("%Y%m%d%H%M%S")
        dest = folder / f"{dest.stem}_{stamp}{dest.suffix}"

    with open(dest, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return str(dest.relative_to(BASE))

# ---------------------------------------------------------
# CARGA DE DATASETS
# ---------------------------------------------------------
docs = load_json(DOC_FILE)
empleados = load_json(EMP_FILE)
servicios = load_json(SERV_FILE)
vehiculos = load_json(VEH_FILE)
papelera = load_json(PAPELERA)

# ---------------------------------------------------------
# UI
# ---------------------------------------------------------
st.title("📁 Repositorio Central de Documentación")
st.markdown("Sube, visualiza y organiza toda la documentación de empleados, servicios y vehículos.")
st.markdown("---")

# -------------------------
# FORMULARIO DE SUBIDA
# -------------------------
st.header("➕ Subir nuevo documento")

categorias = [
    "Contrato Empleado",
    "Contrato Servicio",
    "PRL",
    "Reconocimiento Médico",
    "Documentación Vehículo",
    "Justificante Ausencia",
    "EPIs",
    "Otros"
]

col1, col2 = st.columns(2)

with col1:
    categoria = st.selectbox("Categoría del documento", categorias)

with col2:
    descripcion = st.text_input("Descripción del documento")

uploaded = st.file_uploader("📄 Subir archivo", type=["pdf", "jpg", "jpeg", "png", "docx", "xlsx"])

# Selección dinámica según categoría
if categoria in ["Contrato Empleado", "PRL", "Reconocimiento Médico", "EPIs"]:
    target_list = empleados
    target_label = "Empleado"
elif categoria == "Contrato Servicio":
    target_list = servicios
    target_label = "Servicio"
elif categoria == "Documentación Vehículo":
    target_list = vehiculos
    target_label = "Vehículo"
else:
    target_list = []
    target_label = "Asignar a (opcional)"

if target_list:
    asignacion = st.selectbox(
        f"{target_label}",
        options=[e["id"] for e in target_list],
        format_func=lambda x: next(e for e in target_list if e["id"] == x).get("nombre", f"ID {x}")
    )
else:
    asignacion = None

if st.button("💾 Guardar documento"):
    if not uploaded:
        st.error("Debes subir un archivo.")
    else:
        new = {
            "id": next_id(docs),
            "categoria": categoria,
            "descripcion": descripcion or "",
            "archivo": save_doc(categoria.replace(" ", "_"), uploaded, asignacion if asignacion else "general"),
            "asignacion": asignacion,
            "fecha_subida": datetime.now().isoformat()
        }
        docs.append(new)
        save_json(DOC_FILE, docs)
        st.success("Documento guardado correctamente.")

st.markdown("---")

# -------------------------
# LISTADO
# -------------------------
st.header("📂 Documentos existentes")

if not docs:
    st.info("No hay documentos aún.")
else:
    categoria_filtro = st.selectbox("Filtrar por categoría", ["Todas"] + categorias)

    filtrados = docs if categoria_filtro == "Todas" else [d for d in docs if d["categoria"] == categoria_filtro]

    for d in filtrados:
        with st.expander(f"{d['categoria']} — {d['descripcion']}"):
            st.write(f"**Fecha subida:** {d['fecha_subida']}")
            st.write(f"**Asignado a:** {d.get('asignacion')}")

            ruta = BASE / d["archivo"]
            if ruta.exists():
                with open(ruta, "rb") as f:
                    st.download_button("⬇️ Descargar archivo", data=f.read(), file_name=ruta.name)
            else:
                st.error("⚠ Archivo no encontrado en disco.")

            colA, colB = st.columns(2)
            with colA:
                if st.button(f"🗑️ Mover a papelera {d['id']}", key=f"del_{d['id']}"):
                    papelera.append({"tipo": "documento", "contenido": d, "fecha": datetime.now().isoformat()})
                    save_json(PAPELERA, papelera)
                    docs = [x for x in docs if x["id"] != d["id"]]
                    save_json(DOC_FILE, docs)
                    st.warning("Documento movido a papelera.")
                    st.experimental_rerun()

st.markdown("---")

# -------------------------
# IR A PAPELERA
# -------------------------
if st.button("🗑️ Ir a Papelera"):
    st.experimental_set_query_params(page="papelera")
    st.experimental_rerun()
