import streamlit as st
import pandas as pd
import psycopg2
from datetime import date

def get_connection():
    return psycopg2.connect(st.secrets["DATABASE_URL"])

st.title("🚗 Ficha de Vehículos")

# ==========================
# CARGAR VEHÍCULOS
# ==========================
try:
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM vehiculos ORDER BY matricula", conn)
    conn.close()
except Exception as e:
    st.error(f"Error cargando vehículos: {e}")
    st.stop()

if df.empty:
    st.warning("No hay vehículos cargados en el sistema.")
    st.stop()

# ==========================
# BOTONES SUPERIORES
# ==========================
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("➕ Añadir nuevo vehículo"):
        st.session_state["modo"] = "nuevo"

with col_btn2:
    if st.button("✏ Editar vehículo"):
        st.session_state["modo"] = "editar"

# ==========================
# SELECCIÓN VEHÍCULO
# ==========================
if "vehiculo_index" not in st.session_state:
    st.session_state["vehiculo_index"] = 0

vehiculo_sel = st.selectbox(
    "Selecciona un vehículo",
    df["matricula"].tolist(),
    index=st.session_state["vehiculo_index"]
)

veh = df[df["matricula"] == vehiculo_sel].iloc[0]

st.markdown("---")

# ==========================
# MODO NUEVO
# ==========================
if st.session_state.get("modo") == "nuevo":

    st.subheader("➕ Nuevo vehículo")

    with st.form("form_nuevo"):
        id_vehiculo = st.text_input("ID Vehículo")
        matricula = st.text_input("Matrícula")
        bastidor = st.text_input("Bastidor")
        marca = st.text_input("Marca")
        modelo = st.text_input("Modelo")
        tipo = st.text_input("Tipo")

        itv = st.date_input("ITV vigente hasta", value=None)
        seguro = st.date_input("Seguro vigente hasta", value=None)

        aseguradora = st.text_input("Aseguradora")
        poliza = st.text_input("Póliza")

        col_save, col_cancel = st.columns(2)
        guardar = col_save.form_submit_button("Guardar vehículo")
        cancelar = col_cancel.form_submit_button("Cancelar")

    if cancelar:
        st.session_state["modo"] = None
        st.session_state["vehiculo_index"] = 0
        st.rerun()

    if guardar:
        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO vehiculos (
                    id_vehiculo, matricula, bastidor, marca, modelo, tipo,
                    itv_vigente_hasta, seguro_vigente_hasta,
                    aseguradora, poliza
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                id_vehiculo, matricula, bastidor, marca, modelo, tipo,
                itv if itv else None,
                seguro if seguro else None,
                aseguradora, poliza
            ))

            conn.commit()
            conn.close()

            st.success("Vehículo añadido correctamente ✅")
            st.session_state["modo"] = None
            st.session_state["vehiculo_index"] = 0
            st.rerun()

        except Exception as e:
            st.error(f"Error insertando vehículo: {e}")

# ==========================
# MODO EDITAR
# ==========================
elif st.session_state.get("modo") == "editar":

    st.subheader("✏ Editar vehículo")

    with st.form("form_editar"):
        id_vehiculo = st.text_input("ID Vehículo", veh["id_vehiculo"])
        matricula = st.text_input("Matrícula", veh["matricula"])
        bastidor = st.text_input("Bastidor", veh["bastidor"])
        marca = st.text_input("Marca", veh["marca"])
        modelo = st.text_input("Modelo", veh["modelo"])
        tipo = st.text_input("Tipo", veh["tipo"])

        itv = st.date_input(
            "ITV vigente hasta",
            veh["itv_vigente_hasta"] if pd.notna(veh["itv_vigente_hasta"]) else None
        )

        seguro = st.date_input(
            "Seguro vigente hasta",
            veh["seguro_vigente_hasta"] if pd.notna(veh["seguro_vigente_hasta"]) else None
        )

        aseguradora = st.text_input("Aseguradora", veh["aseguradora"])
        poliza = st.text_input("Póliza", veh["poliza"])

        col_save, col_cancel = st.columns(2)
        guardar = col_save.form_submit_button("Guardar cambios")
        cancelar = col_cancel.form_submit_button("Cancelar")

    if cancelar:
        st.session_state["modo"] = None
        st.session_state["vehiculo_index"] = 0
        st.rerun()

    if guardar:
        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute("""
                UPDATE vehiculos SET
                    id_vehiculo=%s,
                    bastidor=%s,
                    marca=%s,
                    modelo=%s,
                    tipo=%s,
                    itv_vigente_hasta=%s,
                    seguro_vigente_hasta=%s,
                    aseguradora=%s,
                    poliza=%s
                WHERE matricula=%s
            """, (
                id_vehiculo,
                bastidor,
                marca,
                modelo,
                tipo,
                itv if itv else None,
                seguro if seguro else None,
                aseguradora,
                poliza,
                vehiculo_sel
            ))

            conn.commit()
            conn.close()

            st.success("Vehículo actualizado correctamente ✅")
            st.session_state["modo"] = None
            st.session_state["vehiculo_index"] = 0
            st.rerun()

        except Exception as e:
            st.error(f"Error actualizando vehículo: {e}")

# ==========================
# VISTA NORMAL
# ==========================
else:

    st.subheader("📋 Información del vehículo")

    col1, col2 = st.columns(2)

    with col1:
        st.write("Matrícula:", veh["matricula"])
        st.write("Marca:", veh["marca"])
        st.write("Modelo:", veh["modelo"])
        st.write("Tipo:", veh["tipo"])
        st.write("Bastidor:", veh["bastidor"])

    with col2:
        st.write("ITV vigente hasta:", veh["itv_vigente_hasta"])
        st.write("Seguro vigente hasta:", veh["seguro_vigente_hasta"])
        st.write("Aseguradora:", veh["aseguradora"])
        st.write("Póliza:", veh["poliza"])



