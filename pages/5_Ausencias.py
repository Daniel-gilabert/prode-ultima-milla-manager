import streamlit as st
import json
from datetime import date, datetime, timedelta
from pathlib import Path

# -----------------------------
# Archivos JSON
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
AUS_FILE = BASE_DIR / "data" / "ausencias.json"
EMP_FILE = BASE_DIR / "data" / "empleados.json"
PAPELERA_FILE = BASE_DIR / "data" / "papelera.json"

# -----------------------------
# Helpers
# -----------------------------
def load_json(path, default):
    if path.exists():
        try:
            return json.loads(path.read_text())
        except:
            return default
    return default

def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=4))

def next_id(lista):
    if not lista:
        return 1
    return max(e["id"] for e in lista) + 1

# -----------------------------
# Load Data
# -----------------------------
empleados = load_json(EMP_FILE, [])
ausencias = load_json(AUS_FILE, [])
papelera = load_json(PAPELERA_FILE, [])

# -----------------------------
# UI
# -----------------------------
st.title("🏖️ Gestión de Ausencias (Vacaciones / Permisos / Bajas)")
st.markdown("Registra ausencias por empleado con rangos de fechas, justificantes y motivo.")

st.markdown("---")

# -----------------------------
# NUEVA AUSENCIA
# -----------------------------
st.header("➕ Registrar nueva ausencia")

if not empleados:
    st.warning("⚠ No hay empleados registrados.")
    st.stop()

nombres = {e["id"]: f"{e['nombre']} {e['apellidos']}" for e in empleados}

col1, col2 = st.columns(2)

with col1:
    emp_sel = st.selectbox("Empleado", list(nombres.keys()), format_func=lambda x: nombres[x])

with col2:
    motivo = st.selectbox("Motivo", ["Vacaciones", "Permiso", "Baja médica"])

col3, col4 = st.columns(2)
with col3:
    desde = st.date_input("Desde", value=date.today())

with col4:
    hasta = st.date_input("Hasta", value=date.today() + timedelta(days=1))

if hasta < desde:
    st.error("La fecha FIN no puede ser menor que la fecha INICIO.")
    st.stop()

st.markdown("### 🧾 Justificante (opcional)")
justificante = st.file_uploader("Subir justificante (PDF/JPG/PNG)", type=["pdf", "jpg", "jpeg", "png"])

if st.button("💾 Registrar ausencia"):
    nueva = {
        "id": next_id(ausencias),
        "empleado_id": emp_sel,
        "motivo": motivo,
        "desde": desde.isoformat(),
        "hasta": hasta.isoformat(),
        "justificante": None
    }

    # Guardar justificante
    if justificante:
        carpeta = BASE_DIR / "documentos" / "ausencias" / str(nueva["id"])
        carpeta.mkdir(parents=True, exist_ok=True)
        filepath = carpeta / justificante.name
        filepath.write_bytes(justificante.getvalue())
        nueva["justificante"] = str(filepath.relative_to(BASE_DIR))

    ausencias.append(nueva)
    save_json(AUS_FILE, ausencias)
    st.success("Ausencia registrada con éxito.")

st.markdown("---")

# -----------------------------
# LISTADO DE AUSENCIAS
# -----------------------------
st.header("📋 Ausencias registradas")

if not ausencias:
    st.info("No hay ausencias registradas.")
else:
    for a in ausencias:
        empleado = nombres.get(a["empleado_id"], "Empleado desconocido")
        with st.expander(f"{empleado} — {a['motivo']}"):
            st.write(f"**Desde:** {a['desde']}")
            st.write(f"**Hasta:** {a['hasta']}")
            st.write(f"**Motivo:** {a['motivo']}")

            # JUSTIFICANTE
            if a.get("justificante"):
                ruta = BASE_DIR / a["justificante"]
                if ruta.exists():
                    with open(ruta, "rb") as f:
                        st.download_button(
                            "📄 Descargar justificante",
                            data=f.read(),
                            file_name=ruta.name,
                        )
                else:
                    st.warning("Justificante no encontrado.")
            else:
                st.write("_Sin justificante_")

            colA, colB = st.columns(2)

            # -----------------------------
            # EDITAR AUSENCIA
            # -----------------------------
            with colA:
                if st.button(f"✏️ Editar {a['id']}", key=f"edit_{a['id']}"):
                    st.session_state.edit_aus_id = a["id"]
                    st.experimental_rerun()

            # -----------------------------
            # MOVER A PAPELERA
            # -----------------------------
            with colB:
                if st.button(f"🗑️ Borrar {a['id']}", key=f"del_{a['id']}"):
                    papelera.append({
                        "tipo": "ausencia",
                        "contenido": a,
                        "fecha": datetime.now().isoformat()
                    })
                    save_json(PAPELERA_FILE, papelera)

                    ausencias = [x for x in ausencias if x["id"] != a["id"]]
                    save_json(AUS_FILE, ausencias)

                    st.warning("La ausencia se movió a la PAPELERA.")
                    st.experimental_rerun()

st.markdown("---")

# -----------------------------
# MODO EDICIÓN
# -----------------------------
if "edit_aus_id" in st.session_state:
    aus_id = st.session_state.edit_aus_id
    actual = next(a for a in ausencias if a["id"] == aus_id)

    st.header(f"✏️ Editando ausencia #{aus_id}")

    col1, col2 = st.columns(2)
    with col1:
        emp_edit = st.selectbox(
            "Empleado",
            list(nombres.keys()),
            index=list(nombres.keys()).index(actual["empleado_id"]),
            key="emp_edit"
        )

    with col2:
        motivo_edit = st.selectbox(
            "Motivo",
            ["Vacaciones", "Permiso", "Baja médica"],
            index=["Vacaciones", "Permiso", "Baja médica"].index(actual["motivo"]),
            key="mot_edit"
        )

    col3, col4 = st.columns(2)
    with col3:
        desde_edit = st.date_input("Desde", value=datetime.fromisoformat(actual["desde"]).date())

    with col4:
        hasta_edit = st.date_input("Hasta", value=datetime.fromisoformat(actual["hasta"]).date())

    justificante_edit = st.file_uploader("Actualizar justificante", type=["pdf", "jpg", "jpeg", "png"])

    if st.button("💾 Guardar cambios"):
        actual["empleado_id"] = emp_edit
        actual["motivo"] = motivo_edit
        actual["desde"] = desde_edit.isoformat()
        actual["hasta"] = hasta_edit.isoformat()

        if justificante_edit:
            carpeta = BASE_DIR / "documentos" / "ausencias" / str(actual["id"])
            carpeta.mkdir(parents=True, exist_ok=True)
            filepath = carpeta / justificante_edit.name
            filepath.write_bytes(justificante_edit.getvalue())
            actual["justificante"] = str(filepath.relative_to(BASE_DIR))

        save_json(AUS_FILE, ausencias)
        st.success("Ausencia actualizada.")
        del st.session_state.edit_aus_id
        st.experimental_rerun()

    if st.button("❌ Cancelar edición"):
        del st.session_state.edit_aus_id
        st.experimental_rerun()

st.markdown("---")

# BOTÓN IR A PAPELERA
if st.button("🗑️ Ver Papelera"):
    st.experimental_set_query_params(page="papelera")
    st.experimental_rerun()
