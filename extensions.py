"""
CuentasClaras - Extensiones de Flask
Inicialización de extensiones reutilizables
Autor: Fernando Poblete
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Inicializar extensiones sin vincularlas a la app
# Esto permite reutilizarlas en diferentes contextos (tests, múltiples apps)
db = SQLAlchemy()
login_manager = LoginManager()


def init_extensions(app):
    """
    Inicializa todas las extensiones con la aplicación Flask
    
    Args:
        app: Instancia de Flask
    """
    # Configurar SQLAlchemy
    db.init_app(app)
    
    # Configurar Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Ruta para login
    login_manager.login_message = None  # Desactivar mensaje por defecto
    
    # Registrar el loader de usuarios
    from models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        """Carga el usuario desde la base de datos por su ID"""
        return User.query.get(int(user_id))
