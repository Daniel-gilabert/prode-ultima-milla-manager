import base64
import streamlit.components.v1 as components

def generar_html_impresion(emp, foto_path):
    foto_html = ""
    if foto_path.exists():
        img_b64 = base64.b64encode(foto_path.read_bytes()).decode()
        foto_html = f"<img src='data:image/jpeg;base64,{img_b64}' width='120'><br><br>"

    return f"""
    <html>
    <head>
        <title>Ficha empleado</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                padding: 40px;
            }}
            h1 {{
                border-bottom: 1px solid #ccc;
                padding-bottom: 5px;
            }}
            .fila {{
                margin: 6px 0;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        {foto_html}
        <h1>{emp['nombre']}</h1>
        <div class="fila"><b>ID:</b> {emp['id_empleado']}</div>
        <div class="fila"><b>DNI:</b> {emp['dni']}</div>
        <div class="fila"><b>Email:</b> {emp['email']}</div>
        <div class="fila"><b>Teléfono:</b> {emp['telefono']}</div>
        <div class="fila"><b>Puesto:</b> {emp['puesto']}</div>
        <div class="fila"><b>Ubicación:</b> {emp['ubicacion']}</div>
        <div class="fila"><b>Estado:</b> {emp['estado']}</div>

        <script>
            window.onload = function() {{
                window.print();
            }}
        </script>
    </body>
    </html>
    """

# -----------------------------------------
# BOTÓN IMPRIMIR (VENTANA NUEVA REAL)
# -----------------------------------------
if st.button("🖨 Imprimir ficha"):
    html = generar_html_impresion(emp, foto_jpg if foto_jpg.exists() else foto_png)
    html_b64 = base64.b64encode(html.encode()).decode()

    components.html(
        f"""
        <script>
            var w = window.open();
            w.document.write(atob("{html_b64}"));
            w.document.close();
        </script>
        """,
        height=0
    )



