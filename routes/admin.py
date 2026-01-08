"""
CuentasClaras - Rutas de Administración
Panel de administración para gestionar usuarios
Autor: Fernando Poblete
"""

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import User
from functools import wraps

# Crear blueprint para rutas de administración
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    """
    Decorador para proteger rutas que requieren privilegios de admin
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Debes iniciar sesión para acceder a esta página', 'error')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_admin:
            flash('No tienes permisos de administrador', 'error')
            return redirect(url_for('main.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/')
@login_required
@admin_required
def panel():
    """
    Panel de administración
    Muestra lista de todos los usuarios registrados
    """
    # Obtener todos los usuarios ordenados por fecha de creación
    users = User.query.order_by(User.created_at.desc()).all()
    
    return render_template('admin.html', users=users)
