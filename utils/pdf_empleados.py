from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from pathlib import Path

COLOR_PRODE = HexColor("#00587A")

def generar_pdf_empleados(empleados, fotos_dir, salida):
    c = canvas.Canvas(str(salida), pagesize=A4)
    width, height = A4

    for emp in empleados:
        y = height - 2*cm

        # CABECERA
        c.setFont("Helvetica-Bold", 18)
        c.setFillColor(COLOR_PRODE)
        c.drawString(2*cm, y, "PRODE · Ficha de Empleado")
        y -= 1.2*cm

        # FOTO
        foto = (
            fotos_dir / f"{emp['id_empleado']}.jpg"
        )
        if foto.exists():
            c.drawImage(
                ImageReader(str(foto)),
                2*cm, y-4*cm,
                width=4*cm, height=4*cm,
                preserveAspectRatio=True
            )

        # DATOS
        x = 7*cm
        c.setFont("Helvetica-Bold", 14)
        c.drawString(x, y, emp["nombre"])
        y -= 0.8*cm

        c.setFont("Helvetica", 11)
        datos = [
            ("🆔 ID", emp["id_empleado"]),
            ("🪪 DNI", emp["dni"]),
            ("✉ Email", emp["email"]),
            ("📞 Teléfono", emp["telefono"]),
            ("💼 Puesto", emp["puesto"]),
            ("📍 Ubicación", emp["ubicacion"]),
            ("✅ Estado", emp["estado"]),
        ]

        for label, valor in datos:
            c.drawString(x, y, f"{label}: {valor}")
            y -= 0.6*cm

        c.showPage()

    c.save()
