"""
CuentasClaras - Rutas Principales
Landing page, dashboard y perfil de usuario
Autor: Fernando Poblete
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from models import User, Debtor, Debt, DebtHistory
from extensions import db
from sqlalchemy import func
from pdf_generator import generate_all_debtors_pdf
from datetime import datetime, timedelta

# Crear blueprint para rutas principales
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """
    Página de inicio (landing page)
    Muestra información sobre la aplicación
    """
    return render_template('landing.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Dashboard principal del usuario
    Muestra estadísticas y lista de deudores con búsqueda y ordenamiento
    """
    # Obtener parámetros de búsqueda y ordenamiento
    search = request.args.get('search', '').strip()
    sort_by = request.args.get('sort_by', 'name')  # name, debt_asc, debt_desc
    
    # Obtener todos los deudores del usuario actual
    query = Debtor.query.filter_by(user_id=current_user.id)
    
    # Aplicar búsqueda por nombre si existe
    if search:
        query = query.filter(Debtor.name.ilike(f'%{search}%'))
    
    debtors = query.all()
    
    # Ordenar deudores
    if sort_by == 'name_asc':
        debtors.sort(key=lambda d: d.name.lower())
    elif sort_by == 'name_desc':
        debtors.sort(key=lambda d: d.name.lower(), reverse=True)
    elif sort_by == 'debt_asc':
        debtors.sort(key=lambda d: d.total_debt() - d.total_paid())
    elif sort_by == 'debt_desc':
        debtors.sort(key=lambda d: d.total_debt() - d.total_paid(), reverse=True)
    
    # Calcular estadísticas (con todos los deudores, no filtrados)
    all_debtors = Debtor.query.filter_by(user_id=current_user.id).all()
    total_owed = 0
    total_paid = 0
    active_debtors = 0
    
    for debtor in all_debtors:
        debtor_total = debtor.total_debt()
        debtor_paid = debtor.total_paid()
        
        total_owed += debtor_total
        total_paid += debtor_paid
        
        # Contar deudores con deudas activas (no pagadas completamente)
        if debtor_total > debtor_paid:
            active_debtors += 1
    
    # Calcular total pendiente
    total_pending = total_owed - total_paid
    
    return render_template('dashboard.html', 
                         debtors=debtors,
                         total_owed=total_owed,
                         total_paid=total_paid,
                         total_pending=total_pending,
                         active_debtors=active_debtors,
                         search=search,
                         sort_by=sort_by)


@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """
    Perfil del usuario
    Permite configurar moneda preferida
    """
    if request.method == 'POST':
        new_currency = request.form.get('currency')
        
        # Validar moneda
        valid_currencies = ['CLP', 'USD', 'BRL']
        if new_currency in valid_currencies:
            current_user.currency = new_currency
            db.session.commit()
            flash('Moneda actualizada correctamente', 'success')
        else:
            flash('Moneda no válida', 'error')
        
        return redirect(url_for('main.profile'))
    
    return render_template('profile.html')


@main_bp.route('/help')
def help():
    """
    Página de ayuda y documentación
    Guía de uso de la aplicación
    """
    return render_template('help.html')


@main_bp.route('/history')
@login_required
def history():
    """
    Historial general de movimientos del usuario
    Con filtros por deudor, fecha y tipo de acción
    """
    # Obtener parámetros de filtro
    debtor_id = request.args.get('debtor_id', type=int)
    action_type = request.args.get('action_type', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    # Query base: todos los movimientos del usuario a través de sus deudas
    query = DebtHistory.query.join(Debt).join(Debtor).filter(
        Debtor.user_id == current_user.id
    )
    
    # Aplicar filtros
    if debtor_id:
        query = query.filter(Debt.debtor_id == debtor_id)
    
    if action_type:
        query = query.filter(DebtHistory.action_type == action_type)
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(DebtHistory.created_at >= date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            # Agregar 1 día para incluir todo el día seleccionado
            date_to_obj = date_to_obj + timedelta(days=1)
            query = query.filter(DebtHistory.created_at < date_to_obj)
        except ValueError:
            pass
    
    # Ordenar por fecha descendente (más reciente primero)
    movements = query.order_by(DebtHistory.created_at.desc()).all()
    
    # Obtener lista de deudores para el filtro
    debtors = Debtor.query.filter_by(user_id=current_user.id).order_by(Debtor.name).all()
    
    # Tipos de acción disponibles
    action_types = [
        ('created', 'Deuda Creada'),
        ('edited', 'Deuda Editada'),
        ('installment_paid', 'Cuota Pagada'),
        ('marked_paid', 'Marcada como Pagada'),
        ('deleted', 'Deuda Eliminada')
    ]
    
    return render_template('history.html',
                         movements=movements,
                         debtors=debtors,
                         action_types=action_types,
                         selected_debtor=debtor_id,
                         selected_action=action_type,
                         date_from=date_from,
                         date_to=date_to)


@main_bp.route('/export_all_pdf')
@login_required
def export_all_pdf():
    """
    Exportar reporte completo de todos los deudores a PDF
    Genera y descarga PDF con estadísticas y detalle
    """
    # Obtener todos los deudores del usuario actual
    debtors = Debtor.query.filter_by(user_id=current_user.id).all()
    
    # Generar PDF
    pdf_buffer = generate_all_debtors_pdf(debtors, current_user)
    
    # Nombre del archivo con fecha
    from datetime import datetime
    filename = f"reporte_completo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    # Enviar archivo
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )
