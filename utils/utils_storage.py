"""utils_storage.py — Subida de fotos a Supabase Storage."""
import streamlit as st
import requests


def get_supabase_headers():
    return {
        "apikey": st.secrets["SUPABASE_KEY"],
        "Authorization": f"Bearer {st.secrets['SUPABASE_KEY']}",
        "Content-Type": "application/octet-stream",
    }


def subir_foto(archivo, bucket: str, nombre_archivo: str):
    url_base = st.secrets["SUPABASE_URL"]
    endpoint = f"{url_base}/storage/v1/object/{bucket}/{nombre_archivo}"
    headers  = get_supabase_headers()
    headers["x-upsert"] = "true"
    data = archivo.read()
    r = requests.post(endpoint, headers=headers, data=data)
    if r.status_code in (200, 201):
        return f"{url_base}/storage/v1/object/public/{bucket}/{nombre_archivo}"
    else:
        st.error(f"Error al subir foto: {r.status_code} — {r.text}")
        return None


def eliminar_foto(bucket: str, nombre_archivo: str) -> bool:
    url_base = st.secrets["SUPABASE_URL"]
    endpoint = f"{url_base}/storage/v1/object/{bucket}/{nombre_archivo}"
    r = requests.delete(endpoint, headers=get_supabase_headers())
    return r.status_code in (200, 204)
