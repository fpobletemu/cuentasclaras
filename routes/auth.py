"""
CuentasClaras - Rutas de Autenticación
Manejo de registro, login y logout de usuarios
Autor: Fernando Poblete
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import User
from extensions import db

# Crear blueprint para rutas de autenticación
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Registro de nuevos usuarios
    GET: Muestra formulario de registro
    POST: Procesa el registro y crea el usuario
    """
    # Redirigir si ya está autenticado
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Validar que el username no exista
        if User.query.filter_by(username=username).first():
            flash('El nombre de usuario ya existe', 'error')
            return redirect(url_for('auth.register'))
        
        # Validar que el email no exista
        if User.query.filter_by(email=email).first():
            flash('El email ya está registrado', 'error')
            return redirect(url_for('auth.register'))
        
        # Crear nuevo usuario
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('¡Registro exitoso! Por favor inicia sesión', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Inicio de sesión de usuarios
    GET: Muestra formulario de login
    POST: Autentica al usuario
    """
    # Redirigir si ya está autenticado
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Buscar usuario
        user = User.query.filter_by(username=username).first()
        
        # Verificar credenciales
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        
        flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """
    Cierre de sesión del usuario actual
    """
    logout_user()
    return redirect(url_for('main.index'))
