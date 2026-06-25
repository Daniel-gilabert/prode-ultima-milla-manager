"""pages/ausencias.py — Vista global de ausencias, bajas y vacaciones."""
import streamlit as st
import datetime
from utils import query, execute, page_header, badge


TIPO_COLORS = {
    "Vacaciones":             "blue",
    "Baja médica":            "red",
    "Ausencia justificada":   "yellow",
    "Ausencia injustificada": "orange",
    "Otro":                   "blue",
}


def render():
    page_header("📅", "Ausencias · Bajas · Vacaciones")

    # ── Filtros ──
    col1, col2, col3, col4 = st.columns([1.5, 1.2, 1, 1])
    with col1:
        empleados_list = query(
            "SELECT id, nombre || ' ' || apellidos AS nombre_completo "
            "FROM empleados WHERE activo=TRUE ORDER BY apellidos"
        )
        opciones_emp = {"Todos los empleados": None}
        opciones_emp.update({e["nombre_completo"]: e["id"] for e in empleados_list})
        sel_emp = st.selectbox("Empleado", list(opciones_emp.keys()),
                               label_visibility="collapsed")
        emp_id_filtro = opciones_emp[sel_emp]

    with col2:
        tipo_filtro = st.selectbox("Tipo", [
            "Todos los tipos", "Vacaciones", "Baja médica",
            "Ausencia justificada", "Ausencia injustificada", "Otro"
        ], label_visibility="collapsed")

    with col3:
        fecha_desde = st.date_input("Desde",
                                    value=datetime.date.today().replace(month=1, day=1),
                                    label_visibility="collapsed")
    with col4:
        fecha_hasta = st.date_input("Hasta",
                                    value=datetime.date.today(),
                                    label_visibility="collapsed")

    # ── Query ──
    where  = ["a.fecha_inicio <= %s", "a.fecha_fin >= %s"]
    params = [fecha_hasta, fecha_desde]

    if emp_id_filtro:
        where.append("a.empleado_id = %s")
        params.append(emp_id_filtro)
    if tipo_filtro != "Todos los tipos":
        where.append("a.tipo = %s")
        params.append(tipo_filtro)

    sql = """
        SELECT a.id, e.nombre || ' ' || e.apellidos AS empleado,
               a.tipo, a.fecha_inicio, a.fecha_fin,
               (a.fecha_fin - a.fecha_inicio + 1) AS dias,
               a.observaciones
        FROM ausencias a
        JOIN empleados e ON e.id = a.empleado_id
        WHERE """ + " AND ".join(where) + """
        ORDER BY a.fecha_inicio DESC
    """
    rows = query(sql, params)

    # ── Métricas rápidas ──
    total_dias = sum(r.get("dias") or 0 for r in rows)
    tipos_count = {}
    for r in rows:
        tipos_count[r["tipo"]] = tipos_count.get(r["tipo"], 0) + 1

    mc1, mc2, mc3, mc4 = st.columns(4)
    with mc1:
        st.markdown(f"""<div class="card card-blue">
            <div class="metric-label">Total registros</div>
            <div class="metric-value">{len(rows)}</div>
        </div>""", unsafe_allow_html=True)
    with mc2:
        st.markdown(f"""<div class="card card-orange">
            <div class="metric-label">Días totales</div>
            <div class="metric-value">{total_dias}</div>
        </div>""", unsafe_allow_html=True)
    with mc3:
        n_vac = tipos_count.get("Vacaciones", 0)
        st.markdown(f"""<div class="card card-green">
            <div class="metric-label">Vacaciones</div>
            <div class="metric-value">{n_vac}</div>
        </div>""", unsafe_allow_html=True)
    with mc4:
        n_baja = tipos_count.get("Baja médica", 0)
        st.markdown(f"""<div class="card card-yellow">
            <div class="metric-label">Bajas médicas</div>
            <div class="metric-value">{n_baja}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Tabla de resultados ──
    col_tabla, col_form = st.columns([1.8, 1])

    with col_tabla:
        if not rows:
            st.info("No hay ausencias con los filtros seleccionados.")
        else:
            for r in rows:
                color = TIPO_COLORS.get(r["tipo"], "blue")
                b = badge(r["tipo"], color)
                obs = r.get("observaciones") or "—"
                st.markdown(f"""
                <div class="card" style="padding:0.9rem 1.2rem;margin-bottom:0.4rem;
                                         border-left:4px solid var(--{'orange' if color=='orange' else color});">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <div>
                            <span style="font-weight:700;color:#1C2B3A;">
                                {r['empleado']}
                            </span>
                            &nbsp;{b}
                        </div>
                        <div style="font-size:0.8rem;color:#5A6D82;">
                            {r['fecha_inicio']} → {r['fecha_fin']}
                            &nbsp;·&nbsp; <b>{r['dias']} día(s)</b>
                        </div>
                    </div>
                    <div style="font-size:0.78rem;color:#5A6D82;margin-top:4px;">
                        💬 {obs}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ── Formulario nueva ausencia ──
    with col_form:
        st.markdown("#### ➕ Registrar ausencia")
        with st.container():
            st.markdown('<div class="card card-orange">', unsafe_allow_html=True)
            emp_opts = {e["nombre_completo"]: e["id"] for e in empleados_list}
            sel_emp_form = st.selectbox("Empleado *", list(emp_opts.keys()),
                                        key="nueva_aus_emp")
            tipo_nuevo = st.selectbox("Tipo *", list(TIPO_COLORS.keys()),
                                      key="nueva_aus_tipo")
            f_ini = st.date_input("Fecha inicio *", key="nueva_aus_ini")
            f_fin = st.date_input("Fecha fin *",    key="nueva_aus_fin",
                                  value=datetime.date.today())
            obs_nuevo = st.text_area("Observaciones", height=80, key="nueva_aus_obs")

            if st.button("💾 Guardar ausencia", use_container_width=True):
                if f_fin < f_ini:
                    st.warning("La fecha fin debe ser posterior a la de inicio.")
                else:
                    emp_id_nuevo = emp_opts[sel_emp_form]
                    ok = execute("""
                        INSERT INTO ausencias
                        (empleado_id, tipo, fecha_inicio, fecha_fin, observaciones)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (emp_id_nuevo, tipo_nuevo, f_ini, f_fin, obs_nuevo))
                    if ok:
                        st.success("✅ Ausencia registrada.")
                        st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
