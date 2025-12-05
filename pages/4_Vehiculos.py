# pages/4_Vehiculos.py
import streamlit as st
from pathlib import Path
import json
from datetime import date, datetime
import os
import shutil

# -------------------------
# CONFIGURACIÓN Y RUTAS
# -------------------------
BASE_DIR = Path.cwd()
DATA_DIR = BASE_DIR / "data"
VEH_FILE = DATA_DIR / "vehiculos.json"
SERVICIOS_FILE = DATA_DIR / "servicios.json"
EMPLEADOS_FILE = DATA_DIR / "empleados.json"
PAPELERA_FILE = DATA_DIR / "papelera.json"

DOCS_DIR = DATA_DIR / "documents" / "vehicles"

LOGO_PATH = Path("/mnt/data/ccc6eb30-0a2e-47ae-a93f-08dc1d55755d.jpg")  # Logo PRODE

# Crear carpetas y archivos si no existen
DATA_DIR.mkdir(exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)

for f in [VEH_FILE, SERVICIOS_FILE, EMPLEADOS_FILE, PAPELERA_FILE]:
    if not f.exists():
        f.write_text("[]", encoding="utf-8")


# -------------------------
# FUNCIONES JSON
# -------------------------
def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except:
        return []


def save_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def next_id(items: list):
    if not items:
        return 1
    return max([int(i.get("id", 0)) for i in items]) + 1


# -------------------------
# FUNCIONES DOCUMENTOS
# -------------------------
def veh_folder(veh_id: int) -> Path:
    folder = DOCS_DIR / f"veh_{veh_id}"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def save_vehicle_document(veh_id: int, uploaded_file):
    if not uploaded_file:
        return None

    folder = veh_folder(veh_id)
    filename = uploaded_file.name.replace(" ", "_")
    dest = folder / filename

    if dest.exists():
        stamp = datetime.now().strftime("%Y%m%d%H%M%S")
        dest = folder / f"{dest.stem}_{stamp}{dest.suffix}"

    with open(dest, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return str(dest.relative_to(BASE_DIR))


def delete_vehicle_document(path_rel: str):
    try:
        p = BASE_DIR / path_rel
        if p.exists():
            p.unlink()
            return True
    except:
        return False
    return False


# -------------------------
# CARGA INICIAL DE DATOS
# -------------------------
vehiculos = load_json(VEH_FILE)
servicios = load_json(SERVICIOS_FILE)
empleados = load_json(EMPLEADOS_FILE)
papelera = load_json(PAPELERA_FILE)

# Session state para edición
if "veh_edit_id" not in st.session_state:
    st.session_state.veh_edit_id = None

if "tmp_asignaciones" not in st.session_state:
    st.session_state.tmp_asignaciones = []

if "tmp_averias" not in st.session_state:
    st.session_state.tmp_averias = []


# -------------------------
# INTERFAZ
# -------------------------
st.title("🚗 Gestión de Vehículos — PRODE Última Milla Manager")
if LOGO_PATH.exists():
    st.image(str(LOGO_PATH), width=160)
st.markdown("---")

# BOTÓN NUEVO VEHÍCULO
if st.button("➕ Nuevo vehículo"):
    st.session_state.veh_edit_id = None
    st.session_state.tmp_asignaciones = []
    st.session_state.tmp_averias = []
    st.experimental_rerun()


# -------------------------
# FORMULARIO DE VEHÍCULO
# -------------------------
st.header("📝 Crear / Editar vehículo")

edit_mode = False
veh_editing = None

if st.session_state.veh_edit_id:
    edit_mode = True
    veh_editing = next((v for v in vehiculos if v["id"] == st.session_state.veh_edit_id), None)

pref = veh_editing.copy() if veh_editing else {}


with st.form("form_vehiculo"):
    col1, col2 = st.columns(2)

    # -------------------------
    # DATOS BÁSICOS VEHÍCULO
    # -------------------------
    with col1:
        marca = st.text_input("Marca", value=pref.get("marca", ""))
        modelo = st.text_input("Modelo", value=pref.get("modelo", ""))
        matricula = st.text_input("Matrícula", value=pref.get("matricula", "")).upper()
        num_bastidor = st.text_input("Número de bastidor (opcional)", value=pref.get("bastidor", ""))

        tipo = st.selectbox(
            "Tipo de vehículo",
            ["Moto 3R", "Moto 4R", "Furgoneta", "Coche", "Otro"],
            index=["Moto 3R","Moto 4R","Furgoneta","Coche","Otro"].index(pref.get("tipo","Moto 3R"))
        )

        propiedad = st.selectbox(
            "Propiedad",
            ["PRODE", "Renting", "Leasing", "Otro"],
            index=["PRODE","Renting","Leasing","Otro"].index(pref.get("propiedad","PRODE"))
        )

        año_mat = st.number_input("Año matriculación", min_value=2000, max_value=2100, value=int(pref.get("anio", 2020)))

    # -------------------------
    # DATOS RENTING
    # -------------------------
    with col2:
        st.markdown("### Datos Renting (si aplica)")
        empresa_renting = st.text_input("Empresa Renting", value=pref.get("empresa_renting", ""))
        contacto_renting = st.text_input("Persona contacto", value=pref.get("contacto_renting", ""))
        tel_renting = st.text_input("Teléfono contacto", value=pref.get("tel_renting", ""))
        email_renting = st.text_input("Email contacto", value=pref.get("email_renting", ""))

        fecha_ini_rent = st.date_input("Fecha inicio renting", value=datetime.fromisoformat(pref["fecha_ini_renting"]).date() if pref.get("fecha_ini_renting") else date.today())
        fecha_fin_rent = st.date_input("Fecha fin renting", value=datetime.fromisoformat(pref["fecha_fin_renting"]).date() if pref.get("fecha_fin_renting") else date.today())

        cuota = st.number_input("Cuota mensual (opcional)", min_value=0.0, value=float(pref.get("cuota_renting", 0)))

    st.markdown("---")
    # -------------------------
    # ITV
    # -------------------------
    st.subheader("🔍 ITV")
    col_itv1, col_itv2 = st.columns(2)

    with col_itv1:
        fecha_itv_ultima = st.date_input(
            "Última ITV",
            value=datetime.fromisoformat(pref["fecha_itv_ultima"]).date() if pref.get("fecha_itv_ultima") else date.today()
        )

    with col_itv2:
        fecha_itv_proxima = st.date_input(
            "Próxima ITV",
            value=datetime.fromisoformat(pref["fecha_itv_proxima"]).date() if pref.get("fecha_itv_proxima") else date.today()
        )

    # Alertas ITV automáticas
    hoy = date.today()
    alerta_itv = None

    if fecha_itv_proxima < hoy:
        alerta_itv = "🚨 ITV CADUCADA"
    elif (fecha_itv_proxima - hoy).days < 30:
        alerta_itv = "⚠ ITV en menos de 30 días"

    if alerta_itv:
        st.error(alerta_itv)

    st.markdown("---")

    # -------------------------
    # ASIGNACIONES
    # -------------------------
    st.subheader("👥 Asignación de vehículo")

    servicios_map = {s["id"]: s["nombre"] for s in servicios}
    empleados_map = {e["id"]: f"{e['nombre']} {e['apellidos']}" for e in empleados}

    col_a1, col_a2, col_a3 = st.columns(3)

    with col_a1:
        asign_servicio = st.selectbox(
            "Asignado a servicio",
            ["Ninguno"] + list(servicios_map.values())
        )

    with col_a2:
        asign_empleado = st.selectbox(
            "Asignado a empleado",
            ["Ninguno"] + list(empleados_map.values())
        )

    with col_a3:
        fecha_asig_inicio = st.date_input("Desde", value=date.today())

    fecha_asig_fin = None
    if st.checkbox("¿Fecha fin?"):
        fecha_asig_fin = st.date_input("Fin", value=date.today())

    if st.button("➕ Añadir asignación"):
        st.session_state.tmp_asignaciones.append({
            "servicio": asign_servicio if asign_servicio != "Ninguno" else None,
            "empleado": asign_empleado if asign_empleado != "Ninguno" else None,
            "desde": fecha_asig_inicio.isoformat(),
            "hasta": fecha_asig_fin.isoformat() if fecha_asig_fin else None,
        })
        st.experimental_rerun()

    if st.session_state.tmp_asignaciones:
        st.markdown("### Asignaciones actuales:")
        for i, a in enumerate(st.session_state.tmp_asignaciones):
            st.write(f"- {a['servicio'] or ''} {a['empleado'] or ''} → {a['desde']} / {a['hasta'] or 'actual'}")
            if st.button(f"❌ Eliminar asignación #{i+1}", key=f"del_asig_{i}"):
                st.session_state.tmp_asignaciones.pop(i)
                st.experimental_rerun()

    st.markdown("---")

    # -------------------------
    # AVERÍAS / INCIDENCIAS
    # -------------------------
    st.subheader("🔧 Averías / Incidencias")

    col_av1, col_av2 = st.columns(2)

    with col_av1:
        tipo_averia = st.text_input("Tipo de avería")
        taller = st.text_input("Taller")
        tel_taller = st.text_input("Teléfono taller")

    with col_av2:
        fecha_ent = st.date_input("Entrada a taller", value=date.today())
        fecha_prev = st.date_input("Fecha prevista salida", value=date.today())
        fecha_real = st.date_input("Fecha real salida (opcional)", value=date.today())

    descripcion = st.text_area("Descripción de la avería")
    coste = st.number_input("Coste (opcional)", min_value=0.0, value=0.0)

    if st.button("➕ Añadir avería"):
        st.session_state.tmp_averias.append({
            "tipo": tipo_averia,
            "taller": taller,
            "tel_taller": tel_taller,
            "fecha_entrada": fecha_ent.isoformat(),
            "fecha_prevista": fecha_prev.isoformat(),
            "fecha_salida": fecha_real.isoformat() if fecha_real else None,
            "descripcion": descripcion,
            "coste": coste
        })
        st.experimental_rerun()

    if st.session_state.tmp_averias:
        st.markdown("### Averías registradas:")
        for i, a in enumerate(st.session_state.tmp_averias):
            st.write(f"- {a['tipo']} ({a['taller']}) — {a['fecha_entrada']} → {a['fecha_salida'] or 'En taller'}")
            if st.button(f"❌ Borrar avería #{i+1}", key=f"del_av_{i}"):
                st.session_state.tmp_averias.pop(i)
                st.experimental_rerun()

    st.markdown("---")

    # -------------------------
    # SUBIDA DE DOCUMENTOS
    # -------------------------
    st.subheader("📁 Documentos del vehículo")

    uploaded_doc = st.file_uploader("Subir documento (PDF/IMG/DOCX)", type=["pdf", "png", "jpg", "jpeg", "docx"])

    st.markdown("---")

    # -------------------------
    # BOTÓN GUARDAR
    # -------------------------
    submitted = st.form_submit_button("💾 Guardar vehículo")

    if submitted:
        if not marca or not matricula:
            st.error("Marca y matrícula son obligatorias.")
        else:
            if edit_mode:
                # ACTUALIZAR VEHÍCULO
                for v in vehiculos:
                    if v["id"] == veh_editing["id"]:
                        v.update({
                            "marca": marca,
                            "modelo": modelo,
                            "matricula": matricula,
                            "bastidor": num_bastidor,
                            "tipo": tipo,
                            "propiedad": propiedad,
                            "anio": año_mat,
                            "empresa_renting": empresa_renting,
                            "contacto_renting": contacto_renting,
                            "tel_renting": tel_renting,
                            "email_renting": email_renting,
                            "fecha_ini_renting": fecha_ini_rent.isoformat(),
                            "fecha_fin_renting": fecha_fin_rent.isoformat(),
                            "cuota_renting": cuota,
                            "fecha_itv_ultima": fecha_itv_ultima.isoformat(),
                            "fecha_itv_proxima": fecha_itv_proxima.isoformat(),
                            "asignaciones": st.session_state.tmp_asignaciones.copy(),
                            "averias": st.session_state.tmp_averias.copy(),
                        })

                        # Documento subido
                        if uploaded_doc:
                            ruta = save_vehicle_document(v["id"], uploaded_doc)
                            if ruta:
                                v.setdefault("documentos", []).append({
                                    "nombre": uploaded_doc.name,
                                    "ruta": ruta
                                })

                        save_json(VEH_FILE, vehiculos)
                        st.success("Vehículo actualizado correctamente.")
                        st.experimental_rerun()
            else:
                # CREAR NUEVO VEHÍCULO
                new_id = next_id(vehiculos)
                veh = {
                    "id": new_id,
                    "marca": marca,
                    "modelo": modelo,
                    "matricula": matricula,
                    "bastidor": num_bastidor,
                    "tipo": tipo,
                    "propiedad": propiedad,
                    "anio": año_mat,
                    "empresa_renting": empresa_renting,
                    "contacto_renting": contacto_renting,
                    "tel_renting": tel_renting,
                    "email_renting": email_renting,
                    "fecha_ini_renting": fecha_ini_rent.isoformat(),
                    "fecha_fin_renting": fecha_fin_rent.isoformat(),
                    "cuota_renting": cuota,
                    "fecha_itv_ultima": fecha_itv_ultima.isoformat(),
                    "fecha_itv_proxima": fecha_itv_proxima.isoformat(),
                    "asignaciones": st.session_state.tmp_asignaciones.copy(),
                    "averias": st.session_state.tmp_averias.copy(),
                    "documentos": []
                }

                # Guardar nuevo vehículo
                vehiculos.append(veh)
                save_json(VEH_FILE, vehiculos)

                # Guardar doc
                if uploaded_doc:
                    ruta = save_vehicle_document(new_id, uploaded_doc)
                    if ruta:
                        veh["documentos"].append({
                            "nombre": uploaded_doc.name,
                            "ruta": ruta
                        })
                        save_json(VEH_FILE, vehiculos)

                st.success("Vehículo creado correctamente.")
                st.experimental_rerun()


# -------------------------
# LISTADO DE VEHÍCULOS
# -------------------------
st.header("📋 Vehículos registrados")

if not vehiculos:
    st.info("No hay vehículos registrados.")
else:
    for v in vehiculos:
        with st.expander(f"{v['marca']} {v['modelo']} — {v['matricula']}"):
            st.markdown(f"**Tipo:** {v['tipo']}")
            st.markdown(f"**Propiedad:** {v['propiedad']}")
            st.markdown(f"**Año:** {v['anio']}")
            st.markdown(f"**Próxima ITV:** {v['fecha_itv_proxima']}")

            # DOCUMENTOS
            st.markdown("### 📁 Documentos:")
            docs = v.get("documentos", [])
            if docs:
                for d in docs:
                    path = BASE_DIR / d["ruta"]
                    if path.exists():
                        with open(path, "rb") as f:
                            st.download_button(
                                f"Descargar {d['nombre']}",
                                f.read(),
                                file_name=d["nombre"],
                                key=f"dl_{v['id']}_{d['nombre']}"
                            )
            else:
                st.write("No hay documentos.")

            # EDITAR
            if st.button(f"✏️ Editar {v['matricula']}", key=f"edit_{v['id']}"):
                st.session_state.veh_edit_id = v["id"]
                st.session_state.tmp_asignaciones = v.get("asignaciones", []).copy()
                st.session_state.tmp_averias = v.get("averias", []).copy()
                st.experimental_rerun()

            # ELIMINAR → PAPELERA
            if st.button(f"🗑️ Mover a papelera {v['matricula']}", key=f"del_{v['id']}"):
                papelera.append({
                    "tipo": "vehiculo",
                    "contenido": v,
                    "fecha": datetime.now().isoformat()
                })
                save_json(PAPELERA_FILE, papelera)
                vehiculos = [x for x in vehiculos if x["id"] != v["id"]]
                save_json(VEH_FILE, vehiculos)
                st.warning("Vehículo movido a la papelera.")
                st.experimental_rerun()

st.markdown("---")

# ENLACE PAPELERA
if st.button("🗑️ Ir a Papelera"):
    st.experimental_set_query_params(page="papelera")
    st.experimental_rerun()

