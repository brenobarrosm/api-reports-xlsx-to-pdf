from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io
from app.entities.report import ReportInfoOutDTO


class GetReportFilePdfService:
    def __init__(self):
        pass

    def execute(self, report: ReportInfoOutDTO) -> bytes:
        pdf_io = io.BytesIO()
        c = canvas.Canvas(pdf_io, pagesize=A4)

        c.setFont("Helvetica-Bold", 20)
        c.drawString(100, 800, report.title)

        c.setFont("Helvetica", 12)
        y_position = 760
        for metric in report.metrics:
            texto = f"{metric.metric}: {str(metric.value)}"
            c.drawString(100, y_position, texto)
            y_position -= 20

        c.setFont("Helvetica-Oblique", 10)
        c.drawString(100, y_position - 20, f"Criado em: {str(report.created_at)}")

        c.showPage()
        c.save()
        pdf_bytes = pdf_io.getvalue()
        return pdf_bytes
