import streamlit as st
import json
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
    return max([s["id"] for s in data], default=0) + 1


# ----------------------------
# Ficha Horizontal
# ----------------------------

def mostrar_ficha_servicio(servicio):
    st.markdown("### 📝 Ficha del servicio")
    st.write("---")

    # --- FILA 1 ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📦 Datos del servicio")
        st.markdown(f"**ID:** {servicio['id']}")
        st.markdown(f"**Nombre del servicio:** {servicio['nombre_servicio']}")
        st.markdown(f"**Teléfono:** {servicio['telefono']}")

    with col2:
        st.subheader("🏢 Empresa")
        st.markdown(f"**CIF:** {servicio['cif']}")
        st.markdown(f"**Empresa:** {servicio['nombre_empresa']}")
        st.markdown(f"**Correo:** {servicio['correo']}")

    st.write("---")

    # --- FILA 2 ---
    st.subheader("📍 Dirección del servicio")
    st.info(servicio["direccion"])

    st.write("---")

    # --- FILA 3 ---
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("👤 Persona de contacto")
        st.markdown(f"**Nombre:** {servicio['persona_contacto']}")

    with col4:
        st.subheader("📞 Teléfono de contacto")
        st.markdown(f"**Teléfono:** {servicio['telefono_contacto']}")

    st.write("---")

    # --- FILA 4 ---
    st.subheader("🧾 Notas adicionales")
    st.markdown(servicio["notas"] if servicio["notas"] else "_Sin notas_")

    st.write("---")


# ----------------------------
# Página de Servicios
# ----------------------------

def app():
    st.title("📦 Gestión de Servicios")

    servicios = load_data()

    st.subheader("🔧 Crear / Editar servicio")

    nombres_servicios = ["Nuevo servicio"] + [
        f"{s['id']} - {s['nombre_servicio']}" for s in servicios
    ]
    seleccion = st.selectbox("Seleccionar servicio", nombres_servicios)

    if seleccion != "Nuevo servicio":
        servicio_id = int(seleccion.split(" - ")[0])
        servicio_actual = next((s for s in servicios if s["id"] == servicio_id), None)
        mostrar_ficha_servicio(servicio_actual)
    else:
        servicio_actual = None

    # ----------------------------
    # FORMULARIO
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

    # ----------------------------
    # Acción al guardar
    # ----------------------------

    if submitted:
        if servicio_actual:
            # Editar
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
    # TABLA DE SERVICIOS
    # ----------------------------

    st.subheader("📋 Lista de servicios registrados")
    if servicios:
        st.dataframe(servicios, use_container_width=True)
    else:
        st.info("No hay servicios registrados todavía.")


# Necesario para multipage en Streamlit
if __name__ == "__main__":
    app()


