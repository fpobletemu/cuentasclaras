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
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(debtor_bp)
    app.register_blueprint(debt_bp)
    
    # Crear tablas en la base de datos si no existen
    with app.app_context():
        from extensions import db
        db.create_all()
    
    return app


# Punto de entrada para servidores WSGI (Gunicorn, uWSGI, etc.)
app = create_app()

if __name__ == '__main__':
    app.run()
