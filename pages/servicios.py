"""pages/servicios.py — Lista de servicios y ficha."""
import streamlit as st
from utils import query, execute, page_header, back_button, badge


def ficha_servicio(srv_id: int):
    rows = query("SELECT * FROM servicios WHERE id = %s", (srv_id,))
    if not rows:
        st.error("Servicio no encontrado.")
        return
    s = rows[0]

    if back_button("← Volver a servicios"):
        st.session_state.pop("selected_servicio", None)
        st.rerun()

    activo_b = badge("Activo", "green") if s.get("activo") else badge("Inactivo", "red")
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:1rem;margin-bottom:1rem;">
        <span style="font-size:2rem">📋</span>
        <div>
            <h2 style="margin:0;color:#1B3A6B;font-weight:800;">
                {s.get('codigo','—')} — {s.get('descripcion','—')}
                &nbsp;{activo_b}
            </h2>
            <p style="color:#5A6D82;margin:4px 0 0;">
                {s.get('tipo_servicio','—')} &nbsp;|&nbsp;
                📅 {s.get('fecha_inicio_contrato','—')} → {s.get('fecha_fin_contrato','—')}
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    tab_datos, tab_empresa, tab_emp, tab_veh = st.tabs([
        "📋 Datos del servicio",
        "🏢 Empresa / Cliente",
        "👤 Empleado asignado",
        "🚛 Vehículo asignado"
    ])

    with tab_datos:
        c1, c2 = st.columns(2)
        with c1:
            st.text_input("Código",        value=s.get("codigo",""),               disabled=True)
            st.text_input("Descripción",   value=s.get("descripcion",""),          disabled=True)
            st.text_input("Tipo servicio", value=s.get("tipo_servicio","") or "",  disabled=True)
            st.text_input("Días servicio", value=s.get("dias_servicio","") or "",  disabled=True)
        with c2:
            st.text_input("Horario inicio",  value=s.get("horario_inicio","") or "",              disabled=True)
            st.text_input("Horario fin",     value=s.get("horario_fin","") or "",                 disabled=True)
            st.text_input("Inicio contrato", value=str(s.get("fecha_inicio_contrato","") or ""),  disabled=True)
            st.text_input("Fin contrato",    value=str(s.get("fecha_fin_contrato","") or ""),     disabled=True)
        if s.get("observaciones"):
            st.markdown("**Observaciones:**")
            st.info(s["observaciones"])
        if s.get("tarifa_mensual"):
            st.markdown(f"**Tarifa mensual:** `{s['tarifa_mensual']} €`")

    with tab_empresa:
        c1, c2 = st.columns(2)
        with c1:
            st.text_input("Empresa",   value=s.get("empresa_nombre","") or "",    disabled=True)
            st.text_input("CIF",       value=s.get("empresa_cif","") or "",       disabled=True)
            st.text_input("Dirección", value=s.get("empresa_direccion","") or "", disabled=True)
            st.text_input("CP",        value=s.get("empresa_cp","") or "",        disabled=True)
            st.text_input("Ciudad",    value=s.get("empresa_ciudad","") or "",    disabled=True)
        with c2:
            st.text_input("Contacto",  value=s.get("contacto_nombre","") or "",   disabled=True)
            st.text_input("Cargo",     value=s.get("contacto_cargo","") or "",    disabled=True)
            st.text_input("Email",     value=s.get("contacto_email","") or "",    disabled=True)
            st.text_input("Teléfono",  value=s.get("contacto_telefono","") or "", disabled=True)
            st.text_input("Móvil",     value=s.get("contacto_movil","") or "",    disabled=True)

    with tab_emp:
        emp_id = s.get("empleado_base_id")
        if emp_id:
            emp = query("SELECT * FROM empleados WHERE id = %s", (emp_id,))
            if emp:
                e = emp[0]
                ini = (e['nombre'][0] + e['apellidos'][0]).upper()
                activo_emp = badge("Activo","green") if e.get("activo") else badge("Inactivo","red")
                st.markdown(f"""
                <div class="row-card">
                    <div class="row-avatar">{ini}</div>
                    <div>
                        <div class="row-name">
                            {e['nombre']} {e['apellidos']} &nbsp; {activo_emp}
                        </div>
                        <div class="row-sub">
                            📧 {e.get('email','—')} &nbsp;|&nbsp;
                            📱 {e.get('telefono','—')} &nbsp;|&nbsp;
                            🪪 {e.get('dni','—')}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Ver ficha del empleado →"):
                    st.session_state["selected_empleado"] = e["id"]
                    st.session_state["page"] = "Empleados"
                    st.session_state.pop("selected_servicio", None)
                    st.rerun()
        else:
            st.info("Sin empleado asignado.")

    with tab_veh:
        veh_id = s.get("vehiculo_base_id")
        if veh_id:
            veh = query("SELECT * FROM vehiculos WHERE id = %s", (veh_id,))
            if veh:
                v = veh[0]
                st.markdown(f"""
                <div class="row-card">
                    <div class="row-avatar"
                         style="background:rgba(27,58,107,0.08);
                                color:#1B3A6B;font-size:1.4rem;">🚛</div>
                    <div>
                        <div class="row-name">
                            {v.get('matricula','—')} —
                            {v.get('marca','')} {v.get('modelo','')}
                        </div>
                        <div class="row-sub">
                            Tipo: {v.get('tipo','—')} &nbsp;|&nbsp;
                            ITV: {v.get('itv_vigente_hasta','—')}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Ver ficha del vehículo →"):
                    st.session_state["selected_vehiculo"] = v["id"]
                    st.session_state["page"] = "Vehiculos"
                    st.session_state.pop("selected_servicio", None)
                    st.rerun()
        else:
            st.info("Sin vehículo asignado.")


def lista_servicios():
    page_header("📋", "Servicios")

    col_s, col_f, col_btn = st.columns([2, 1, 1])
    with col_s:
        buscar = st.text_input("🔍 Buscar", label_visibility="collapsed",
                               placeholder="Código, descripción, empresa…")
    with col_f:
        filtro = st.selectbox("Estado", ["Todos","Activos","Inactivos"],
                              label_visibility="collapsed")
    with col_btn:
        if st.button("➕ Nuevo servicio", use_container_width=True):
            st.session_state["nuevo_servicio"] = not st.session_state.get("nuevo_servicio", False)

    if st.session_state.get("nuevo_servicio"):
        with st.expander("➕ Nuevo servicio", expanded=True):
            empleados_list = query(
                "SELECT id, nombre || ' ' || apellidos AS nombre "
                "FROM empleados WHERE activo=TRUE ORDER BY apellidos"
            )
            vehiculos_list = query(
                "SELECT id, matricula || ' — ' || marca || ' ' || modelo AS nombre "
                "FROM vehiculos ORDER BY matricula"
            )
            emp_opts = {e["nombre"]: e["id"] for e in empleados_list}
            veh_opts = {v["nombre"]: v["id"] for v in vehiculos_list}

            with st.form("form_nuevo_srv"):
                c1, c2 = st.columns(2)
                with c1:
                    n_cod  = st.text_input("Código *")
                    n_desc = st.text_input("Descripción *")
                    n_tipo = st.selectbox("Tipo servicio",
                                          ["Reparto","Recogida","Mensajería","Otro"])
                    n_dias = st.text_input("Días servicio", placeholder="Ej: L-V")
                    n_hi   = st.text_input("Horario inicio", placeholder="08:00")
                    n_hf   = st.text_input("Horario fin",    placeholder="16:00")
                with c2:
                    n_emp  = st.selectbox("Empleado *", list(emp_opts.keys()))
                    n_veh  = st.selectbox("Vehículo *", list(veh_opts.keys()))
                    n_fi   = st.date_input("Inicio contrato")
                    n_ff   = st.date_input("Fin contrato")
                    n_tar  = st.number_input("Tarifa mensual (€)", min_value=0.0, step=10.0)
                    n_obs  = st.text_area("Observaciones", height=68)

                if st.form_submit_button("✅ Crear servicio", use_container_width=True):
                    if not n_cod or not n_desc:
                        st.warning("Código y descripción son obligatorios.")
                    else:
                        ok = execute("""
                            INSERT INTO servicios
                            (codigo, descripcion, tipo_servicio, dias_servicio,
                             horario_inicio, horario_fin, empleado_base_id,
                             vehiculo_base_id, fecha_inicio_contrato,
                             fecha_fin_contrato, tarifa_mensual, observaciones, activo)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,TRUE)
                        """, (n_cod, n_desc, n_tipo, n_dias, n_hi, n_hf,
                              emp_opts[n_emp], veh_opts[n_veh],
                              n_fi, n_ff, n_tar or None, n_obs or None))
                        if ok:
                            st.success(f"Servicio {n_cod} creado correctamente.")
                            st.session_state["nuevo_servicio"] = False
                            st.rerun()

    where, params = [], []
    if buscar:
        where.append("(s.codigo ILIKE %s OR s.descripcion ILIKE %s OR s.empresa_nombre ILIKE %s)")
        params += [f"%{buscar}%"] * 3
    if filtro == "Activos":
        where.append("s.activo = TRUE")
    elif filtro == "Inactivos":
        where.append("s.activo = FALSE")

    sql = """
        SELECT s.id, s.codigo, s.descripcion, s.tipo_servicio,
               s.dias_servicio, s.horario_inicio, s.horario_fin, s.activo,
               e.nombre || ' ' || e.apellidos AS empleado,
               v.matricula
        FROM servicios s
        LEFT JOIN empleados e ON e.id = s.empleado_base_id
        LEFT JOIN vehiculos v ON v.id = s.vehiculo_base_id
    """
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY s.codigo LIMIT 100"

    servicios = query(sql, params or None)
    st.markdown(f"**{len(servicios)} servicio(s)**")
    st.markdown("---")

    for s in servicios:
        activo_b = badge("Activo","green") if s.get("activo") else badge("Inactivo","red")
        col_main, col_act = st.columns([5, 0.8])
        with col_main:
            st.markdown(f"""
            <div class="row-card">
                <div class="row-avatar"
                     style="background:rgba(26,140,91,0.10);
                            color:#1A8C5B;font-size:1.3rem;">📋</div>
                <div>
                    <div class="row-name">
                        {s.get('codigo','—')} — {s.get('descripcion','—')}
                        &nbsp; {activo_b}
                    </div>
                    <div class="row-sub">
                        👤 {s.get('empleado','—')} &nbsp;|&nbsp;
                        🚛 {s.get('matricula','—')} &nbsp;|&nbsp;
                        🕐 {s.get('horario_inicio','—')}–{s.get('horario_fin','—')}
                        &nbsp;|&nbsp; {s.get('dias_servicio','—')}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col_act:
            if st.button("Ver →", key=f"srv_{s['id']}"):
                st.session_state["selected_servicio"] = s["id"]
                st.rerun()


def render():
    if st.session_state.get("selected_servicio"):
        ficha_servicio(st.session_state["selected_servicio"])
    else:
        lista_servicios()
