import streamlit as st
import json
import os
from pathlib import Path

DATA_PATH = Path("data/servicios.json")


# ----------------------------
# Funciones auxiliares
# ----------------------------

def load_data():
    if not DATA_PATH.exists():
        return []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return []


def save_data(data):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def get_next_id(data):
    if not data:
        return 1
    return max(item["id"] for item in data) + 1


# ----------------------------
# Página de Servicios
# ----------------------------

def app():
    st.title("📦 Gestión de Servicios")

    servicios = load_data()

    # Selección de servicio para editar
    st.subheader("🔧 Crear / Editar servicio")

    nombres_servicios = ["Nuevo servicio"] + [f"{s['id']} - {s['nombre_servicio']}" for s in servicios]
    seleccion = st.selectbox("Seleccionar servicio", nombres_servicios)

    if seleccion != "Nuevo servicio":
        servicio_id = int(seleccion.split(" - ")[0])
        servicio_actual = next((s for s in servicios if s["id"] == servicio_id), None)
    else:
        servicio_actual = None

    # ----------------------------
    # FORMULARIO CORRECTO
    # ----------------------------

    with st.form("form_servicio"):
        nombre_servicio = st.text_input(
            "Nombre del servicio",
            value=servicio_actual["nombre_servicio"] if servicio_actual else ""
        )

        cif = st.text_input(
            "CIF",
            value=servicio_actual["cif"] if servicio_actual else ""
        )

        nombre_empresa = st.text_input(
            "Nombre de la empresa",
            value=servicio_actual["nombre_empresa"] if servicio_actual else ""
        )

        direccion = st.text_area(
            "Dirección completa",
            value=servicio_actual["direccion"] if servicio_actual else ""
        )

        telefono = st.text_input(
            "Teléfono del servicio",
            value=servicio_actual["telefono"] if servicio_actual else ""
        )

        correo = st.text_input(
            "Correo del servicio",
            value=servicio_actual["correo"] if servicio_actual else ""
        )

        persona_contacto = st.text_input(
            "Persona de contacto principal",
            value=servicio_actual["persona_contacto"] if servicio_actual else ""
        )

        telefono_contacto = st.text_input(
            "Teléfono persona contacto",
            value=servicio_actual["telefono_contacto"] if servicio_actual else ""
        )

        notas = st.text_area(
            "Notas / información adicional",
            value=servicio_actual["notas"] if servicio_actual else ""
        )

        submitted = st.form_submit_button("💾 Guardar servicio")

    # FIN DEL FORMULARIO
    # -----------------------------------

    if submitted:
        if servicio_actual:
            # Editar existente
            servicio_actual.update({
                "nombre_servicio": nombre_servicio,
                "cif": cif,
                "nombre_empresa": nombre_empresa,
                "direccion": direccion,
                "telefono": telefono,
                "correo": correo,
                "persona_contacto": persona_contacto,
                "telefono_contacto": telefono_contacto,
                "notas": notas
            })
            st.success("Servicio actualizado correctamente ✔️")

        else:
            # Crear nuevo
            nuevo_servicio = {
                "id": get_next_id(servicios),
                "nombre_servicio": nombre_servicio,
                "cif": cif,
                "nombre_empresa": nombre_empresa,
                "direccion": direccion,
                "telefono": telefono,
                "correo": correo,
                "persona_contacto": persona_contacto,
                "telefono_contacto": telefono_contacto,
                "notas": notas
            }
            servicios.append(nuevo_servicio)
            st.success("Servicio creado correctamente ✔️")

        save_data(servicios)

    # ----------------------------
    # Mostrar tabla de servicios
    # ----------------------------
    st.subheader("📋 Lista de servicios registrados")
    if servicios:
        st.dataframe(servicios, use_container_width=True)
    else:
        st.info("No hay servicios registrados todavía.")


# Llamada necesaria para Streamlit multipage
if __name__ == "__main__":
    app()

