"""
CuentasClaras - Application Factory
Aplicación Flask para gestión de deudas personales
Autor: Fernando Poblete
"""

from flask import Flask
from config import config
from extensions import init_extensions
from models import User, Debtor, Debt
import os


def create_app(config_name='default'):
    """
    Factory para crear la aplicación Flask
    
    Args:
        config_name (str): Nombre de la configuración a usar ('development', 'production', 'default')
    
    Returns:
        Flask: Instancia de la aplicación configurada
    """
    # Crear instancia de Flask
    app = Flask(__name__)
    
    # Cargar configuración
    app.config.from_object(config[config_name])
    
    # Crear directorio de uploads si no existe
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Inicializar extensiones (db, login_manager)
    init_extensions(app)
    
    # Importar y registrar blueprints
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.debtor import debtor_bp
    from routes.debt import debt_bp
    from routes.admin import admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(debtor_bp)
    app.register_blueprint(debt_bp)
    app.register_blueprint(admin_bp)
    
    # Registrar filtros personalizados de Jinja2
    @app.template_filter('format_date')
    def format_date_filter(date_obj):
        """Formatea fecha sin ceros a la izquierda (ej: 9/1/2026)"""
        if date_obj:
            return f"{date_obj.day}/{date_obj.month}/{date_obj.year}"
        return ""
    
    @app.template_filter('format_datetime')
    def format_datetime_filter(datetime_obj):
        """Formatea fecha y hora sin ceros a la izquierda (ej: 9/1/2026 8:05)"""
        if datetime_obj:
            hour = datetime_obj.hour
            minute = f"{datetime_obj.minute:02d}"  # Minutos sí llevan 0 (ej: 8:05)
            return f"{datetime_obj.day}/{datetime_obj.month}/{datetime_obj.year} {hour}:{minute}"
        return ""
    
    @app.template_filter('format_time')
    def format_time_filter(datetime_obj):
        """Formatea solo hora sin ceros a la izquierda (ej: 8:05)"""
        if datetime_obj:
            hour = datetime_obj.hour
            minute = f"{datetime_obj.minute:02d}"
            return f"{hour}:{minute}"
        return ""
    
    # Crear tablas en la base de datos si no existen
    with app.app_context():
        from extensions import db
        db.create_all()
        
        # Crear usuario admin por defecto si no existe
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@cuentasclaras.com',
                is_admin=True
            )
            admin_user.set_password('admin')
            db.session.add(admin_user)
            db.session.commit()
            print("✅ Usuario admin creado por defecto (username: admin, password: admin)")
    
    return app


# Punto de entrada para servidores WSGI (Gunicorn, uWSGI, etc.)
app = create_app()

if __name__ == '__main__':
    app.run()
