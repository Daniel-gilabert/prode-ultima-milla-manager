"""pages/vehiculos.py — Lista de vehículos, ficha, check-in de estado."""
import streamlit as st
from utils import query, execute, page_header, back_button, badge
from utils_storage import subir_foto
import datetime
import json

# ─────────────────────────────────────────────
# IMÁGENES GENÉRICAS POR MARCA
# Las URLs son imágenes públicas de ejemplo.
# Para añadir una marca nueva: ve a "⚙️ Gestionar marcas" en la lista de vehículos.
# Las marcas personalizadas se guardan en st.session_state["marcas_extra"].
# ─────────────────────────────────────────────
MARCAS_DEFAULT = {
    "paxter":  "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/240px-PNG_transparency_demonstration_1.png",
    "scoobic": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/240px-PNG_transparency_demonstration_1.png",
    "renault": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/240px-PNG_transparency_demonstration_1.png",
}

# Emojis representativos por marca mientras no haya foto real
MARCA_EMOJI = {
    "paxter":  "🛵",
    "scoobic": "🛺",
    "renault": "🚐",
}

SUPABASE_URL = "https://drjnffoyzuploatfcltf.supabase.co"
MARCA_FOTOS = {
    "paxter":  f"{SUPABASE_URL}/storage/v1/object/public/fotos-app/marcas/paxtser.jpg",
    "scoobic": f"{SUPABASE_URL}/storage/v1/object/public/fotos-app/marcas/scoobic.jpg",
    "renault": f"{SUPABASE_URL}/storage/v1/object/public/fotos-app/marcas/renault.jpg",
}

def get_marca_foto(marca: str) -> str:
    """Devuelve la URL de la foto genérica de la marca, o cadena vacía si no existe."""
    return MARCA_FOTOS.get(marca.lower().strip(), "")

CHECKLIST_ITEMS = [
    ("carroceria",    "🚗 Carrocería exterior"),
    ("ruedas",        "🔧 Ruedas y neumáticos"),
    ("luces",         "💡 Luces delanteras y traseras"),
    ("cristales",     "🪟 Cristales y espejos"),
    ("interior",      "💺 Interior y limpieza"),
    ("frenos",        "🛑 Frenos"),
    ("nivel_aceite",  "🛢️ Nivel de aceite"),
    ("documentacion", "📄 Documentación en vehículo"),
]

ESTADO_OPTS = ["✅ Correcto", "⚠️ Revisar", "❌ Defecto"]


def get_marcas():
    """Devuelve lista de marcas disponibles (default + añadidas por usuario)."""
    extra = st.session_state.get("marcas_extra", [])
    base  = ["Paxter", "Scoobic", "Renault"]
    return base + [m for m in extra if m not in base]


def get_emoji(marca: str) -> str:
    return MARCA_EMOJI.get(marca.lower().strip(), "🚛")


# ─────────────────────────────────────────────
# CHECK-IN
# ─────────────────────────────────────────────
def tab_checkin(veh_id: int, matricula: str):
    st.markdown("### 📋 Registro de estado del vehículo")
    st.caption("Rellena el estado actual. Puedes subir fotos por cada punto.")

    # Historial de check-ins anteriores
    historico = query("""
        SELECT fecha, responsable, estado_json, observaciones
        FROM checkins_vehiculo
        WHERE vehiculo_id = %s
        ORDER BY fecha DESC LIMIT 5
    """, (veh_id,))

    if historico:
        with st.expander(f"📂 Últimos {len(historico)} check-ins registrados"):
            for h in historico:
                est = json.loads(h["estado_json"]) if h.get("estado_json") else {}
                st.markdown(f"**{h['fecha']}** — {h.get('responsable','—')}")
                cols = st.columns(4)
                for i, (key, label) in enumerate(CHECKLIST_ITEMS):
                    cols[i % 4].markdown(f"{label}: **{est.get(key,'—')}**")
                if h.get("observaciones"):
                    st.caption(f"💬 {h['observaciones']}")
                st.markdown("---")

    st.markdown("#### ➕ Nuevo check-in")
    responsable = st.text_input("Responsable del check-in",
                                value=st.session_state.get("usuario", ""))

    estado_resultado = {}
    cols_check = st.columns(2)
    for i, (key, label) in enumerate(CHECKLIST_ITEMS):
        with cols_check[i % 2]:
            val = st.selectbox(label, ESTADO_OPTS, key=f"chk_{veh_id}_{key}")
            estado_resultado[key] = val

    observaciones = st.text_area("Observaciones generales", height=80,
                                  key=f"chk_obs_{veh_id}")

    st.markdown("#### 📸 Fotos del estado")
    fotos = st.file_uploader(
        "Sube fotos del vehículo (puedes subir varias)",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        key=f"fotos_{veh_id}"
    )
    if fotos:
        cols_fotos = st.columns(min(len(fotos), 4))
        for i, foto in enumerate(fotos):
            cols_fotos[i % 4].image(foto, use_column_width=True,
                                     caption=foto.name)

    if st.button("💾 Guardar check-in", key=f"save_chk_{veh_id}",
                 use_container_width=True):
        # Intentar guardar en tabla checkins_vehiculo si existe
        ok = execute("""
            INSERT INTO checkins_vehiculo
            (vehiculo_id, fecha, responsable, estado_json, observaciones)
            VALUES (%s, %s, %s, %s, %s)
        """, (veh_id, datetime.date.today(), responsable,
              json.dumps(estado_resultado), observaciones))
        if ok:
            st.success("✅ Check-in registrado correctamente.")
            st.rerun()
        else:
            # Si la tabla no existe todavía, mostrar resumen igualmente
            st.warning(
                "⚠️ La tabla `checkins_vehiculo` no existe aún en Supabase. "
                "Créala con esta SQL y vuelve a intentarlo:"
            )
            st.code("""
CREATE TABLE checkins_vehiculo (
  id              SERIAL PRIMARY KEY,
  vehiculo_id     INT REFERENCES vehiculos(id),
  fecha           DATE NOT NULL DEFAULT CURRENT_DATE,
  responsable     TEXT,
  estado_json     TEXT,
  observaciones   TEXT,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);
            """, language="sql")


# ─────────────────────────────────────────────
# FICHA DE VEHÍCULO
# ─────────────────────────────────────────────
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
    foto_url      = v.get("foto_url", "") or get_marca_foto(marca)

    col_img, col_info = st.columns([0.18, 0.82])
    with col_img:
        if foto_url:
            st.image(foto_url, width=80)
        else:
            st.markdown(f"""
            <div style="width:80px;height:80px;border-radius:12px;
                        background:rgba(27,58,107,0.08);
                        display:flex;align-items:center;justify-content:center;
                        font-size:2.8rem;">{emoji}</div>
            """, unsafe_allow_html=True)
        foto_file = st.file_uploader("📷", type=["jpg","jpeg","png"],
                                      key=f"foto_veh_{veh_id}",
                                      label_visibility="collapsed")
        if foto_file:
            ext = foto_file.name.split(".")[-1]
            url = subir_foto(foto_file, "vehiculos", f"vehiculo_{veh_id}.{ext}")
            if url:
                ok = execute("UPDATE vehiculos SET foto_url=%s WHERE id=%s",
                             (url, veh_id))
                if ok:
                    st.success("✅ Foto actualizada.")
                    st.rerun()
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
        "🔧 Datos del vehículo",
        "📋 Check-in de estado",
        "👥 Empleados asignados"
    ])

    with tab_datos:
        marcas_disp = get_marcas()
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
            itv_v       = st.date_input("ITV vigente hasta",
                                        value=itv_fecha or hoy)
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


# ─────────────────────────────────────────────
# LISTA DE VEHÍCULOS
# ─────────────────────────────────────────────
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

    # ── Panel gestión de marcas ──
    if st.session_state.get("gestionar_marcas"):
        with st.expander("⚙️ Marcas disponibles", expanded=True):
            marcas_actuales = get_marcas()
            st.markdown("**Marcas actuales:**")
            for m in marcas_actuales:
                st.markdown(f"- {get_emoji(m)} {m}")
            st.markdown("---")
            nueva_marca = st.text_input("Añadir nueva marca",
                                        placeholder="Ej: Citroën, Ford…",
                                        key="input_nueva_marca")
            if st.button("Añadir marca", key="btn_add_marca"):
                if nueva_marca.strip():
                    extra = st.session_state.get("marcas_extra", [])
                    if nueva_marca.strip() not in extra and nueva_marca.strip() not in ["Paxter","Scoobic","Renault"]:
                        extra.append(nueva_marca.strip())
                        st.session_state["marcas_extra"] = extra
                        st.success(f"Marca '{nueva_marca}' añadida.")
                        st.rerun()

    # ── Formulario nuevo vehículo ──
    if st.session_state.get("nuevo_vehiculo"):
        with st.expander("➕ Nuevo vehículo", expanded=True):
            marcas_disp = get_marcas()
            with st.form("form_nuevo_veh"):
                c1, c2 = st.columns(2)
                with c1:
                    n_mat  = st.text_input("Matrícula *")
                    n_bast = st.text_input("Bastidor")
                    n_marc = st.selectbox("Marca *", marcas_disp)
                    n_mod  = st.text_input("Modelo")
                with c2:
                    n_tipo = st.selectbox("Tipo", ["renting","propiedad"])
                    n_itv  = st.date_input("ITV vigente hasta", value=hoy)
                    n_seg  = st.date_input("Seguro vigente hasta", value=hoy)
                    n_aseg = st.text_input("Aseguradora")
                    n_pol  = st.text_input("Póliza")
                sub = st.form_submit_button("✅ Crear vehículo", use_container_width=True)
                if sub:
                    if not n_mat:
                        st.warning("La matrícula es obligatoria.")
                    else:
                        ok = execute("""
                            INSERT INTO vehiculos
                            (matricula, bastidor, marca, modelo, tipo,
                             itv_vigente_hasta, seguro_vigente_hasta,
                             aseguradora, poliza)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        """, (n_mat, n_bast, n_marc, n_mod, n_tipo,
                              n_itv, n_seg, n_aseg, n_pol))
                        if ok:
                            st.success(f"Vehículo {n_mat} creado correctamente.")
                            st.session_state["nuevo_vehiculo"] = False
                            st.rerun()

    # ── Filtros BD ──
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
        itv_v    = v.get("itv_vigente_hasta")
        marca    = v.get("marca","")
        emoji    = get_emoji(marca)
        foto_url = v.get("foto_url","") or get_marca_foto(marca)

        if itv_v and itv_v <= hoy:
            alerta = "🔴"
        elif itv_v and (itv_v - hoy).days <= 30:
            alerta = "🟡"
        else:
            alerta = "🟢"

        tipo_b = badge(v.get("tipo","—"),
                       "orange" if v.get("tipo") == "renting" else "blue")

        if foto_url:
            avatar_veh = f'<img src="{foto_url}" style="width:48px;height:48px;border-radius:8px;object-fit:cover;flex-shrink:0;">'
        else:
            avatar_veh = f'<div class="row-avatar" style="background:rgba(27,58,107,0.08);color:#1B3A6B;font-size:1.6rem;width:48px;height:48px;">{emoji}</div>'

        col_main, col_act = st.columns([5, 0.8])
        with col_main:
            st.markdown(f"""
            <div class="row-card">
                {avatar_veh}
                <div>
                    <div class="row-name">
                        {v.get('matricula','—')} &nbsp; {tipo_b}
                    </div>
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


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────
def render():
    if st.session_state.get("selected_vehiculo"):
        ficha_vehiculo(st.session_state["selected_vehiculo"])
    else:
        lista_vehiculos()
