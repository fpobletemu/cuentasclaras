"""
CuentasClaras - Generador de PDFs
Funciones para exportar reportes de deudas en formato PDF
Autor: Fernando Poblete
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, KeepTogether, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime


def format_date_pdf(date_obj):
    """
    Formatea fecha para PDF sin ceros a la izquierda
    
    Args:
        date_obj: Objeto date o datetime
        
    Returns:
        str: Fecha formateada (ej: 9/1/2026)
    """
    if date_obj:
        return f"{date_obj.day}/{date_obj.month}/{date_obj.year}"
    return ""


def format_datetime_pdf(datetime_obj):
    """
    Formatea fecha y hora para PDF sin ceros a la izquierda
    
    Args:
        datetime_obj: Objeto datetime
        
    Returns:
        str: Fecha y hora formateada (ej: 9/1/2026 8:05:30)
    """
    if datetime_obj:
        hour = datetime_obj.hour
        minute = f"{datetime_obj.minute:02d}"
        second = f"{datetime_obj.second:02d}"
        return f"{datetime_obj.day}/{datetime_obj.month}/{datetime_obj.year} {hour}:{minute}:{second}"
    return ""


class NumberedCanvas(canvas.Canvas):
    """
    Canvas personalizado que agrega número de página, fecha/hora y marca de agua
    en cada página del PDF para prevenir falsificaciones
    """
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []
        self.export_timestamp = format_datetime_pdf(datetime.now())
    
    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()
    
    def save(self):
        page_count = len(self.pages)
        for page_num, page in enumerate(self.pages, 1):
            self.__dict__.update(page)
            self.draw_page_elements(page_num, page_count)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)
    
    def draw_page_elements(self, page_num, page_count):
        """
        Dibuja elementos de seguridad en cada página:
        - Timestamp en esquina superior derecha
        - Número de página en footer
        - Marca de agua diagonal en el centro
        """
        page_width, page_height = letter
        
        # Timestamp en esquina superior derecha (pequeño y discreto)
        self.saveState()
        self.setFont('Helvetica', 7)
        self.setFillColor(colors.HexColor('#6b7280'))
        self.drawRightString(page_width - 0.5*inch, page_height - 0.4*inch, 
                            f"Exportado: {self.export_timestamp}")
        self.restoreState()
        
        # Número de página en footer
        self.saveState()
        self.setFont('Helvetica', 9)
        self.setFillColor(colors.HexColor('#9ca3af'))
        self.drawCentredString(page_width / 2, 0.5*inch, 
                              f"Página {page_num} de {page_count}")
        self.restoreState()
        
        # Marca de agua diagonal (muy sutil pero presente)
        self.saveState()
        self.translate(page_width / 2, page_height / 2)
        self.rotate(45)
        self.setFont('Helvetica', 50)
        self.setFillColor(colors.Color(0.9, 0.9, 0.9, alpha=0.3))
        self.drawCentredString(0, 0, "CuentasClaras")
        self.setFont('Helvetica', 12)
        self.drawCentredString(0, -30, self.export_timestamp)
        self.restoreState()


def format_currency_for_pdf(amount, currency):
    """
    Formatea un monto según la moneda del usuario para mostrar en PDF
    
    Args:
        amount (float): Monto a formatear
        currency (str): Código de moneda (CLP, USD, BRL)
    
    Returns:
        str: Monto formateado con símbolo de moneda
    """
    # Redondear a 2 decimales
    amount = round(amount, 2)
    
    # Separar parte entera y decimal
    integer_part = int(amount)
    decimal_part = int((amount - integer_part) * 100)
    
    # Formatear parte entera con separador de miles
    formatted_integer = "{:,}".format(integer_part).replace(",", ".")
    
    # Formato según moneda
    if currency == 'CLP':
        return f"${formatted_integer}"
    elif currency == 'USD':
        return f"${formatted_integer},{decimal_part:02d}"
    elif currency == 'BRL':
        return f"R${formatted_integer},{decimal_part:02d}"
    else:
        return f"${formatted_integer},{decimal_part:02d}"


def generate_debtor_pdf(debtor, debts, current_user):
    """
    Genera un PDF con el detalle de deudas de un deudor específico
    
    Args:
        debtor: Objeto Debtor con información del deudor
        debts: Lista de objetos Debt del deudor
        current_user: Usuario actual para obtener formato de moneda
    
    Returns:
        BytesIO: Buffer con el PDF generado
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Obtener timestamp de exportación
    now = datetime.now()
    export_datetime = f"{now.day}/{now.month}/{now.year} a las {now.hour}:{now.minute:02d}:{now.second:02d}"
    
    # Estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#374151'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Título del documento
    title = Paragraph("CuentasClaras - Reporte de Deudas", title_style)
    elements.append(title)
    
    # Timestamp de exportación prominente
    export_info_style = ParagraphStyle(
        'ExportInfo',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#6b7280'),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    export_info = Paragraph(f"Documento exportado el {export_datetime}", export_info_style)
    elements.append(export_info)
    elements.append(Spacer(1, 0.1*inch))
    
    # Información del deudor
    debtor_info = [
        ['Deudor:', debtor.name],
        ['Teléfono:', debtor.phone or 'No especificado'],
        ['Email:', debtor.email or 'No especificado'],
        ['Fecha:', format_date_pdf(datetime.now())]
    ]
    
    debtor_table = Table(debtor_info, colWidths=[2*inch, 4*inch])
    debtor_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1f2937')),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb'))
    ]))
    
    elements.append(debtor_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Título de la tabla de deudas y tabla juntos
    debts_section = []
    debts_heading = Paragraph("Detalle de Deudas", heading_style)
    debts_section.append(debts_heading)
    debts_section.append(Spacer(1, 0.1*inch))
    
    # Tabla de deudas
    debts_data = [['Monto', 'Fecha Inicial', 'Días', 'Cuotas', 'Archivos', 'Estado']]
    
    total_debt = 0
    total_paid = 0
    
    for debt in debts:
        # Calcular valores
        days = debt.days_elapsed()
        installment_text = '-'
        if debt.has_installments:
            installment_text = f"{debt.installments_paid}/{debt.installments_total}"
        
        status = 'Pagada' if debt.paid else 'Pendiente'
        
        # Contar archivos adjuntos
        attachments_count = debt.count_attachments()
        attachments_text = f"{attachments_count}" if attachments_count > 0 else '-'
        
        # Calcular monto pagado
        if debt.paid:
            paid_amount = debt.amount
        elif debt.has_installments:
            paid_amount = (debt.amount / debt.installments_total) * debt.installments_paid + debt.partial_payment
        else:
            paid_amount = 0
        
        total_debt += debt.amount
        total_paid += paid_amount
        
        # Agregar fila
        debts_data.append([
            format_currency_for_pdf(debt.amount, current_user.currency),
            format_date_pdf(debt.initial_date),
            str(days),
            installment_text,
            attachments_text,
            status
        ])
    
    debts_table = Table(debts_data, colWidths=[1.3*inch, 1.2*inch, 0.7*inch, 0.8*inch, 0.7*inch, 1.1*inch])
    debts_table.setStyle(TableStyle([
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        
        # Body
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#1f2937')),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        
        # Alternating row colors
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
        
        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb'))
    ]))
    
    debts_section.append(debts_table)
    
    # Mantener título y tabla juntos
    elements.append(KeepTogether(debts_section))
    elements.append(Spacer(1, 0.3*inch))
    
    # Totales
    pending = total_debt - total_paid
    
    totals_section = []
    totals_data = [
        ['Total Adeudado:', format_currency_for_pdf(total_debt, current_user.currency)],
        ['Total Pagado:', format_currency_for_pdf(total_paid, current_user.currency)],
        ['Total Pendiente:', format_currency_for_pdf(pending, current_user.currency)]
    ]
    
    totals_table = Table(totals_data, colWidths=[2*inch, 2*inch])
    totals_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
        ('BACKGROUND', (0, 2), (0, 2), colors.HexColor('#3b82f6')),
        ('BACKGROUND', (1, 2), (1, 2), colors.HexColor('#dbeafe')),
        ('TEXTCOLOR', (0, 0), (-1, 1), colors.HexColor('#1f2937')),
        ('TEXTCOLOR', (0, 2), (0, 2), colors.whitesmoke),
        ('TEXTCOLOR', (1, 2), (1, 2), colors.HexColor('#1f2937')),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb'))
    ]))
    
    totals_section.append(totals_table)
    elements.append(KeepTogether(totals_section))
    
    # Nota de autenticidad al final
    elements.append(Spacer(1, 0.3*inch))
    authenticity_style = ParagraphStyle(
        'Authenticity',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#9ca3af'),
        alignment=TA_CENTER,
        leading=10
    )
    authenticity_note = Paragraph(
        f"Este documento fue generado electrónicamente por CuentasClaras el {export_datetime}.<br/>"
        f"Cualquier modificación posterior invalida su autenticidad.",
        authenticity_style
    )
    elements.append(authenticity_note)
    
    # Generar PDF con canvas personalizado
    doc.build(elements, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    
    return buffer


def generate_all_debtors_pdf(debtors, current_user):
    """
    Genera un PDF con el reporte completo de todos los deudores
    
    Args:
        debtors: Lista de objetos Debtor con sus deudas
        current_user: Usuario actual para obtener formato de moneda
    
    Returns:
        BytesIO: Buffer con el PDF generado
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Obtener timestamp de exportación
    now = datetime.now()
    export_datetime = f"{now.day}/{now.month}/{now.year} a las {now.hour}:{now.minute:02d}:{now.second:02d}"
    
    # Estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#374151'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=13,
        textColor=colors.HexColor('#4b5563'),
        spaceAfter=8,
        spaceBefore=8
    )
    
    # Título del documento
    title = Paragraph("CuentasClaras - Reporte General", title_style)
    elements.append(title)
    
    # Timestamp de exportación prominente
    export_info_style = ParagraphStyle(
        'ExportInfo',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#6b7280'),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    export_info = Paragraph(f"Documento exportado el {export_datetime}", export_info_style)
    elements.append(export_info)
    elements.append(Spacer(1, 0.3*inch))
    
    # Calcular totales generales
    grand_total_debt = 0
    grand_total_paid = 0
    active_debtors = 0
    
    for debtor in debtors:
        debtor_total = debtor.total_debt()
        debtor_paid = debtor.total_paid()
        
        grand_total_debt += debtor_total
        grand_total_paid += debtor_paid
        
        if debtor_total > debtor_paid:
            active_debtors += 1
    
    # Resumen general
    summary_section = []
    summary_heading = Paragraph("Resumen General", heading_style)
    summary_section.append(summary_heading)
    summary_section.append(Spacer(1, 0.1*inch))
    
    summary_data = [
        ['Total Deudores:', str(len(debtors))],
        ['Deudores Activos:', str(active_debtors)],
        ['Total Adeudado:', format_currency_for_pdf(grand_total_debt, current_user.currency)],
        ['Total Pagado:', format_currency_for_pdf(grand_total_paid, current_user.currency)],
        ['Total Pendiente:', format_currency_for_pdf(grand_total_debt - grand_total_paid, current_user.currency)]
    ]
    
    summary_table = Table(summary_data, colWidths=[2.5*inch, 2.5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
        ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor('#3b82f6')),
        ('TEXTCOLOR', (0, 0), (-1, 3), colors.HexColor('#1f2937')),
        ('TEXTCOLOR', (0, 4), (-1, 4), colors.whitesmoke),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb'))
    ]))
    
    summary_section.append(summary_table)
    
    # Mantener resumen junto
    elements.append(KeepTogether(summary_section))
    elements.append(Spacer(1, 0.3*inch))
    
    # Detalle por deudor
    detail_heading = Paragraph("Detalle por Deudor", heading_style)
    elements.append(detail_heading)
    elements.append(Spacer(1, 0.1*inch))
    
    for idx, debtor in enumerate(debtors):
        # Crear lista de elementos para este deudor (se mantendrán juntos)
        debtor_elements = []
        
        # Nombre del deudor
        debtor_name = Paragraph(debtor.name, subheading_style)
        debtor_elements.append(debtor_name)
        
        # Obtener deudas del deudor
        from models import Debt
        debts = Debt.query.filter_by(debtor_id=debtor.id).all()
        
        if debts:
            # Tabla de deudas del deudor
            debtor_debts_data = [['Monto', 'Fecha', 'Días', 'Cuotas', 'Archivos', 'Estado']]
            
            debtor_total = 0
            debtor_paid = 0
            
            for debt in debts:
                days = debt.days_elapsed()
                installment_text = '-'
                if debt.has_installments:
                    installment_text = f"{debt.installments_paid}/{debt.installments_total}"
                
                status = 'Pagada' if debt.paid else 'Pendiente'
                
                # Contar archivos adjuntos
                attachments_count = debt.count_attachments()
                attachments_text = f"{attachments_count}" if attachments_count > 0 else '-'
                
                # Calcular monto pagado
                if debt.paid:
                    paid_amount = debt.amount
                elif debt.has_installments:
                    paid_amount = (debt.amount / debt.installments_total) * debt.installments_paid + debt.partial_payment
                else:
                    paid_amount = 0
                
                debtor_total += debt.amount
                debtor_paid += paid_amount
                
                debtor_debts_data.append([
                    format_currency_for_pdf(debt.amount, current_user.currency),
                    format_date_pdf(debt.initial_date),
                    str(days),
                    installment_text,
                    attachments_text,
                    status
                ])
            
            # Agregar fila de totales del deudor
            debtor_pending = debtor_total - debtor_paid
            debtor_debts_data.append([
                f"Total: {format_currency_for_pdf(debtor_total, current_user.currency)}",
                f"Pagado: {format_currency_for_pdf(debtor_paid, current_user.currency)}",
                '',
                '',
                '',
                f"Pendiente: {format_currency_for_pdf(debtor_pending, current_user.currency)}"
            ])
            
            debtor_debts_table = Table(debtor_debts_data, colWidths=[1.1*inch, 1*inch, 0.6*inch, 0.7*inch, 0.6*inch, 1.5*inch])
            debtor_debts_table.setStyle(TableStyle([
                # Header
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6b7280')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                
                # Body
                ('BACKGROUND', (0, 1), (-1, -2), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -2), colors.HexColor('#1f2937')),
                ('ALIGN', (0, 1), (-1, -2), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -2), 9),
                
                # Totals row
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e5e7eb')),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#1f2937')),
                ('ALIGN', (0, -1), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -1), (-1, -1), 9),
                
                # Alternating row colors
                ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f9fafb')]),
                
                # Padding
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                
                # Grid
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db'))
            ]))
            
            debtor_elements.append(debtor_debts_table)
        else:
            no_debts = Paragraph("Sin deudas registradas", styles['Italic'])
            debtor_elements.append(no_debts)
        
        # Mantener todos los elementos del deudor juntos en la misma página
        elements.append(KeepTogether(debtor_elements))
        
        # Agregar espacio o salto de página entre deudores
        if idx < len(debtors) - 1:
            elements.append(Spacer(1, 0.3*inch))
    
    # Nota de autenticidad al final
    elements.append(Spacer(1, 0.5*inch))
    authenticity_style = ParagraphStyle(
        'Authenticity',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#9ca3af'),
        alignment=TA_CENTER,
        leading=10
    )
    authenticity_note = Paragraph(
        f"Este documento fue generado electrónicamente por CuentasClaras el {export_datetime}.<br/>"
        f"Cualquier modificación posterior invalida su autenticidad.",
        authenticity_style
    )
    elements.append(authenticity_note)
    
    # Generar PDF con canvas personalizado
    doc.build(elements, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    
    return buffer
