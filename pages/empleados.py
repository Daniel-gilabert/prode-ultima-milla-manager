"""pages/empleados.py — Lista de empleados y ficha individual."""
import streamlit as st
from utils import query, execute, page_header, back_button, badge

# ─────────────────────────────────────────────
# FICHA DE EMPLEADO
# ─────────────────────────────────────────────
def ficha_empleado(emp_id: int):
    rows = query("SELECT * FROM empleados WHERE id = %s", (emp_id,))
    if not rows:
        st.error("Empleado no encontrado.")
        return
    e = rows[0]

    if back_button("← Volver a empleados"):
        st.session_state.pop("selected_empleado", None)
        st.rerun()

    # Cabecera de ficha
    col_foto, col_info = st.columns([0.15, 0.85])
    with col_foto:
        if e.get("foto_url"):
            st.image(e["foto_url"], width=90)
        else:
            initials = (e.get("nombre","?")[0] + e.get("apellidos","?")[0]).upper()
            st.markdown(f"""
            <div style="width:80px;height:80px;border-radius:50%;
                        background:#E8500A;color:white;font-size:1.6rem;
                        font-weight:800;display:flex;align-items:center;
                        justify-content:center;">{initials}</div>
            """, unsafe_allow_html=True)

    with col_info:
        activo = e.get("activo", False)
        estado_html = badge("Activo", "green") if activo else badge("Inactivo", "red")
        st.markdown(f"""
        <h2 style="margin:0;color:#1B3A6B;font-weight:800;">
            {e.get('nombre','')} {e.get('apellidos','')}
            &nbsp;{estado_html}
        </h2>
        <p style="color:#5A6D82;margin:4px 0 0;">
            📧 {e.get('email','—')} &nbsp;|&nbsp; 📱 {e.get('telefono','—')}
            &nbsp;|&nbsp; 🪪 {e.get('dni','—')}
        </p>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Tabs de la ficha
    tab_datos, tab_servicios, tab_ausencias = st.tabs([
        "📋 Datos personales", "🚛 Servicios asignados", "📅 Ausencias / Bajas"
    ])

    # ── Tab 1: Datos ──
    with tab_datos:
        st.markdown('<div class="card card-blue">', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            nombre    = st.text_input("Nombre",    value=e.get("nombre", ""))
            apellidos = st.text_input("Apellidos", value=e.get("apellidos", ""))
            dni       = st.text_input("DNI",       value=e.get("dni", ""))
        with c2:
            telefono  = st.text_input("Teléfono",  value=e.get("telefono", ""))
            email     = st.text_input("Email",     value=e.get("email", ""))
            activo_cb = st.checkbox("Empleado activo", value=bool(e.get("activo")))
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("💾 Guardar cambios", key="save_emp"):
            ok = execute("""
                UPDATE empleados
                SET nombre=%s, apellidos=%s, dni=%s,
                    telefono=%s, email=%s, activo=%s
                WHERE id=%s
            """, (nombre, apellidos, dni, telefono, email, activo_cb, emp_id))
            if ok:
                st.success("Empleado actualizado correctamente.")

    # ── Tab 2: Servicios ──
    with tab_servicios:
        servicios = query("""
            SELECT s.id, s.codigo, s.nombre_linea, s.fecha,
                   v.matricula, v.marca, v.modelo
            FROM servicios s
            LEFT JOIN vehiculos v ON v.id = s.vehiculo_id
            WHERE s.empleado_id = %s
            ORDER BY s.fecha DESC NULLS LAST
            LIMIT 30
        """, (emp_id,))

        if servicios:
            import pandas as pd
            df = pd.DataFrame(servicios)
            df = df.rename(columns={
                "id": "ID", "codigo": "Código", "nombre_linea": "Línea",
                "fecha": "Fecha", "matricula": "Matrícula",
                "marca": "Marca", "modelo": "Modelo"
            })
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Este empleado no tiene servicios asignados.")

    # ── Tab 3: Ausencias ──
    with tab_ausencias:
        ausencias = query("""
            SELECT id, tipo, fecha_inicio, fecha_fin, observaciones
            FROM ausencias
            WHERE empleado_id = %s
            ORDER BY fecha_inicio DESC
        """, (emp_id,))

        if ausencias:
            import pandas as pd
            df_a = pd.DataFrame(ausencias)
            df_a = df_a.rename(columns={
                "id": "ID", "tipo": "Tipo", "fecha_inicio": "Inicio",
                "fecha_fin": "Fin", "observaciones": "Observaciones"
            })
            st.dataframe(df_a, use_container_width=True, hide_index=True)
        else:
            st.info("Sin ausencias registradas para este empleado.")

        st.markdown("---")
        st.markdown("##### ➕ Registrar nueva ausencia")
        with st.expander("Nueva ausencia / baja / vacación"):
            c1, c2 = st.columns(2)
            with c1:
                tipo       = st.selectbox("Tipo", ["Vacaciones", "Baja médica",
                                                    "Ausencia justificada",
                                                    "Ausencia injustificada", "Otro"])
                fecha_ini  = st.date_input("Fecha inicio")
            with c2:
                fecha_fin  = st.date_input("Fecha fin")
            observaciones  = st.text_area("Observaciones", height=80)
            if st.button("Guardar ausencia", key="nueva_ausencia"):
                ok = execute("""
                    INSERT INTO ausencias (empleado_id, tipo, fecha_inicio, fecha_fin, observaciones)
                    VALUES (%s, %s, %s, %s, %s)
                """, (emp_id, tipo, fecha_ini, fecha_fin, observaciones))
                if ok:
                    st.success("Ausencia registrada.")
                    st.rerun()

# ─────────────────────────────────────────────
# LISTA DE EMPLEADOS
# ─────────────────────────────────────────────
def lista_empleados():
    page_header("👥", "Empleados")

    # Buscador y filtro
    col_search, col_filter, col_btn = st.columns([2, 1, 0.8])
    with col_search:
        buscar = st.text_input("🔍 Buscar por nombre, apellidos o DNI",
                               placeholder="Ej: García…", label_visibility="collapsed")
    with col_filter:
        filtro_activo = st.selectbox("Estado", ["Todos", "Activos", "Inactivos"],
                                     label_visibility="collapsed")
    with col_btn:
        if st.button("➕ Nuevo empleado", use_container_width=True):
            st.session_state["nuevo_empleado"] = True

    # Query con filtros
    where = []
    params = []
    if buscar:
        where.append("(nombre ILIKE %s OR apellidos ILIKE %s OR dni ILIKE %s)")
        params += [f"%{buscar}%"] * 3
    if filtro_activo == "Activos":
        where.append("activo = TRUE")
    elif filtro_activo == "Inactivos":
        where.append("activo = FALSE")

    sql = "SELECT * FROM empleados"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY apellidos, nombre"

    empleados = query(sql, params or None)

    st.markdown(f"**{len(empleados)} empleado(s) encontrado(s)**")
    st.markdown("---")

    if not empleados:
        st.info("No se encontraron empleados con esos criterios.")
        return

    # Renderizar filas clickables
    for emp in empleados:
        nombre_completo = f"{emp.get('nombre','')} {emp.get('apellidos','')}"
        initials = (emp.get("nombre","?")[0] + emp.get("apellidos","?")[0]).upper()
        activo   = emp.get("activo", False)
        estado   = badge("Activo", "green") if activo else badge("Inactivo", "red")

        col_main, col_action = st.columns([5, 0.8])
        with col_main:
            st.markdown(f"""
            <div class="row-card">
                <div class="row-avatar">{initials}</div>
                <div>
                    <div class="row-name">{nombre_completo} &nbsp; {estado}</div>
                    <div class="row-sub">
                        📧 {emp.get('email','—')} &nbsp;|&nbsp;
                        📱 {emp.get('telefono','—')} &nbsp;|&nbsp;
                        🪪 {emp.get('dni','—')}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col_action:
            if st.button("Ver ficha →", key=f"emp_{emp['id']}"):
                st.session_state["selected_empleado"] = emp["id"]
                st.rerun()

    # Modal: nuevo empleado
    if st.session_state.get("nuevo_empleado"):
        st.markdown("---")
        st.markdown("### ➕ Nuevo empleado")
        with st.form("form_nuevo_emp"):
            c1, c2 = st.columns(2)
            with c1:
                n_nombre   = st.text_input("Nombre *")
                n_apellido = st.text_input("Apellidos *")
                n_dni      = st.text_input("DNI *")
            with c2:
                n_tel      = st.text_input("Teléfono")
                n_email    = st.text_input("Email")
                n_activo   = st.checkbox("Activo", value=True)
            submitted = st.form_submit_button("Crear empleado")
            if submitted:
                if not n_nombre or not n_apellido or not n_dni:
                    st.warning("Nombre, apellidos y DNI son obligatorios.")
                else:
                    ok = execute("""
                        INSERT INTO empleados (nombre, apellidos, dni, telefono, email, activo)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (n_nombre, n_apellido, n_dni, n_tel, n_email, n_activo))
                    if ok:
                        st.success("Empleado creado correctamente.")
                        st.session_state.pop("nuevo_empleado", None)
                        st.rerun()

# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────
def render():
    if st.session_state.get("selected_empleado"):
        ficha_empleado(st.session_state["selected_empleado"])
    else:
        lista_empleados()
