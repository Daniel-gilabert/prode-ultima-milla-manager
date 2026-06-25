import streamlit as st
from utils import (
    GLOBAL_CSS, check_login, render_sidebar, page_header,
    metric_card, query
)

# ── Siempre lo primero ──
st.set_page_config(
    page_title="PRODE · Última Milla",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────────
def pantalla_login():
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown("## 🚚 PRODE · Última Milla")
        st.markdown("*Gestión de asistencia y rutas — Fundación PRODE*")
        st.markdown("---")
        username = st.text_input("Usuario", placeholder="Tu usuario")
        password = st.text_input("Contraseña", type="password", placeholder="••••••••")
        if st.button("Entrar →", use_container_width=True):
            if not username or not password:
                st.warning("Completa usuario y contraseña.")
            else:
                with st.spinner("Verificando..."):
                    ok, rol = check_login(username, password)
                if ok:
                    st.session_state["login"]   = True
                    st.session_state["usuario"] = username.strip()
                    st.session_state["rol"]     = rol
                    st.session_state["page"]    = "Dashboard"
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos.")
        st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────
def pagina_dashboard():
    page_header("📊", "Dashboard")

    empleados = query("SELECT COUNT(*) AS n FROM empleados WHERE activo = TRUE")
    vehiculos = query("SELECT COUNT(*) AS n FROM vehiculos")
    servicios = query("SELECT COUNT(*) AS n FROM servicios")
    ausencias = query(
        "SELECT COUNT(*) AS n FROM ausencias "
        "WHERE fecha_inicio <= CURRENT_DATE AND (fecha_fin IS NULL OR fecha_fin >= CURRENT_DATE)"
    )

    n_emp = empleados[0]["n"] if empleados else "—"
    n_veh = vehiculos[0]["n"] if vehiculos else "—"
    n_srv = servicios[0]["n"] if servicios else "—"
    n_aus = ausencias[0]["n"] if ausencias else "—"

    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card("👥 Empleados activos", n_emp, "blue")
    with c2: metric_card("🚛 Vehículos", n_veh, "orange")
    with c3: metric_card("📋 Servicios", n_srv, "green")
    with c4: metric_card("📅 Ausencias hoy", n_aus, "yellow")

    st.markdown("---")
    col_a, col_b = st.columns([1.2, 1])

    with col_a:
        st.markdown("#### Ausencias recientes")
        rows = query("""
            SELECT e.nombre, e.apellidos, a.tipo, a.fecha_inicio, a.fecha_fin
            FROM ausencias a
            JOIN empleados e ON e.id = a.empleado_id
            ORDER BY a.fecha_inicio DESC LIMIT 8
        """)
        if rows:
            import pandas as pd
            df = pd.DataFrame(rows)
            df.columns = ["Nombre", "Apellidos", "Tipo", "Inicio", "Fin"]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No hay ausencias registradas.")

    with col_b:
        st.markdown("#### ITVs próximas a vencer")
        rows_itv = query("""
            SELECT matricula, marca, modelo, itv_vigente_hasta,
                   (itv_vigente_hasta - CURRENT_DATE) AS dias
            FROM vehiculos
            WHERE itv_vigente_hasta IS NOT NULL
              AND itv_vigente_hasta >= CURRENT_DATE
            ORDER BY itv_vigente_hasta ASC LIMIT 6
        """)
        if rows_itv:
            import pandas as pd
            df2 = pd.DataFrame(rows_itv)
            df2.columns = ["Matrícula", "Marca", "Modelo", "ITV hasta", "Días"]
            st.dataframe(df2, use_container_width=True, hide_index=True)
        else:
            st.info("Sin datos de ITV.")

# ─────────────────────────────────────────────
# ROUTER
# ─────────────────────────────────────────────
if not st.session_state.get("login"):
    pantalla_login()
else:
    render_sidebar()
    page = st.session_state.get("page", "Dashboard")

    if page == "Dashboard":
        pagina_dashboard()
    elif page == "Empleados":
        from pages.empleados import render
        render()
    elif page == "Vehiculos":
        from pages.vehiculos import render
        render()
    elif page == "Servicios":
        from pages.servicios import render
        render()
    elif page == "Ausencias":
        from pages.ausencias import render
        render()
