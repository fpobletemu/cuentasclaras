"""
CuentasClaras - Rutas de Deudas
Operaciones sobre deudas individuales
Autor: Fernando Poblete
"""

from flask import Blueprint, request, redirect, url_for, flash, send_from_directory, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import Debtor, Debt, DebtHistory
import json
from extensions import db
from datetime import datetime
import os
import json

# Crear blueprint para rutas de deudas
debt_bp = Blueprint('debt', __name__, url_prefix='/debt')


def log_debt_change(debt_id, action_type, description):
    """
    Registra un cambio en el historial de la deuda
    
    Args:
        debt_id: ID de la deuda
        action_type: Tipo de acción (created, edited, installment_paid, marked_paid, deleted)
        description: Descripción del cambio
    """
    history = DebtHistory(
        debt_id=debt_id,
        user_id=current_user.id,
        action_type=action_type,
        description=description
    )
    db.session.add(history)


def allowed_file(filename):
    """Verifica si el archivo tiene una extensión permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def save_attachments(files, user_id, debt_id, attachment_type='debt'):
    """
    Guarda archivos adjuntos y retorna lista de nombres
    
    Args:
        files: Lista de archivos desde request.files
        user_id: ID del usuario
        debt_id: ID de la deuda
        attachment_type: 'debt' o 'payment'
    
    Returns:
        list: Lista de nombres de archivos guardados
    """
    saved_files = []
    
    if not files:
        return saved_files
    
    # Crear directorio si no existe
    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], str(user_id), str(debt_id))
    os.makedirs(upload_path, exist_ok=True)
    
    for file in files:
        if file and file.filename and allowed_file(file.filename):
            # Crear nombre seguro con timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            original_filename = secure_filename(file.filename)
            filename = f"{attachment_type}_{timestamp}_{original_filename}"
            
            # Guardar archivo
            file.save(os.path.join(upload_path, filename))
            saved_files.append(filename)
    
    return saved_files


@debt_bp.route('/add', methods=['POST'])
@login_required
def add():
    """
    Agregar nueva deuda a un deudor
    Soporta deudas simples o con cuotas y archivos adjuntos
    """
    debtor_id = request.form.get('debtor_id', type=int)
    amount = request.form.get('amount', type=float)
    initial_date = request.form.get('initial_date')
    has_installments = request.form.get('has_installments') in ['true', 'on', True]
    installments_total = request.form.get('installments_total', type=int, default=0)
    notes = request.form.get('notes', '')
    
    # Verificar que el deudor existe y pertenece al usuario
    debtor = Debtor.query.get_or_404(debtor_id)
    if debtor.user_id != current_user.id:
        flash('No tienes permiso para agregar deudas a este deudor', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Validar monto
    if not amount or amount <= 0:
        flash('El monto debe ser mayor a cero', 'error')
        return redirect(url_for('debtor.detail', debtor_id=debtor_id))
    
    # Convertir fecha
    try:
        date_obj = datetime.strptime(initial_date, '%Y-%m-%d')
    except ValueError:
        flash('Fecha inválida', 'error')
        return redirect(url_for('debtor.detail', debtor_id=debtor_id))
    
    # Validar cuotas
    if has_installments and (not installments_total or installments_total <= 0):
        flash('El número de cuotas debe ser mayor a cero', 'error')
        return redirect(url_for('debtor.detail', debtor_id=debtor_id))
    
    # Crear nueva deuda
    debt = Debt(
        debtor_id=debtor_id,
        amount=amount,
        initial_date=date_obj,
        has_installments=has_installments,
        installments_total=installments_total if has_installments else 0,
        installments_paid=0,
        paid=False,
        notes=notes
    )
    
    db.session.add(debt)
    db.session.flush()  # Para obtener el debt.id
    
    # Procesar archivos adjuntos
    if 'debt_files' in request.files:
        files = request.files.getlist('debt_files')
        saved_files = save_attachments(files, current_user.id, debt.id, 'debt')
        if saved_files:
            debt.debt_attachments = json.dumps(saved_files)
    
    # Registrar en historial
    log_debt_change(
        debt.id, 
        'created', 
        f'Deuda creada por {current_user.format_currency(amount)}' + 
        (f' en {installments_total} cuotas' if has_installments else '')
    )
    
    db.session.commit()
    
    flash('Deuda agregada correctamente', 'success')
    return redirect(url_for('debtor.detail', debtor_id=debtor_id))


@debt_bp.route('/<int:debt_id>/pay_installment', methods=['POST'])
@login_required
def pay_installment(debt_id):
    """
    Pagar una cuota de una deuda
    Incrementa el contador de cuotas pagadas
    """
    # Buscar deuda
    debt = Debt.query.get_or_404(debt_id)
    
    # Verificar propiedad a través del deudor
    if debt.debtor.user_id != current_user.id:
        flash('No tienes permiso para modificar esta deuda', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Verificar que tenga cuotas
    if not debt.has_installments:
        flash('Esta deuda no tiene cuotas', 'error')
        return redirect(url_for('debtor.detail', debtor_id=debt.debtor_id))
    
    # Verificar que no se excedan las cuotas
    if debt.installments_paid >= debt.installments_total:
        flash('Ya se pagaron todas las cuotas', 'error')
        return redirect(url_for('debtor.detail', debtor_id=debt.debtor_id))
    
    # Incrementar cuotas pagadas
    debt.installments_paid += 1
    
    # Marcar como pagada si se completaron todas las cuotas
    if debt.installments_paid >= debt.installments_total:
        debt.paid = True
        log_debt_change(
            debt.id,
            'marked_paid',
            f'Deuda completamente pagada (todas las cuotas pagadas)'
        )
        flash('¡Deuda completamente pagada!', 'success')
    else:
        log_debt_change(
            debt.id,
            'installment_paid',
            f'Cuota {debt.installments_paid}/{debt.installments_total} pagada'
        )
        flash(f'Cuota pagada. Progreso: {debt.installments_paid}/{debt.installments_total}', 'success')
    
    db.session.commit()
    return redirect(url_for('debtor.detail', debtor_id=debt.debtor_id))


@debt_bp.route('/<int:debt_id>/mark_paid', methods=['POST'])
@login_required
def mark_paid(debt_id):
    """
    Marcar una deuda como pagada completamente
    Para deudas sin cuotas o pago total anticipado
    Opcionalmente acepta archivos de evidencia de pago
    """
    # Buscar deuda
    debt = Debt.query.get_or_404(debt_id)
    
    # Verificar propiedad a través del deudor
    if debt.debtor.user_id != current_user.id:
        flash('No tienes permiso para modificar esta deuda', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Marcar como pagada
    debt.paid = True
    
    # Si tiene cuotas, marcar todas como pagadas
    if debt.has_installments:
        debt.installments_paid = debt.installments_total
    
    # Procesar archivos adjuntos de evidencia si hay
    if 'payment_files' in request.files:
        files = request.files.getlist('payment_files')
        if files and files[0].filename:  # Verificar que hay archivos
            new_attachments = save_attachments(files, current_user.id, debt_id, 'payment')
            if new_attachments:
                # Obtener adjuntos existentes
                existing = debt.get_payment_attachments()
                # Agregar nuevos
                existing.extend(new_attachments)
                # Guardar como JSON
                debt.payment_attachments = json.dumps(existing)
    
    # Registrar en historial
    log_debt_change(
        debt.id,
        'marked_paid',
        'Deuda marcada como pagada'
    )
    
    db.session.commit()
    flash('Deuda marcada como pagada correctamente', 'success')
    return redirect(url_for('debtor.detail', debtor_id=debt.debtor_id))


@debt_bp.route('/<int:debt_id>/delete', methods=['POST'])
@login_required
def delete(debt_id):
    """
    Eliminar una deuda
    Operación irreversible
    """
    # Buscar deuda
    debt = Debt.query.get_or_404(debt_id)
    
    # Verificar propiedad a través del deudor
    if debt.debtor.user_id != current_user.id:
        flash('No tienes permiso para eliminar esta deuda', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Guardar información antes de eliminar
    debtor_id = debt.debtor_id
    amount = debt.amount
    
    # Registrar eliminación en historial (antes de eliminar)
    log_debt_change(
        debt.id,
        'deleted',
        f'Deuda de {current_user.format_currency(amount)} eliminada'
    )
    db.session.commit()
    
    # Eliminar archivos adjuntos físicos
    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], str(current_user.id), str(debt_id))
    if os.path.exists(upload_path):
        import shutil
        shutil.rmtree(upload_path)
    
    # Eliminar deuda (cascade eliminará el historial automáticamente)
    db.session.delete(debt)
    db.session.commit()
    
    flash('Deuda eliminada correctamente', 'success')
    return redirect(url_for('debtor.detail', debtor_id=debtor_id))


@debt_bp.route('/<int:debt_id>/add_payment_evidence', methods=['POST'])
@login_required
def add_payment_evidence(debt_id):
    """
    Agregar evidencia de pago a una deuda
    """
    # Buscar deuda
    debt = Debt.query.get_or_404(debt_id)
    
    # Verificar propiedad
    if debt.debtor.user_id != current_user.id:
        flash('No tienes permiso para modificar esta deuda', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Procesar archivos
    if 'payment_files' in request.files:
        files = request.files.getlist('payment_files')
        saved_files = save_attachments(files, current_user.id, debt.id, 'payment')
        
        if saved_files:
            # Agregar a los existentes
            existing = debt.get_payment_attachments()
            existing.extend(saved_files)
            debt.payment_attachments = json.dumps(existing)
            
            db.session.commit()
            flash(f'Se agregaron {len(saved_files)} archivo(s) de evidencia de pago', 'success')
        else:
            flash('No se pudieron cargar los archivos. Verifica el formato.', 'error')
    else:
        flash('No se seleccionaron archivos', 'error')
    
    return redirect(url_for('debtor.detail', debtor_id=debt.debtor_id))


@debt_bp.route('/<int:debt_id>/download/<filename>')
@login_required
def download_file(debt_id, filename):
    """
    Descargar un archivo adjunto
    """
    # Buscar deuda
    debt = Debt.query.get_or_404(debt_id)
    
    # Verificar propiedad
    if debt.debtor.user_id != current_user.id:
        flash('No tienes permiso para acceder a este archivo', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Verificar que el archivo pertenece a esta deuda
    all_files = debt.get_debt_attachments() + debt.get_payment_attachments()
    if filename not in all_files:
        flash('Archivo no encontrado', 'error')
        return redirect(url_for('debtor.detail', debtor_id=debt.debtor_id))
    
    # Construir ruta del archivo
    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], str(current_user.id), str(debt_id))
    
    return send_from_directory(upload_path, filename, as_attachment=True)


@debt_bp.route('/<int:debt_id>/edit', methods=['POST'])
@login_required
def edit(debt_id):
    """
    Editar una deuda existente
    Permite modificar monto, cuotas, notas y adjuntar nuevos archivos
    """
    # Buscar deuda
    debt = Debt.query.get_or_404(debt_id)
    
    # Verificar propiedad
    if debt.debtor.user_id != current_user.id:
        flash('No tienes permiso para editar esta deuda', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Obtener datos del formulario
    amount = request.form.get('amount', type=float)
    has_installments = request.form.get('has_installments') == 'on'
    installments_total = request.form.get('installments_total', type=int, default=0)
    notes = request.form.get('notes', '')
    
    # Validar monto
    if amount and amount > 0:
        debt.amount = amount
    
    # Actualizar sistema de cuotas
    debt.has_installments = has_installments
    if has_installments and installments_total > 0:
        debt.installments_total = installments_total
        # Si las cuotas pagadas exceden el nuevo total, ajustar
        if debt.installments_paid > installments_total:
            debt.installments_paid = installments_total
        # Si se completaron todas las cuotas, marcar como pagada
        if debt.installments_paid >= debt.installments_total:
            debt.paid = True
    else:
        debt.has_installments = False
        debt.installments_total = 0
        debt.installments_paid = 0
    
    # Actualizar notas
    debt.notes = notes
    
    # Procesar archivos adjuntos si hay
    if 'debt_files' in request.files:
        files = request.files.getlist('debt_files')
        if files and files[0].filename:  # Verificar que hay archivos
            new_attachments = save_attachments(files, current_user.id, debt_id, 'debt')
            if new_attachments:
                # Obtener adjuntos existentes
                existing = debt.get_debt_attachments()
                # Agregar nuevos
                existing.extend(new_attachments)
                # Guardar como JSON
                debt.debt_attachments = json.dumps(existing)
    
    # Registrar en historial
    log_debt_change(
        debt.id,
        'edited',
        'Deuda editada'
    )
    
    db.session.commit()
    
    flash('Deuda actualizada correctamente', 'success')
    return redirect(url_for('debtor.detail', debtor_id=debt.debtor_id))

