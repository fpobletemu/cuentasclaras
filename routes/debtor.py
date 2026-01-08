"""
CuentasClaras - Rutas de Deudores
CRUD completo para gestión de deudores
Autor: Fernando Poblete
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from models import Debtor, Debt
from extensions import db
from pdf_generator import generate_debtor_pdf

# Crear blueprint para rutas de deudores
debtor_bp = Blueprint('debtor', __name__, url_prefix='/debtor')


@debtor_bp.route('/add', methods=['POST'])
@login_required
def add():
    """
    Agregar nuevo deudor
    Crea un deudor asociado al usuario actual
    """
    name = request.form.get('name')
    phone = request.form.get('phone', '')
    email = request.form.get('email', '')
    
    # Validar nombre
    if not name:
        flash('El nombre es obligatorio', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Crear nuevo deudor
    debtor = Debtor(
        user_id=current_user.id,
        name=name,
        phone=phone,
        email=email
    )
    
    db.session.add(debtor)
    db.session.commit()
    
    flash(f'Deudor {name} agregado correctamente', 'success')
    return redirect(url_for('main.dashboard'))


@debtor_bp.route('/<int:debtor_id>')
@login_required
def detail(debtor_id):
    """
    Detalle de un deudor específico
    Muestra todas sus deudas y estadísticas
    """
    # Buscar deudor y verificar propiedad
    debtor = Debtor.query.get_or_404(debtor_id)
    
    if debtor.user_id != current_user.id:
        flash('No tienes permiso para ver este deudor', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Obtener todas las deudas del deudor
    debts = Debt.query.filter_by(debtor_id=debtor_id).all()
    
    # Calcular estadísticas
    total_debt = debtor.total_debt()
    total_paid = debtor.total_paid()
    pending = total_debt - total_paid
    
    return render_template('debtor_detail.html',
                         debtor=debtor,
                         debts=debts,
                         total_debt=total_debt,
                         total_paid=total_paid,
                         pending=pending)


@debtor_bp.route('/<int:debtor_id>/edit', methods=['POST'])
@login_required
def edit(debtor_id):
    """
    Editar información de un deudor
    Actualiza nombre, teléfono y email
    """
    # Buscar deudor y verificar propiedad
    debtor = Debtor.query.get_or_404(debtor_id)
    
    if debtor.user_id != current_user.id:
        flash('No tienes permiso para editar este deudor', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Actualizar datos
    debtor.name = request.form.get('name', debtor.name)
    debtor.phone = request.form.get('phone', debtor.phone)
    debtor.email = request.form.get('email', debtor.email)
    
    db.session.commit()
    
    flash('Deudor actualizado correctamente', 'success')
    return redirect(url_for('debtor.detail', debtor_id=debtor_id))


@debtor_bp.route('/<int:debtor_id>/delete', methods=['POST'])
@login_required
def delete(debtor_id):
    """
    Eliminar un deudor y todas sus deudas
    Operación irreversible
    """
    # Buscar deudor y verificar propiedad
    debtor = Debtor.query.get_or_404(debtor_id)
    
    if debtor.user_id != current_user.id:
        flash('No tienes permiso para eliminar este deudor', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Eliminar todas las deudas asociadas
    Debt.query.filter_by(debtor_id=debtor_id).delete()
    
    # Eliminar deudor
    db.session.delete(debtor)
    db.session.commit()
    
    flash('Deudor eliminado correctamente', 'success')
    return redirect(url_for('main.dashboard'))


@debtor_bp.route('/<int:debtor_id>/export_pdf')
@login_required
def export_pdf(debtor_id):
    """
    Exportar deudas de un deudor a PDF
    Genera y descarga PDF con detalle completo
    """
    # Buscar deudor y verificar propiedad
    debtor = Debtor.query.get_or_404(debtor_id)
    
    if debtor.user_id != current_user.id:
        flash('No tienes permiso para exportar este deudor', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Obtener todas las deudas del deudor
    debts = Debt.query.filter_by(debtor_id=debtor_id).all()
    
    # Generar PDF
    pdf_buffer = generate_debtor_pdf(debtor, debts, current_user)
    
    # Nombre del archivo
    filename = f"deudas_{debtor.name.replace(' ', '_')}.pdf"
    
    # Enviar archivo
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )
