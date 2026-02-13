import streamlit as st
import pandas as pd
import psycopg2

# ---------------------------------------
# CONEXIÓN A SUPABASE
# ---------------------------------------

def get_connection():
    return psycopg2.connect(st.secrets["DATABASE_URL"])

# ---------------------------------------
# INTERFAZ
# ---------------------------------------

st.title("📥 Importar Vehículos desde Excel")

archivo = st.file_uploader("Sube el Excel de vehículos", type=["xlsx"])

if archivo:

    try:
        df = pd.read_excel(archivo)

        # ---------------------------
        # LIMPIEZA DE DATOS
        # ---------------------------

        df["matricula"] = df["maticula"] = df["matricula"].astype(str).str.strip()

        # Convertir fechas correctamente
        df["itv_vigente_hasta"] = pd.to_datetime(
            df.get("itv_vigente_hasta"), errors="coerce"
        )

        df["seguro_vigente_hasta"] = pd.to_datetime(
            df.get("seguro_vigente_hasta"), errors="coerce"
        )

        conn = get_connection()
        cursor = conn.cursor()

        for _, row in df.iterrows():

            itv_fecha = (
                row["itv_vigente_hasta"].date()
                if pd.notnull(row["itv_vigente_hasta"])
                else None
            )

            seguro_fecha = (
                row["seguro_vigente_hasta"].date()
                if pd.notnull(row["seguro_vigente_hasta"])
                else None
            )

            cursor.execute("""
                INSERT INTO vehiculos (
                    id_vehiculo,
                    matricula,
                    bastidor,
                    marca,
                    modelo,
                    tipo,
                    itv_vigente_hasta,
                    seguro_vigente_hasta,
                    aseguradora,
                    poliza
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (matricula)
                DO UPDATE SET
                    bastidor = EXCLUDED.bastidor,
                    marca = EXCLUDED.marca,
                    modelo = EXCLUDED.modelo,
                    tipo = EXCLUDED.tipo,
                    itv_vigente_hasta = EXCLUDED.itv_vigente_hasta,
                    seguro_vigente_hasta = EXCLUDED.seguro_vigente_hasta,
                    aseguradora = EXCLUDED.aseguradora,
                    poliza = EXCLUDED.poliza;
            """, (
                row.get("id_vehiculo"),
                row.get("matricula"),
                row.get("bastidor"),
                row.get("marca"),
                row.get("modelo"),
                row.get("tipo"),
                itv_fecha,
                seguro_fecha,
                row.get("aseguradora"),
                row.get("poliza")
            ))

        conn.commit()
        cursor.close()
        conn.close()

        st.success("✅ Importación completada correctamente 🚀")

    except Exception as e:
        st.error(f"❌ Error durante la importación: {e}")

