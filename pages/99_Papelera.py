# pages/99_Papelera.py
import streamlit as st
from pathlib import Path
import json
from datetime import datetime

BASE_DIR = Path.cwd()
DATA_DIR = BASE_DIR / "data"
PAPELERA_FILE = DATA_DIR / "papelera.json"
SERVICIOS_FILE = DATA_DIR / "servicios.json"
EMPLEADOS_FILE = DATA_DIR / "empleados.json"

# Asegurar archivos
if not PAPELERA_FILE.exists():
    PAPELERA_FILE.write_text("[]", encoding="utf-8")
if not SERVICIOS_FILE.exists():
    SERVICIOS_FILE.write_text("[]", encoding="utf-8")
if not EMPLEADOS_FILE.exists():
    EMPLEADOS_FILE.write_text("[]", encoding="utf-8")

def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []

def save_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

papelera = load_json(PAPELERA_FILE)
servicios = load_json(SERVICIOS_FILE)
empleados = load_json(EMPLEADOS_FILE)

# ------------
#      UI
# ------------
st.title("🗑️ Papelera — Recuperación de datos")
st.markdown("---")
st.info("Aquí puedes **restaurar** o **eliminar definitivamente** los datos borrados.")

if not papelera:
    st.success("La papelera está vacía.")
    st.stop()

# Separar elementos por tipo
serv_borrados = [x for x in papelera if x.get("tipo") == "servicio"]
emp_borrados = [x for x in papelera if x.get("tipo") == "empleado"]

# ============================
#     SERVICIOS
# ============================
st.header("📁 Servicios eliminados")

if not serv_borrados:
    st.write("No hay servicios eliminados.")
else:
    for item in serv_borrados:
        srv = item["contenido"]
        fecha_del = item.get("fecha")
        fecha_str = datetime.fromisoformat(fecha_del).strftime("%d/%m/%Y %H:%M") if fecha_del else "-"

        with st.expander(f"🗂️ {srv['nombre']} — eliminado el {fecha_str}"):
            st.write(f"**Empresa:** {srv.get('empresa','')}")
            st.write(f"**NIF:** {srv.get('nif','')}")
            st.write(f"**Dimensión:** {srv.get('dimension','')}")

            c1, c2 = st.columns(2)

            # Restaurar servicio
            with c1:
                if st.button(f"♻️ Restaurar servicio {srv['id']}", key=f"restore_srv_{srv['id']}"):
                    servicios.append(srv)
                    save_json(SERVICIOS_FILE, servicios)

                    papelera.remove(item)
                    save_json(PAPELERA_FILE, papelera)

                    st.success("Servicio restaurado correctamente.")
                    st.experimental_rerun()

            # Borrar definitivamente (solo admin)
            with c2:
                chk = st.checkbox(f"Confirmar eliminación permanente {srv['id']}", key=f"del_confirm_srv_{srv['id']}")
                if chk:
                    if st.button(f"🗑️ Borrar DEFINITIVO {srv['id']}", key=f"delete_final_srv_{srv['id']}"):
                        papelera.remove(item)
                        save_json(PAPELERA_FILE, papelera)

                        st.error("Servicio eliminado de forma permanente.")
                        st.experimental_rerun()


# ============================
#    EMPLEADOS (cuando estén)
# ============================
st.header("👥 Empleados eliminados")

if not emp_borrados:
    st.write("No hay empleados eliminados (todavía).")
else:
    for item in emp_borrados:
        emp = item["contenido"]
        fecha_del = item.get("fecha")
        fecha_str = datetime.fromisoformat(fecha_del).strftime("%d/%m/%Y %H:%M") if fecha_del else "-"

        with st.expander(f"👤 {emp['nombre']} {emp['apellidos']} — eliminado el {fecha_str}"):
            
            c1, c2 = st.columns(2)

            with c1:
                if st.button(f"♻️ Restaurar empleado {emp['id']}", key=f"restore_emp_{emp['id']}"):
                    empleados.append(emp)
                    save_json(EMPLEADOS_FILE, empleados)

                    papelera.remove(item)
                    save_json(PAPELERA_FILE, papelera)

                    st.success("Empleado restaurado.")
                    st.experimental_rerun()

            with c2:
                chk = st.checkbox(f"Confirmar eliminación permanente emp {emp['id']}", key=f"del_confirm_emp_{emp['id']}")
                if chk:
                    if st.button(f"🗑️ Borrar DEFINITIVO emp {emp['id']}", key=f"delete_final_emp_{emp['id']}"):
                        papelera.remove(item)
                        save_json(PAPELERA_FILE, papelera)

                        st.error("Empleado eliminado de forma permanente.")
                        st.experimental_rerun()

st.markdown("---")
st.success("Papelera lista y funcionando.")        
