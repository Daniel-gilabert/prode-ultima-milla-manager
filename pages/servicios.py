def ficha_vehiculo(veh_id: int):
    rows = query("SELECT * FROM vehiculos WHERE id = %s", (veh_id,))
    if not rows:
        st.error("Vehículo no encontrado.")
        return
    v = rows[0]

    if back_button("← Volver a vehículos"):
        st.session_state.pop("selected_vehiculo", None)
        st.rerun()

    hoy       = datetime.date.today()
    itv_fecha = v.get("itv_vigente_hasta")
    seg_fecha = v.get("seguro_vigente_hasta")

    if itv_fecha and itv_fecha <= hoy:
        st.error(f"⚠️ ITV vencida el {itv_fecha}")
    elif itv_fecha and (itv_fecha - hoy).days <= 30:
        st.warning(f"⚠️ ITV vence en {(itv_fecha - hoy).days} días ({itv_fecha})")
    if seg_fecha and seg_fecha <= hoy:
        st.error(f"⚠️ Seguro vencido el {seg_fecha}")
    elif seg_fecha and (seg_fecha - hoy).days <= 30:
        st.warning(f"⚠️ Seguro vence en {(seg_fecha - hoy).days} días ({seg_fecha})")

    marca      = v.get("marca", "")
    emoji      = get_emoji(marca)
    tipo_color = "orange" if str(v.get("tipo","")).lower() == "renting" else "blue"

    col_img, col_info = st.columns([0.18, 0.82])
    with col_img:
        st.markdown(f"""
        <div style="width:80px;height:80px;border-radius:12px;
                    background:rgba(27,58,107,0.08);
                    display:flex;align-items:center;justify-content:center;
                    font-size:2.8rem;">{emoji}</div>
        """, unsafe_allow_html=True)
    with col_info:
        st.markdown(f"""
        <h2 style="margin:0;color:#1B3A6B;font-weight:800;">
            {v.get('matricula','—')} &nbsp; {badge(v.get('tipo','—'), tipo_color)}
        </h2>
        <p style="color:#5A6D82;margin:4px 0 0;">
            {marca} {v.get('modelo','—')}
            &nbsp;|&nbsp; Bastidor: {v.get('bastidor','—')}
        </p>
        """, unsafe_allow_html=True)

    st.markdown("---")

    tab_datos, tab_checkin_t, tab_empleados = st.tabs([
        "🔧 Datos del vehículo", "📋 Check-in de estado", "👥 Empleados asignados"
    ])

    with tab_datos:
        marcas_disp  = get_marcas()
        marca_actual = marca if marca in marcas_disp else marcas_disp[0]
        c1, c2 = st.columns(2)
        with c1:
            matricula   = st.text_input("Matrícula",  value=v.get("matricula",""))
            bastidor    = st.text_input("Bastidor",   value=v.get("bastidor",""))
            marca_sel   = st.selectbox("Marca", marcas_disp,
                                       index=marcas_disp.index(marca_actual)
                                       if marca_actual in marcas_disp else 0)
            modelo      = st.text_input("Modelo",     value=v.get("modelo",""))
        with c2:
            tipo        = st.selectbox("Tipo", ["renting","propiedad"],
                                       index=0 if v.get("tipo","renting")=="renting" else 1)
            itv_v       = st.date_input("ITV vigente hasta", value=itv_fecha or hoy)
            aseguradora = st.text_input("Aseguradora", value=v.get("aseguradora","") or "")
            poliza      = st.text_input("Póliza",      value=v.get("poliza","") or "")
        if st.button("💾 Guardar cambios", key="save_veh"):
            ok = execute("""
                UPDATE vehiculos
                SET matricula=%s, bastidor=%s, marca=%s, modelo=%s,
                    tipo=%s, itv_vigente_hasta=%s, aseguradora=%s, poliza=%s
                WHERE id=%s
            """, (matricula, bastidor, marca_sel, modelo,
                  tipo, itv_v, aseguradora, poliza, veh_id))
            if ok:
                st.success("Vehículo actualizado.")

    with tab_checkin_t:
        tab_checkin(veh_id, v.get("matricula",""))

    with tab_empleados:
        emp_rows = query("""
            SELECT DISTINCT e.id, e.nombre, e.apellidos, e.email
            FROM servicios s
            JOIN empleados e ON e.id = s.empleado_base_id
            WHERE s.vehiculo_base_id = %s
            ORDER BY e.apellidos
        """, (veh_id,))
        if emp_rows:
            for emp in emp_rows:
                ini = (emp['nombre'][0] + emp['apellidos'][0]).upper()
                st.markdown(f"""
                <div class="row-card">
                    <div class="row-avatar">{ini}</div>
                    <div>
                        <div class="row-name">{emp['nombre']} {emp['apellidos']}</div>
                        <div class="row-sub">📧 {emp.get('email','—')}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Ningún empleado asignado a este vehículo en servicios.")


def lista_vehiculos():
    page_header("🚛", "Vehículos")
    hoy = datetime.date.today()

    col_s, col_t, col_btn, col_marca = st.columns([2, 1, 1, 1])
    with col_s:
        buscar = st.text_input("🔍 Buscar", label_visibility="collapsed",
                               placeholder="Matrícula, marca, modelo…")
    with col_t:
        filtro_tipo = st.selectbox("Tipo", ["Todos","Renting","Propiedad"],
                                   label_visibility="collapsed")
    with col_btn:
        if st.button("➕ Nuevo vehículo", use_container_width=True):
            st.session_state["nuevo_vehiculo"] = not st.session_state.get("nuevo_vehiculo", False)
    with col_marca:
        if st.button("⚙️ Gestionar marcas", use_container_width=True):
            st.session_state["gestionar_marcas"] = not st.session_state.get("gestionar_marcas", False)

    if st.session_state.get("gestionar_marcas"):
        with st.expander("⚙️ Marcas disponibles", expanded=True):
            for m in get_marcas():
                st.markdown(f"- {get_emoji(m)} {m}")
            st.markdown("---")
            nueva_marca = st.text_input("Añadir nueva marca", key="input_nueva_marca")
            if st.button("Añadir marca", key="btn_add_marca"):
                if nueva_marca.strip():
                    extra = st.session_state.get("marcas_extra", [])
                    if nueva_marca.strip() not in extra and nueva_marca.strip() not in ["Paxter","Scoobic","Renault"]:
                        extra.append(nueva_marca.strip())
                        st.session_state["marcas_extra"] = extra
                        st.success(f"Marca '{nueva_marca}' añadida.")
                        st.rerun()

    if st.session_state.get("nuevo_vehiculo"):
        with st.expander("➕ Nuevo vehículo", expanded=True):
            with st.form("form_nuevo_veh"):
                c1, c2 = st.columns(2)
                with c1:
                    n_mat  = st.text_input("Matrícula *")
                    n_bast = st.text_input("Bastidor")
                    n_marc = st.selectbox("Marca *", get_marcas())
                    n_mod  = st.text_input("Modelo")
                with c2:
                    n_tipo = st.selectbox("Tipo", ["renting","propiedad"])
                    n_itv  = st.date_input("ITV vigente hasta", value=hoy)
                    n_seg  = st.date_input("Seguro vigente hasta", value=hoy)
                    n_aseg = st.text_input("Aseguradora")
                    n_pol  = st.text_input("Póliza")
                if st.form_submit_button("✅ Crear vehículo", use_container_width=True):
                    if not n_mat:
                        st.warning("La matrícula es obligatoria.")
                    else:
                        ok = execute("""
                            INSERT INTO vehiculos
                            (matricula, bastidor, marca, modelo, tipo,
                             itv_vigente_hasta, seguro_vigente_hasta, aseguradora, poliza)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        """, (n_mat, n_bast, n_marc, n_mod, n_tipo,
                              n_itv, n_seg, n_aseg, n_pol))
                        if ok:
                            st.success(f"Vehículo {n_mat} creado.")
                            st.session_state["nuevo_vehiculo"] = False
                            st.rerun()

    where, params = [], []
    if buscar:
        where.append("(matricula ILIKE %s OR marca ILIKE %s OR modelo ILIKE %s)")
        params += [f"%{buscar}%"] * 3
    if filtro_tipo == "Renting":
        where.append("tipo = 'renting'")
    elif filtro_tipo == "Propiedad":
        where.append("tipo = 'propiedad'")

    sql = "SELECT * FROM vehiculos"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY matricula"

    vehiculos = query(sql, params or None)
    st.markdown(f"**{len(vehiculos)} vehículo(s)**")
    st.markdown("---")

    for v in vehiculos:
        itv_v = v.get("itv_vigente_hasta")
        marca = v.get("marca","")
        emoji = get_emoji(marca)
        alerta = "🔴" if itv_v and itv_v <= hoy else ("🟡" if itv_v and (itv_v - hoy).days <= 30 else "🟢")
        tipo_b = badge(v.get("tipo","—"), "orange" if v.get("tipo") == "renting" else "blue")

        col_main, col_act = st.columns([5, 0.8])
        with col_main:
            st.markdown(f"""
            <div class="row-card">
                <div class="row-avatar" style="background:rgba(27,58,107,0.08);
                     color:#1B3A6B;font-size:1.6rem;width:48px;height:48px;">
                    {emoji}
                </div>
                <div>
                    <div class="row-name">{v.get('matricula','—')} &nbsp; {tipo_b}</div>
                    <div class="row-sub">
                        {marca} {v.get('modelo','—')}
                        &nbsp;|&nbsp; ITV: {alerta} {itv_v or '—'}
                        &nbsp;|&nbsp; Bastidor: {v.get('bastidor','—')}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col_act:
            if st.button("Ver →", key=f"veh_{v['id']}"):
                st.session_state["selected_vehiculo"] = v["id"]
                st.rerun()


def render():
    if st.session_state.get("selected_vehiculo"):
        ficha_vehiculo(st.session_state["selected_vehiculo"])
    else:
        lista_vehiculos()
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
