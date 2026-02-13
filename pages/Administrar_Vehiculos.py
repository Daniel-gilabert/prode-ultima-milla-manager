import streamlit as st
import pandas as pd
import psycopg2

def get_connection():
    return psycopg2.connect(st.secrets["DATABASE_URL"])

st.title("📥 Importar Vehículos desde Excel")

archivo = st.file_uploader("Sube el Excel de vehículos", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)

    # Limpieza básica
    df["matricula"] = df["matricula"].astype(str).str.strip()

    conn = get_connection()
    cursor = conn.cursor()

    inserted = 0
    updated = 0

    for _, row in df.iterrows():
        cursor.execute("""
        INSERT INTO vehiculos (
            id_vehiculo, matricula, bastidor, marca, modelo,
            tipo, itv_vigente_hasta, seguro_vigente_hasta,
            aseguradora, poliza
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
            row.get("itv_vigente_hasta"),
            row.get("seguro_vigente_hasta"),
            row.get("aseguradora"),
            row.get("poliza")
        ))

    conn.commit()
    cursor.close()
    conn.close()

    st.success("Importación completada 🚀")
