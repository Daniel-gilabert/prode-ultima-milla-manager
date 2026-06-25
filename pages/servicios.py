"""
pages/servicios.py
VERSIÓN BASE ADAPTADA A LA NUEVA TABLA servicios

IMPORTANTE:
Esta versión corrige los nombres de columnas para tu esquema actual.
Está preparada para ampliarla con alta/edición.
"""

import streamlit as st
from utils import query, page_header, back_button


def ficha_servicio(srv_id:int):
    rows=query("SELECT * FROM servicios WHERE id=%s",(srv_id,))
    if not rows:
        st.error("Servicio no encontrado.")
        return

    s=rows[0]

    if back_button("← Volver"):
        st.session_state.pop("selected_servicio",None)
        st.rerun()

    st.title(f"{s['codigo']} - {s['descripcion']}")

    tab1,tab2,tab3,tab4,tab5=st.tabs([
        "Servicio",
        "Empresa",
        "Contactos",
        "Facturación",
        "Operativa"
    ])

    with tab1:
        st.text_input("Código",s["codigo"],disabled=True)
        st.text_input("Descripción",s["descripcion"],disabled=True)
        st.text_input("Zona",s.get("zona") or "",disabled=True)
        st.text_input("Tipo",s.get("tipo_servicio") or "",disabled=True)
        st.text_input("Días",s.get("dias_servicio") or "",disabled=True)
        st.text_input("Horario inicio",s.get("horario_inicio") or "",disabled=True)
        st.text_input("Horario fin",s.get("horario_fin") or "",disabled=True)
        st.text_area("Observaciones",s.get("observaciones") or "",disabled=True)

    with tab2:
        st.text_input("Empresa",s.get("empresa_nombre") or "",disabled=True)
        st.text_input("CIF",s.get("empresa_cif") or "",disabled=True)
        st.text_input("Dirección",s.get("empresa_direccion") or "",disabled=True)
        st.text_input("CP",s.get("empresa_cp") or "",disabled=True)
        st.text_input("Ciudad",s.get("empresa_ciudad") or "",disabled=True)
        st.text_input("Provincia",s.get("empresa_provincia") or "",disabled=True)
        st.text_input("País",s.get("empresa_pais") or "",disabled=True)

    with tab3:
        st.subheader("Contacto principal")
        st.text_input("Nombre",s.get("contacto_nombre") or "",disabled=True)
        st.text_input("Cargo",s.get("contacto_cargo") or "",disabled=True)
        st.text_input("Email",s.get("contacto_email") or "",disabled=True)
        st.text_input("Teléfono",s.get("contacto_telefono") or "",disabled=True)
        st.text_input("Móvil",s.get("contacto_movil") or "",disabled=True)

        st.divider()

        st.subheader("Segundo contacto")
        st.text_input("Nombre ",s.get("contacto2_nombre") or "",disabled=True)
        st.text_input("Email ",s.get("contacto2_email") or "",disabled=True)
        st.text_input("Teléfono ",s.get("contacto2_telefono") or "",disabled=True)

    with tab4:
        st.text_input("Email facturación",s.get("facturacion_email") or "",disabled=True)
        st.text_input("Forma de pago",s.get("facturacion_forma_pago") or "",disabled=True)
        st.text_input("Tarifa mensual",str(s.get("tarifa_mensual") or ""),disabled=True)
        st.text_input("Número cuenta",s.get("numero_cuenta") or "",disabled=True)

    with tab5:

        emp=query("SELECT * FROM empleados WHERE id=%s",(s["empleado_base_id"],))
        if emp:
            st.success(f"Empleado: {emp[0]['nombre']} {emp[0]['apellidos']}")

        veh=query("SELECT * FROM vehiculos WHERE id=%s",(s["vehiculo_base_id"],))
        if veh:
            st.success(f"Vehículo: {veh[0]['matricula']} - {veh[0].get('marca','')} {veh[0].get('modelo','')}")


def lista_servicios():

    page_header("📋","Servicios")

    buscar=st.text_input(
        "Buscar",
        placeholder="Código, descripción o empresa..."
    )

    sql="""
    SELECT
        s.*,
        e.nombre AS emp_nombre,
        e.apellidos AS emp_apellidos,
        v.matricula
    FROM servicios s
    LEFT JOIN empleados e
        ON e.id=s.empleado_base_id
    LEFT JOIN vehiculos v
        ON v.id=s.vehiculo_base_id
    """

    params=[]

    if buscar:
        sql+=("""
        WHERE
        codigo ILIKE %s
        OR descripcion ILIKE %s
        OR empresa_nombre ILIKE %s
        """)
        params=[
            f"%{buscar}%",
            f"%{buscar}%",
            f"%{buscar}%"
        ]

    sql+=" ORDER BY codigo"

    servicios=query(sql,params if params else None)

    st.write(f"**{len(servicios)} servicio(s)**")

    for s in servicios:

        c1,c2=st.columns([6,1])

        with c1:
            st.markdown(
                f"""
### {s['codigo']}

**{s['descripcion']}**

🏢 {s.get('empresa_nombre') or 'Sin empresa'}

👤 {s.get('emp_nombre','')} {s.get('emp_apellidos','')}

🚛 {s.get('matricula') or '-'}
"""
            )

        with c2:
            if st.button("Abrir",key=f"s{s['id']}"):
                st.session_state["selected_servicio"]=s["id"]
                st.rerun()

        st.divider()


def render():

    if st.session_state.get("selected_servicio"):
        ficha_servicio(
            st.session_state["selected_servicio"]
        )
    else:
        lista_servicios()
