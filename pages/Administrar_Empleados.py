import streamlit as st
import pandas as pd
import json
from pathlib import Path
import uuid

st.title("🛠️ Administrar Empleados")

# -----------------------------------------
# RUTAS
# -----------------------------------------
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

EMP_FILE = DATA_DIR / "empleados.json"

# -----------------------------------------
# FUNCIONES DE CARGA / GUARDADO
# -----------------------------------------
def load_empleados():
    if EMP_FILE.exists():
        try:
            return json.loads(EMP_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []

def save_empleados(empleados):
    EMP_FILE.write_text(
        json.dumps(empleados, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

# -----------------------------------------
# ESTADO ACTUAL
# -----------------------------------------
empleados = load_empleados()
hay_empleados = len(empleados) > 0

# -----------------------------------------
# INFO INICIAL
# -----------------------------------------
if hay_empleados:
    st.success(f"✅ Hay {len(empleados)} empleados guardados en el sistema.")
    st.info(
        "⚠️ Los empleados **NO se borran ni se recargan automáticamente**.\n\n"
        "Solo cambiarán si subes un nuevo Excel y confirmas que quieres sobrescribir."
    )
else:
    st.warning("⚠️ No hay empleados cargados todavía.")

st.markdown("---")

# -----------------------------------------
# SUBIR EXCEL
# -----------------------------------------
st.subheader("📤 Cargar empleados desde Excel")

archivo = st.file_uploader(
    "Sube el Excel de empleados",
    type=["xlsx"]
)

if archivo:
    try:
        df = pd.read_excel(archivo, dtype=str).fillna("")

        # Normalizar columnas
        df.columns = (
            df.columns.str.lower()
            .str.strip()
            .str.replace(" ", "_")
            .str.replace("á", "a")
            .str.replace("é", "e")
            .str.replace("í", "i")
            .str.replace("ó", "o")
            .str.replace("ú", "u")
        )

        st.success("✅ Excel leído correctamente")
        st.dataframe(df, use_container_width=True)

        st.markdown("---")

        # -----------------------------------------
        # BOTONES DE GUARDADO
        # -----------------------------------------
        if not hay_empleados:
            if st.button("💾 Guardar empleados en el sistema"):
                nuevos = []

                for _, row in df.iterrows():
                    emp = row.to_dict()
                    emp["id"] = str(uuid.uuid4())
                    nuevos.append(emp)

                save_empleados(nuevos)
                st.success("✅ Empleados guardados correctamente.")
                st.rerun()

        else:
            st.error("⚠️ Ya existen empleados en el sistema.")

            if st.checkbox("☠️ Confirmo que quiero SOBRESCRIBIR todos los empleados"):
                if st.button("💾 Sobrescribir empleados"):
                    nuevos = []

                    for _, row in df.iterrows():
                        emp = row.to_dict()
                        emp["id"] = str(uuid.uuid4())
                        nuevos.append(emp)

                    save_empleados(nuevos)
                    st.success("✅ Empleados sobrescritos correctamente.")
                    st.rerun()

    except Exception as e:
        st.error("❌ Error al leer el Excel")
        st.exception(e)

st.markdown("---")

# -----------------------------------------
# LISTADO ACTUAL (CONTROL)
# -----------------------------------------
st.subheader("👥 Empleados actualmente guardados")

if empleados:
    df_actual = pd.DataFrame(empleados)
    st.dataframe(df_actual, use_container_width=True)
else:
    st.info("No hay empleados guardados todavía.")


