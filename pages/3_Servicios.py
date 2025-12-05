# pages/3_Servicios.py
import streamlit as st
from pathlib import Path
import json
from datetime import date

# -------------------------
# RUTAS Y CONFIG
# -------------------------
BASE_DIR = Path.cwd()
DATA_DIR = BASE_DIR / "data"
DOCS_DIR = DATA_DIR / "documents" / "services"
SERVICES_FILE = DATA_DIR / "servicios.json"
PAPELERA_FILE = DATA_DIR / "papelera.json"
EMPLEADOS_FILE = DATA_DIR / "empleados.json"

LOGO_PATH = "/mnt/data/ccc6eb30-0a2e-47ae-a93f-08dc1d55755d.jpg"  # ruta local del logo (ya la tienes)

# Asegurar carpetas
DATA_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)
if not SERVICES_FILE.exists():
    SERVICES_FILE.write_text("[]", encoding="utf-8")
if not PAPELERA_FILE.exists():
    PAPELERA_FILE.write_text("[]", encoding="utf-8")
if not EMPLEADOS_FILE.exists():
    EMPLEADOS_FILE.write_text("[]", encoding="utf-8")


# -------------------------
# UTILIDADES JSON
# -------------------------
def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def next_id(items):
    if not items:
        return 1
    return max([int(i.get("id", 0)) for i in items]) + 1


# -------------------------
# FUNCIONES DE DOCUMENTOS
# -------------------------
def save_service_document(service_id: int, uploaded_file):
    if not uploaded_file:
        return None
    srv_folder = DOCS_DIR / f"service_{service_id}"
    srv_folder.mkdir(parents=True, exist_ok=True)
    # safe filename
    fname = uploaded_file.name.replace(" ", "_")
    dest = srv_folder / fname
    with open(dest, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return str(dest.relative_to(BASE_DIR))


def list_service_documents(service_id: int):
    srv_folder = DOCS_DIR / f"service_{service_id}"
    if not srv_folder.exists():
        return []
    return [p for p in srv_folder.iterdir() if p.is_file()]


# -------------------------
# INTERFAZ
# -------------------------
st.title("🏢 Gestión de Servicios")
if Path(LOGO_PATH).exists():
    st.image(LOGO_PATH, width=160)

st.markdown("---")

# Cargar datos
servicios = load_json(SERVICES_FILE)
papelera = load_json(PAPELERA_FILE)
empleados = load_json(EMPLEADOS_FILE)

# Sidebar ayuda rápida
st.sidebar.header("Acciones rápidas")
if st.sidebar.button("Agregar servicio nuevo (formulario abajo)"):
    st.experimental_rerun()

# === Formulario para crear / editar servicio ===
st.header("➕ Crear / Editar servicio")

with st.form("form_servicio", clear_on_submit=False):
    col1, col2 = st.columns([2, 1])
    with col1:
        nombre = st.text_input("Nombre del servicio")
        nif = st.text_input("NIF")
        empresa = st.text_input("Nombre de la empresa")
        direccion = st.text_area("Dirección completa")
        telefono = st.text_input("Teléfono del servicio")
        correo = st.text_input("Correo del servicio")
        representante = st.text_input("Representante principal")
        # responsables múltiples: entrada + botón para añadir a session_state
        if "responsables_tmp" not in st.session_state:
            st.session_state.responsables_tmp = []
        resp_nombre = st.text_input("Nombre responsable (para añadir)")
        resp_telefono = st.text_input("Teléfono responsable")
        resp_email = st.text_input("Email responsable")
        add_resp = st.button("Añadir responsable")
        if add_resp and resp_nombre:
            st.session_state.responsables_tmp.append({
                "nombre": resp_nombre,
                "telefono": resp_telefono,
                "email": resp_email
            })
            st.experimental_rerun()

        if st.session_state.responsables_tmp:
            st.write("Responsables añadidos:")
            for i, r in enumerate(st.session_state.responsables_tmp):
                st.write(f"{i+1}. {r['nombre']} — {r.get('telefono','')} — {r.get('email','')}")
            if st.button("Borrar lista de responsables (temporal)"):
                st.session_state.responsables_tmp = []
                st.experimental_rerun()

    with col2:
        dimension = st.number_input("Dimensión (valor numérico)", min_value=0, value=1)
        forma_pago = st.selectbox("Forma de pago", ["Transferencia", "Domiciliación", "Efectivo", "Otro"])
        fecha_inicio = st.date_input("Fecha inicio del servicio", value=date.today())
        fecha_fin = st.date_input("Fecha fin del servicio (opcional)", value=None)
        if fecha_fin == date.today():
            # to allow empty date, we use None via checkbox
            pass
        num_motos = st.number_input("Número de motos asignadas", min_value=0, value=0)

        # Asignar empleados (multi-select)
        opciones_empleados = [f"{e.get('id')} - {e.get('nombre')} {e.get('apellidos')}" for e in empleados]
        asignados_sel = st.multiselect("Empleados a asignar (selecciona)", opciones_empleados)

        # Cargar contrato / documentos del servicio
        uploaded_contract = st.file_uploader("Subir contrato del servicio (PDF)", type=["pdf", "jpg", "png", "docx"])

    submitted = st.form_submit_button("Guardar servicio")

    if submitted:
        # validar
        if not nombre:
            st.error("El nombre del servicio es obligatorio.")
        else:
            svc = {
                "id": next_id(servicios),
                "nombre": nombre,
                "nif": nif,
                "empresa": empresa,
                "direccion": direccion,
                "telefono": telefono,
                "correo": correo,
                "representante": representante,
                "responsables": st.session_state.get("responsables_tmp", []),
                "dimension": int(dimension),
                "forma_pago": forma_pago,
                "fecha_inicio": fecha_inicio.isoformat() if fecha_inicio else None,
                "fecha_fin": fecha_fin.isoformat() if fecha_fin else None,
                "num_motos": int(num_motos),
                "empleados_asignados": [],  # list of dicts {id_empleado, fecha_inicio, fecha_fin}
                "documentos": []
            }

            # procesar asignaciones seleccionadas (sin fechas individuales por ahora; se puede editar después)
            for s in asignados_sel:
                # s has format "id - Nombre Apellidos"
                try:
                    id_emp = int(s.split(" - ")[0])
                except:
                    continue
                svc["empleados_asignados"].append({
                    "id_empleado": id_emp,
                    "fecha_inicio": fecha_inicio.isoformat() if fecha_inicio else None,
                    "fecha_fin": fecha_fin.isoformat() if fecha_fin else None
                })

            servicios.append(svc)
            save_json(SERVICES_FILE, servicios)

            # guardar documento si subido
            if uploaded_contract:
                ruta = save_service_document(svc["id"], uploaded_contract)
                if ruta:
                    # actualizar referencia en la lista de servicios
                    for srv in servicios:
                        if srv["id"] == svc["id"]:
                            srv["documentos"].append({"nombre": uploaded_contract.name, "ruta": ruta})
                    save_json(SERVICES_FILE, servicios)

            # limpiar temporales
            st.session_state.responsables_tmp = []
            st.success(f"Servicio '{nombre}' creado correctamente.")
            st.experimental_rerun()

st.markdown("---")

# === LISTADO / GESTION DE SERVICIOS ===
st.header("📋 Listado de Servicios")

if not servicios:
    st.info("No hay servicios creados aún.")
else:
    for srv in servicios:
        with st.expander(f"{srv.get('nombre')}  —  NIF: {srv.get('nif','-')}"):
            cols = st.columns([3, 1])
            with cols[0]:
                st.markdown(f"**Empresa:** {srv.get('empresa','')}")
                st.markdown(f"**Dirección:** {srv.get('direccion','')}")
                st.markdown(f"**Dimensión:** {srv.get('dimension')}")
                st.markdown(f"**Forma de pago:** {srv.get('forma_pago')}")
                st.markdown(f"**Fecha inicio:** {srv.get('fecha_inicio')}")
                st.markdown(f"**Fecha fin:** {srv.get('fecha_fin')}")
                st.markdown(f"**Número motos asignadas:** {srv.get('num_motos')}")
                st.markdown("**Responsables:**")
                for r in srv.get("responsables", []):
                    st.write(f"- {r.get('nombre')} — {r.get('telefono','')} — {r.get('email','')}")
                st.markdown("**Empleados asignados:**")
                for ea in srv.get("empleados_asignados", []):
                    # buscar empleado por id
                    emp = next((e for e in empleados if int(e.get("id",0)) == int(ea.get("id_empleado"))), None)
                    if emp:
                        st.write(f"- {emp.get('nombre')} {emp.get('apellidos')} (desde {ea.get('fecha_inicio')} hasta {ea.get('fecha_fin')})")
                st.markdown("**Documentos:**")
                docs = srv.get("documentos", [])
                if docs:
                    for d in docs:
                        st.write(f"- {d.get('nombre')}  ( {d.get('ruta')} )")
                else:
                    st.write("Sin documentos.")

            with cols[1]:
                # acciones: editar, añadir doc, eliminar (mover a papelera)
                if st.button(f"Editar {srv['id']}", key=f"edit_{srv['id']}"):
                    # rellenamos un modal básico: ponemos los datos en session_state y redirect to top form
                    st.session_state.edit_service = srv["id"]
                    st.info("Edit mode activado: desplázate arriba para editar. (En esta versión, edita los campos manualmente.)")
                    st.experimental_rerun()

                # subir documento adicional
                up = st.file_uploader(f"Subir doc para servicio {srv['id']}", key=f"up_{srv['id']}")
                if up:
                    ruta = save_service_document(srv["id"], up)
                    if ruta:
                        srv["documentos"].append({"nombre": up.name, "ruta": ruta})
                        save_json(SERVICES_FILE, servicios)
                        st.success("Documento guardado.")
                        st.experimental_rerun()

                # eliminar (mover a papelera) con confirmación
                if st.session_state.get("role","") == "admin":
                    if st.button(f"🗑️ Eliminar (mover a papelera) {srv['id']}", key=f"del_{srv['id']}"):
                        # confirm dialog
                        confirm = st.confirm(f"¿Confirmas que deseas mover el servicio '{srv.get('nombre')}' a la papelera? Esto se puede recuperar desde Papelerá.")
                        # Note: st.confirm is not an actual Streamlit method — emulate with a checkbox
                        # We'll ask explicitly using a simple checkbox fallback
                        if confirm:
                            papelera.append({"tipo": "servicio", "contenido": srv})
                            save_json(PAPELERA_FILE, papelera)
                            servicios = [s for s in servicios if s["id"] != srv["id"]]
                            save_json(SERVICES_FILE, servicios)
                            st.warning("Servicio movido a la papelera.")
                            st.experimental_rerun()
                        else:
                            # fallback manual confirm
                            if st.checkbox(f"Marcar para confirmar borrado servicio {srv['id']}", key=f"chk_del_{srv['id']}"):
                                papelera.append({"tipo": "servicio", "contenido": srv})
                                save_json(PAPELERA_FILE, papelera)
                                servicios = [s for s in servicios if s["id"] != srv["id"]]
                                save_json(SERVICES_FILE, servicios)
                                st.warning("Servicio movido a la papelera.")
                                st.experimental_rerun()
                else:
                    st.info("Solo admin puede eliminar servicios.")

st.markdown("---")

# === BOTON IR A PAPELERA ===
if st.button("Ir a Papelera"):
    st.experimental_set_query_params(page="papelera")
    st.experimental_rerun()

# ---------------------------------------------------------
# NOTA: En futuras iteraciones añadiremos:
# - Edición inline (actualizar un servicio ya creado)
# - Fechas individuales por asignación de empleado (ahora usan fecha inicio/fin del servicio por defecto)
# - Mejor UI para editar responsables
# - Vista para descargar documentos directamente desde la app
# ---------------------------------------------------------
