"""pages/vehiculos.py — Lista de vehículos y ficha individual."""
import streamlit as st
from utils import query, execute, page_header, back_button, badge
import datetime

def ficha_vehiculo(veh_id: int):
    rows = query("SELECT * FROM vehiculos WHERE id = %s", (veh_id,))
    if not rows:
        st.error("Vehículo no encontrado.")
        return
    v = rows[0]

    if back_button("← Volver a vehículos"):
        st.session_state.pop("selected_vehiculo", None)
        st.rerun()

    # Alertas de vencimiento
    hoy = datetime.date.today()
    itv_fecha   = v.get("itv_vigente_hasta")
    seg_fecha   = v.get("seguro_vigente_hasta")

    if itv_fecha and itv_fecha <= hoy:
        st.error(f"⚠️ ITV vencida el {itv_fecha}")
    elif itv_fecha and (itv_fecha - hoy).days <= 30:
        st.warning(f"⚠️ ITV vence en {(itv_fecha - hoy).days} días ({itv_fecha})")

    if seg_fecha and seg_fecha <= hoy:
        st.error(f"⚠️ Seguro vencido el {seg_fecha}")
    elif seg_fecha and (seg_fecha - hoy).days <= 30:
        st.warning(f"⚠️ Seguro vence en {(seg_fecha - hoy).days} días ({seg_fecha})")

    # Cabecera
    tipo_color = {"renting": "orange", "propiedad": "blue"}.get(
        str(v.get("tipo","")).lower(), "blue"
    )
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:1rem;margin-bottom:1rem;">
        <span style="font-size:2.5rem">🚛</span>
        <div>
            <h2 style="margin:0;color:#1B3A6B;font-weight:800;">
                {v.get('matricula','—')}
                &nbsp;{badge(v.get('tipo','—'), tipo_color)}
            </h2>
            <p style="color:#5A6D82;margin:4px 0 0;">
                {v.get('marca','—')} {v.get('modelo','—')}
                &nbsp;|&nbsp; Bastidor: {v.get('bastidor','—')}
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    tab_datos, tab_docs, tab_empleados = st.tabs([
        "🔧 Datos del vehículo", "📄 Documentación", "👥 Empleados asignados"
    ])

    with tab_datos:
        st.markdown('<div class="card card-orange">', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            matricula  = st.text_input("Matrícula",  value=v.get("matricula",""))
            bastidor   = st.text_input("Bastidor",   value=v.get("bastidor",""))
            marca      = st.text_input("Marca",      value=v.get("marca",""))
            modelo     = st.text_input("Modelo",     value=v.get("modelo",""))
        with c2:
            tipo       = st.selectbox("Tipo", ["renting","propiedad"],
                                      index=["renting","propiedad"].index(
                                          v.get("tipo","renting")
                                          if v.get("tipo","") in ["renting","propiedad"]
                                          else "renting"))
            itv_v      = st.date_input("ITV vigente hasta",
                                       value=itv_fecha or datetime.date.today())
            aseguradora = st.text_input("Aseguradora", value=v.get("aseguradora",""))
            poliza      = st.text_input("Póliza",      value=v.get("poliza",""))
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("💾 Guardar cambios", key="save_veh"):
            ok = execute("""
                UPDATE vehiculos
                SET matricula=%s, bastidor=%s, marca=%s, modelo=%s,
                    tipo=%s, itv_vigente_hasta=%s, aseguradora=%s, poliza=%s
                WHERE id=%s
            """, (matricula, bastidor, marca, modelo, tipo, itv_v,
                  aseguradora, poliza, veh_id))
            if ok:
                st.success("Vehículo actualizado.")

    with tab_docs:
        st.info("Sección de documentos del vehículo (próximamente).")

    with tab_empleados:
        emp_rows = query("""
            SELECT DISTINCT e.id, e.nombre, e.apellidos, e.email
            FROM servicios s
            JOIN empleados e ON e.id = s.empleado_id
            WHERE s.vehiculo_id = %s
            ORDER BY e.apellidos
        """, (veh_id,))
        if emp_rows:
            for emp in emp_rows:
                st.markdown(f"""
                <div class="row-card">
                    <div class="row-avatar">
                        {emp['nombre'][0]}{emp['apellidos'][0]}
                    </div>
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

    col_s, col_t, col_btn = st.columns([2, 1, 0.9])
    with col_s:
        buscar = st.text_input("🔍 Buscar matrícula, marca o modelo",
                               label_visibility="collapsed",
                               placeholder="Ej: C9227BWP…")
    with col_t:
        filtro_tipo = st.selectbox("Tipo", ["Todos","Renting","Propiedad"],
                                   label_visibility="collapsed")
    with col_btn:
        if st.button("➕ Nuevo vehículo", use_container_width=True):
            st.session_state["nuevo_vehiculo"] = True

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
        if itv_v and itv_v <= hoy:
            alerta = "🔴"
        elif itv_v and (itv_v - hoy).days <= 30:
            alerta = "🟡"
        else:
            alerta = "🟢"

        tipo_b = badge(v.get("tipo","—"),
                       "orange" if v.get("tipo") == "renting" else "blue")

        col_main, col_act = st.columns([5, 0.8])
        with col_main:
            st.markdown(f"""
            <div class="row-card">
                <div class="row-avatar" style="font-size:1.4rem;background:rgba(27,58,107,0.10);
                            color:#1B3A6B;">🚛</div>
                <div>
                    <div class="row-name">
                        {v.get('matricula','—')} &nbsp; {tipo_b}
                    </div>
                    <div class="row-sub">
                        {v.get('marca','—')} {v.get('modelo','—')}
                        &nbsp;|&nbsp; ITV: {alerta} {itv_v or '—'}
                        &nbsp;|&nbsp; Bastidor: {v.get('bastidor','—')}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col_act:
            if st.button("Ver ficha →", key=f"veh_{v['id']}"):
                st.session_state["selected_vehiculo"] = v["id"]
                st.rerun()

    # Nuevo vehículo
    if st.session_state.get("nuevo_vehiculo"):
        st.markdown("---")
        st.markdown("### ➕ Nuevo vehículo")
        with st.form("form_nuevo_veh"):
            c1, c2 = st.columns(2)
            with c1:
                n_mat  = st.text_input("Matrícula *")
                n_bast = st.text_input("Bastidor")
                n_marc = st.text_input("Marca")
                n_mod  = st.text_input("Modelo")
            with c2:
                n_tipo = st.selectbox("Tipo", ["renting","propiedad"])
                n_itv  = st.date_input("ITV vigente hasta")
                n_aseg = st.text_input("Aseguradora")
                n_pol  = st.text_input("Póliza")
            sub = st.form_submit_button("Crear vehículo")
            if sub:
                if not n_mat:
                    st.warning("La matrícula es obligatoria.")
                else:
                    ok = execute("""
                        INSERT INTO vehiculos
                        (matricula, bastidor, marca, modelo, tipo,
                         itv_vigente_hasta, aseguradora, poliza)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    """, (n_mat, n_bast, n_marc, n_mod, n_tipo,
                          n_itv, n_aseg, n_pol))
                    if ok:
                        st.success("Vehículo creado.")
                        st.session_state.pop("nuevo_vehiculo", None)
                        st.rerun()


def render():
    if st.session_state.get("selected_vehiculo"):
        ficha_vehiculo(st.session_state["selected_vehiculo"])
    else:
        lista_vehiculos()
