from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
import io
from app.entities.report import ReportInfoOutDTO


class GetReportFilePdfService:

    def execute(self, report: ReportInfoOutDTO) -> bytes:
        pdf_io = io.BytesIO()
        c = canvas.Canvas(pdf_io, pagesize=A4)
        c.setTitle(f'{report.title} - {datetime.now().strftime("%d/%m/%Y")}')
        width, height = A4

        # Title styling
        title_text = report.title
        title_font = "Helvetica-Bold"
        title_size = 28
        title_color = HexColor('#1B2A41')
        c.setFont(title_font, title_size)
        c.setFillColor(title_color)
        text_width = c.stringWidth(title_text, title_font, title_size)
        c.drawString((width - text_width) / 2, height - 60, title_text)

        y_position = height - 110

        # Section and metrics styling
        section_font = "Helvetica-Bold"
        section_size = 16
        section_color = HexColor('#324A5F')
        metric_name_font = "Helvetica-Bold"
        metric_name_size = 14
        metric_value_font = "Helvetica"
        metric_value_size = 14
        metric_color = HexColor('#000000')
        divider_color = HexColor('#DDDDDD')
        divider_thickness = 0.5

        for section in report.sections:
            # Section title
            c.setFont(section_font, section_size)
            c.setFillColor(section_color)
            c.drawString(50, y_position, section.name)
            y_position -= 24

            for metric in section.metrics:
                # Metric name
                c.setFont(metric_name_font, metric_name_size)
                c.setFillColor(metric_color)
                c.drawString(70, y_position, f"{metric.metric}")
                y_position -= 18

                # Metric value (com quebra de linha)
                c.setFont(metric_value_font, metric_value_size)
                c.setFillColor(metric_color)

                max_text_width = width - 100  # margem lateral (50 de cada lado)
                wrapped_lines = self.wrap_text(
                    str(metric.value),
                    metric_value_font,
                    metric_value_size,
                    max_text_width,
                    c
                )

                for line in wrapped_lines:
                    if y_position < 80:
                        c.showPage()
                        y_position = height - 50
                        c.setFont(metric_value_font, metric_value_size)
                        c.setFillColor(metric_color)

                    c.drawString(90, y_position, line)
                    y_position -= 16

                y_position -= 4  # Espaço extra após valor

                # Check for page break
                if y_position < 80:
                    c.showPage()
                    y_position = height - 50

            # Divider after section
            if y_position >= 80:
                c.setStrokeColor(divider_color)
                c.setLineWidth(divider_thickness)
                c.line(50, y_position, width - 50, y_position)
                y_position -= 30
            else:
                c.showPage()
                y_position = height - 80

        # Created_at footer
        footer_font = "Helvetica-Oblique"
        footer_size = 8
        c.setFont(footer_font, footer_size)
        c.setFillColor(metric_color)
        footer_text = f"Criado em: {report.created_at.strftime('%d/%m/%y às %H:%M')}"
        text_width = c.stringWidth(footer_text, footer_font, footer_size)
        c.drawString((width - text_width) / 2, 40, footer_text)

        # Finalize PDF
        c.showPage()
        c.save()
        pdf_bytes = pdf_io.getvalue()
        return pdf_bytes

    @staticmethod
    def wrap_text(text, font_name, font_size, max_width, canvas_obj):
        lines = []
        words = text.split()
        current_line = ""

        for word in words:
            test_line = f"{current_line} {word}".strip()
            if canvas_obj.stringWidth(test_line, font_name, font_size) <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines
