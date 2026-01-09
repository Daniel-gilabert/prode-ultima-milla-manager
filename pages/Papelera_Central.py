# pages/10_Papelera_Central.py
import streamlit as st
from pathlib import Path
import json
from datetime import datetime
import shutil
import os

# -------------------------
# CONFIG / RUTAS
# -------------------------
BASE = Path.cwd()
DATA = BASE / "data"
PAPELERA_FILE = DATA / "papelera.json"

# Otros ficheros a restaurar
FILES_MAP = {
    "empleado": DATA / "empleados.json",
    "servicio": DATA / "servicios.json",
    "vehiculo": DATA / "vehiculos.json",
    "ausencia": DATA / "ausencias.json",
    "epi": DATA / "epis.json",
    "mantenimiento": DATA / "mantenimiento.json",
    "documento": DATA / "documentacion.json"
}

LOGO_PATH = Path("/mnt/data/ccc6eb30-0a2e-47ae-a93f-08dc1d55755d.jpg")  # ruta del logo que usamos

# Asegurar existencia
DATA.mkdir(parents=True, exist_ok=True)
if not PAPELERA_FILE.exists():
    PAPELERA_FILE.write_text("[]", encoding="utf-8")
for p in FILES_MAP.values():
    if not p.exists():
        p.write_text("[]", encoding="utf-8")


# -------------------------
# HELPERS JSON / FICHEROS
# -------------------------
def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []

def save_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def remove_physical_file(rel_path: str):
    """Eliminar archivo en disco (ruta relativa a BASE). Devuelve True si eliminado."""
    try:
        p = BASE / rel_path
        if p.exists():
            p.unlink()
            # si carpeta queda vacía, se podría borrar (opcional)
            parent = p.parent
            try:
                if parent.exists() and not any(parent.iterdir()):
                    parent.rmdir()
            except Exception:
                pass
            return True
    except Exception:
        pass
    return False

def restore_item_to_file(item):
    """Restaura un elemento de la papelera según su tipo a su JSON correspondiente."""
    tipo = item.get("tipo")
    contenido = item.get("contenido")
    target = FILES_MAP.get(tipo)
    if not target:
        return False, "Tipo no soportado para restaurar."
    data = load_json(target)
    # evitar duplicados: si ya existe un registro con el mismo id, ajustar id nuevo
    existing_ids = {d.get("id") for d in data}
    cid = contenido.get("id")
    if cid in existing_ids:
        # reasignar id nuevo secuencial
        new_id = max(existing_ids) + 1 if existing_ids else 1
        contenido["id"] = new_id
    data.append(contenido)
    save_json(target, data)
    return True, f"Restaurado a {target.name}"

def permanently_delete(item):
    """Borra permanentemente del JSON de papelera y elimina archivos si procede."""
    tipo = item.get("tipo")
    contenido = item.get("contenido")
    # si es documento o contenido con archivos asociados, intentar borrar archivos físicos
    if tipo == "documento":
        archivo = contenido.get("archivo")
        if archivo:
            remove_physical_file(archivo)
    elif tipo == "vehiculo":
        # eliminar documentos del vehículo si están en carpeta documents/vehicles/veh_{id}/
        docs_base = DATA / "documents" / "vehicles" / f"veh_{contenido.get('id')}"
        try:
            if docs_base.exists():
                shutil.rmtree(docs_base)
        except Exception:
            pass
    elif tipo == "servicio":
        docs_base = DATA / "documents" / "services" / f"service_{contenido.get('id')}"
        try:
            if docs_base.exists():
                shutil.rmtree(docs_base)
        except Exception:
            pass
    elif tipo == "empleado":
        docs_base = DATA / "documents" / "epis" / f"emp_{contenido.get('id')}"
        try:
            if docs_base.exists():
                shutil.rmtree(docs_base)
        except Exception:
            pass
    # finalmente, borrar registro de la papelera (caller lo hará), y ya está.
    return True


# -------------------------
# UI: PAPELERA CENTRAL
# -------------------------
st.title("🗑️ Papelera Central — PRODE Última Milla Manager")
if LOGO_PATH.exists():
    st.image(str(LOGO_PATH), width=150)
st.markdown("---")
st.info("Aquí están todos los elementos eliminados. Puedes restaurarlos o borrarlos de forma permanente. **Operaciones con confirmación.**")

papelera = load_json(PAPELERA_FILE)

if not papelera:
    st.success("La papelera está vacía.")
    st.stop()

# Mostrar filtros
st.sidebar.header("Filtros")
tipo_filtro = st.sidebar.selectbox("Filtrar por tipo", ["Todos", "empleado", "servicio", "vehiculo", "ausencia", "epi", "documento", "mantenimiento"])
buscar_text = st.sidebar.text_input("Buscar texto (nombre, id, etc.)")

# Agrupar por tipo para mostrar por secciones
tipos_presentes = {}
for it in papelera:
    t = it.get("tipo", "otro")
    tipos_presentes.setdefault(t, []).append(it)

# Orden por fecha más reciente
def parse_fecha_item(it):
    f = it.get("fecha")
    try:
        return datetime.fromisoformat(f)
    except:
        return datetime.min
papelera_sorted = sorted(papelera, key=parse_fecha_item, reverse=True)

# Botón para vaciar papelera (peligroso) — solo admin idealmente; aquí pedimos confirmación doble
st.sidebar.markdown("---")
if st.sidebar.checkbox("Mostrar opciones avanzadas"):
    if st.sidebar.button("🧨 Vaciar papelera (ELIMINACIÓN PERMANENTE)"):
        if st.sidebar.checkbox("Confirmo que quiero BORRAR TODO PERMANENTEMENTE (no hay vuelta atrás)"):
            # eliminar archivos asociados y borrar papelera
            for item in papelera:
                permanently_delete(item)
            save_json(PAPELERA_FILE, [])
            st.error("Papelera vaciada y borrado permanente de archivos asociados.")
            st.experimental_rerun()

# Recorremos items y los mostramos (aplicar filtros)
count = 0
for item in papelera_sorted:
    tipo = item.get("tipo", "otro")
    if tipo_filtro != "Todos" and tipo != tipo_filtro:
        continue
    contenido = item.get("contenido", {})
    fecha = item.get("fecha", None)
    fecha_str = fecha or "-"
    # construir título humanizado
    title = f"[{tipo.upper()}] "
    if tipo in ("empleado", "epi"):
        name = contenido.get("nombre") or f"{contenido.get('nombre','')} {contenido.get('apellidos','')}".strip()
        title += f"{name} (id:{contenido.get('id')})"
    elif tipo in ("servicio", "vehiculo", "documento", "mantenimiento", "ausencia"):
        # intentar mostrar campo identificador útil
        title += contenido.get("nombre") or contenido.get("matricula") or f"id:{contenido.get('id')}"
    else:
        title += str(contenido.get("id") or "sin id")
    # buscar filtro de texto
    if buscar_text:
        texto = json.dumps(item).lower()
        if buscar_text.lower() not in texto:
            continue

    count += 1
    with st.expander(f"{title} — eliminado: {fecha_str}"):
        st.write("**Tipo:**", tipo)
        st.write("**Fecha eliminación:**", fecha_str)
        st.write("**Contenido (resumen):**")
        # mostrar campos clave según tipo
        if tipo == "empleado":
            st.write(f"- Nombre: {contenido.get('nombre')} {contenido.get('apellidos')}")
            st.write(f"- DNI: {contenido.get('dni','-')}")
            st.write(f"- Puesto: {contenido.get('puesto','-')}")
        elif tipo == "servicio":
            st.write(f"- Nombre servicio: {contenido.get('nombre')}")
            st.write(f"- Empresa: {contenido.get('empresa','-')}")
            st.write(f"- NIF: {contenido.get('nif','-')}")
        elif tipo == "vehiculo":
            st.write(f"- Matrícula: {contenido.get('matricula')}")
            st.write(f"- Marca/Modelo: {contenido.get('marca')} {contenido.get('modelo')}")
        elif tipo == "ausencia":
            st.write(f"- Empleado id: {contenido.get('empleado_id')}")
            st.write(f"- Desde: {contenido.get('desde')}  Hasta: {contenido.get('hasta')}")
            if contenido.get("justificante"):
                st.write(f"- Justificante: {contenido.get('justificante')}")
        elif tipo == "epi":
            st.write(f"- Empleado id: {contenido.get('empleado_id')}")
            st.write(f"- Tipo: {contenido.get('tipo')}")
            st.write(f"- Fecha entrega: {contenido.get('fecha_entrega')}")
        elif tipo == "documento":
            st.write(f"- Categoría: {contenido.get('categoria')}")
            st.write(f"- Descripción: {contenido.get('descripcion')}")
            st.write(f"- Archivo: {contenido.get('archivo')}")
        elif tipo == "mantenimiento":
            st.write(f"- Vehículo id: {contenido.get('vehiculo_id')}")
            st.write(f"- Tipo: {contenido.get('tipo')}")
            st.write(f"- Fecha: {contenido.get('fecha')}")

        st.markdown("")

        c1, c2, c3 = st.columns([1,1,1])

        # -------------------------
        # Restaurar
        # -------------------------
        with c1:
            if st.button(f"♻️ Restaurar (id:{contenido.get('id')})", key=f"restore_{count}"):
                ok, msg = restore_item_to_file(item)
                if ok:
                    # eliminar de papelera
                    current = load_json(PAPELERA_FILE)
                    # remover exactamente este item (comparando contenido e tipo y fecha)
                    new = [it for it in current if not (it.get("tipo")==item.get("tipo") and it.get("contenido").get("id")==item.get("contenido").get("id") and it.get("fecha")==item.get("fecha"))]
                    save_json(PAPELERA_FILE, new)
                    st.success(f"Restaurado: {msg}")
                    st.experimental_rerun()
                else:
                    st.error(f"No se pudo restaurar: {msg}")

        # -------------------------
        # Eliminar permanentemente
        # -------------------------
        with c2:
            if st.checkbox(f"Confirmar borrado permanente id:{contenido.get('id')}", key=f"chk_del_{count}"):
                if st.button(f"🗑️ Borrar definitivamente (id:{contenido.get('id')})", key=f"perma_{count}"):
                    # intentar borrar archivos asociados
                    permanently_delete(item)
                    # quitar del JSON de papelera
                    current = load_json(PAPELERA_FILE)
                    new = [it for it in current if not (it.get("tipo")==item.get("tipo") and it.get("contenido").get("id")==item.get("contenido").get("id") and it.get("fecha")==item.get("fecha"))]
                    save_json(PAPELERA_FILE, new)
                    st.error("Elemento borrado de forma permanente.")
                    st.experimental_rerun()

        # -------------------------
        # Ver archivo asociado (si existe)
        # -------------------------
        with c3:
            if tipo == "documento":
                archivo = contenido.get("archivo")
                if archivo:
                    ruta = BASE / archivo
                    if ruta.exists():
                        with open(ruta, "rb") as f:
                            st.download_button("⬇️ Descargar archivo asociado", data=f.read(), file_name=ruta.name, key=f"dl_doc_{count}")
                    else:
                        st.warning("Archivo asociado no encontrado en disco.")
            elif tipo == "ausencia" and contenido.get("justificante"):
                ruta = BASE / contenido.get("justificante")
                if ruta.exists():
                    with open(ruta, "rb") as f:
                        st.download_button("⬇️ Descargar justificante", data=f.read(), file_name=ruta.name, key=f"dl_just_{count}")
                else:
                    st.warning("Justificante no encontrado.")


st.markdown("---")
st.info("Recuerda: la restauración asigna de nuevo el registro al JSON correspondiente. Si el ID clasha, se le asigna un nuevo ID automáticamente para evitar duplicados.")
