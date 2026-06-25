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

    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:1rem;margin-bottom:1rem;">
        <span style="font-size:2rem">📋</span>
        <div>
            <h2 style="margin:0;color:#1B3A6B;font-weight:800;">
                {s.get('codigo','—')} — {s.get('nombre_linea') or s.get('nombre','—')}
            </h2>
            <p style="color:#5A6D82;margin:4px 0 0;">
                Fecha: {s.get('fecha','—')}
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    tab_datos, tab_emp, tab_veh = st.tabs([
        "📋 Datos del servicio", "👥 Empleado asignado", "🚛 Vehículo asignado"
    ])

    with tab_datos:
        st.markdown('<div class="card card-green">', unsafe_allow_html=True)
        # Mostrar todos los campos disponibles del servicio
        cols = [k for k in s.keys() if k not in ("id",)]
        c1_cols = cols[:len(cols)//2]
        c2_cols = cols[len(cols)//2:]
        c1, c2 = st.columns(2)
        with c1:
            for k in c1_cols:
                st.text_input(k.replace("_"," ").title(), value=str(s.get(k,"") or ""),
                              key=f"srv_f_{k}", disabled=True)
        with c2:
            for k in c2_cols:
                st.text_input(k.replace("_"," ").title(), value=str(s.get(k,"") or ""),
                              key=f"srv_f2_{k}", disabled=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.caption("Edición de servicios próximamente.")

    with tab_emp:
        if s.get("empleado_id"):
            emp = query("SELECT * FROM empleados WHERE id = %s", (s["empleado_id"],))
            if emp:
                e = emp[0]
                st.markdown(f"""
                <div class="row-card">
                    <div class="row-avatar">{e['nombre'][0]}{e['apellidos'][0]}</div>
                    <div>
                        <div class="row-name">{e['nombre']} {e['apellidos']}</div>
                        <div class="row-sub">📧 {e.get('email','—')} | 📱 {e.get('telefono','—')}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Ver ficha del empleado"):
                    st.session_state["selected_empleado"] = e["id"]
                    st.session_state["page"] = "Empleados"
                    st.session_state.pop("selected_servicio", None)
                    st.rerun()
        else:
            st.info("Sin empleado asignado.")

    with tab_veh:
        if s.get("vehiculo_id"):
            veh = query("SELECT * FROM vehiculos WHERE id = %s", (s["vehiculo_id"],))
            if veh:
                v = veh[0]
                st.markdown(f"""
                <div class="row-card">
                    <div class="row-avatar" style="font-size:1.3rem;
                        background:rgba(27,58,107,0.10);color:#1B3A6B;">🚛</div>
                    <div>
                        <div class="row-name">{v.get('matricula','—')} — {v.get('marca','')} {v.get('modelo','')}</div>
                        <div class="row-sub">Tipo: {v.get('tipo','—')} | ITV: {v.get('itv_vigente_hasta','—')}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Ver ficha del vehículo"):
                    st.session_state["selected_vehiculo"] = v["id"]
                    st.session_state["page"] = "Vehiculos"
                    st.session_state.pop("selected_servicio", None)
                    st.rerun()
        else:
            st.info("Sin vehículo asignado.")


def lista_servicios():
    page_header("📋", "Servicios")

    col_s, col_btn = st.columns([3, 0.9])
    with col_s:
        buscar = st.text_input("🔍 Buscar por código o línea",
                               label_visibility="collapsed",
                               placeholder="Ej: SVC-001…")
    with col_btn:
        pass  # reservado para nuevo servicio

    where, params = [], []
    if buscar:
        where.append("(codigo ILIKE %s OR nombre_linea ILIKE %s)")
        params += [f"%{buscar}%"] * 2

    sql = "SELECT s.*, e.nombre AS emp_nombre, e.apellidos AS emp_apellidos, v.matricula FROM servicios s LEFT JOIN empleados e ON e.id = s.empleado_id LEFT JOIN vehiculos v ON v.id = s.vehiculo_id"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY s.id DESC LIMIT 100"

    servicios = query(sql, params or None)
    st.markdown(f"**{len(servicios)} servicio(s)**")
    st.markdown("---")

    for s in servicios:
        col_main, col_act = st.columns([5, 0.8])
        emp_txt = f"{s.get('emp_nombre','')} {s.get('emp_apellidos','')}".strip() or "—"
        with col_main:
            st.markdown(f"""
            <div class="row-card">
                <div class="row-avatar" style="background:rgba(26,140,91,0.10);
                            color:#1A8C5B;font-size:1.3rem;">📋</div>
                <div>
                    <div class="row-name">{s.get('codigo','—')} — {s.get('nombre_linea') or '—'}</div>
                    <div class="row-sub">
                        👤 {emp_txt} &nbsp;|&nbsp;
                        🚛 {s.get('matricula','—')} &nbsp;|&nbsp;
                        📅 {s.get('fecha','—')}
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
