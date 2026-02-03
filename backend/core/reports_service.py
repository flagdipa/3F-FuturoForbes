from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from io import BytesIO
import csv
from datetime import datetime
from decimal import Decimal

class ReportService:
    @staticmethod
    def generate_csv(transactions: list) -> BytesIO:
        from io import StringIO
        output_str = StringIO()
        
        writer = csv.writer(output_str, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        # Headers
        writer.writerow(['Fecha', 'Cuenta', 'Beneficiario', 'Categoría', 'Tipo', 'Monto', 'Notas', 'Estado'])
        
        for t in transactions:
            writer.writerow([
                t["fecha_transaccion"],
                t["cuenta"] or "",
                t["beneficiario"] or "",
                t["categoria"] or "",
                t["codigo_transaccion"],
                f"{t['monto_transaccion']:.2f}".replace('.', ','),
                t["notas"] or "",
                t["estado"] or ""
            ])
            
        output_bytes = BytesIO()
        output_bytes.write(b'\xef\xbb\xbf') # BOM
        output_bytes.write(output_str.getvalue().encode('utf-8'))
        output_bytes.seek(0)
        return output_bytes

    @staticmethod
    def generate_pdf(transactions: list, start_date: str, end_date: str, total_income: Decimal, total_expense: Decimal) -> BytesIO:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        elements = []
        styles = getSampleStyleSheet()

        # Estilo Galáctico
        styles.add(ParagraphStyle(name='GalacticTitle', fontName='Helvetica-Bold', fontSize=24, textColor=colors.HexColor('#00f2ff'), spaceAfter=20, alignment=1)) # Center
        styles.add(ParagraphStyle(name='GalacticSubtitle', fontName='Helvetica', fontSize=12, textColor=colors.HexColor('#7000ff'), spaceAfter=10))
        styles.add(ParagraphStyle(name='GalacticText', fontName='Helvetica', fontSize=10, textColor=colors.black))

        # Título
        elements.append(Paragraph("REPORTE FINANCIERO 3F", styles['GalacticTitle']))
        elements.append(Paragraph(f"Período: {start_date} - {end_date}", styles['GalacticSubtitle']))
        elements.append(Spacer(1, 12))

        # Resumen
        resumen_data = [
            ['Resumen del Período', 'Monto (ARS)'],
            ['Total Ingresos', f"$ {total_income:,.2f}"],
            ['Total Gastos', f"$ {total_expense:,.2f}"],
            ['Balance Neto', f"$ {total_income - total_expense:,.2f}"]
        ]
        
        t_resumen = Table(resumen_data, colWidths=[10*cm, 5*cm])
        t_resumen.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#0f172a')),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.HexColor('#00f2ff')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f1f5f9')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#64748b')),
        ]))
        elements.append(t_resumen)
        elements.append(Spacer(1, 24))

        # Tabla de Transacciones
        elements.append(Paragraph("Detalle de Movimientos (Últimos 100)", styles['GalacticSubtitle']))
        
        table_data = [['Fecha', 'Beneficiario', 'Categoría', 'Monto']]
        for t in transactions[:100]: # Limite PDF para no explotar
            monto_fmt = f"$ {t['monto_transaccion']:,.2f}"
            color = colors.red if t['monto_transaccion'] < 0 else colors.green
            
            table_data.append([
                t["fecha_transaccion"][:10],
                (t["beneficiario"] or "")[:20],
                (t["categoria"] or "")[:15],
                monto_fmt
            ])

        t_trans = Table(table_data, colWidths=[3*cm, 6*cm, 4*cm, 4*cm])
        t_trans.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#050a14')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (3, 0), (-1, -1), 'RIGHT'), # Montos a la derecha
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            # Alternar colores filas
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ]))
        
        elements.append(t_trans)
        
        doc.build(elements)
        buffer.seek(0)
        return buffer

reports_service = ReportService()
