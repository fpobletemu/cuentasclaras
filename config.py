"""
CuentasClaras - Configuración de la aplicación
Autor: Fernando Poblete
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno desde archivo .env
load_dotenv()


class Config:
    """Configuración base de la aplicación"""
    
    # Clave secreta para sesiones y CSRF
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Configuración de base de datos
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///cuentasclaras.db')
    
    # Ajuste para compatibilidad con Render.com (postgres:// -> postgresql://)
    if SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
    
    # Desactivar tracking de modificaciones (mejora performance)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de uploads
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB máximo por archivo
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}  # Solo imágenes y PDF
    
    # Configuración del servidor
    PORT = int(os.environ.get('PORT', 5001))
    DEBUG = os.environ.get('FLASK_ENV') != 'production'


class DevelopmentConfig(Config):
    """Configuración para desarrollo local"""
    DEBUG = True
    SQLALCHEMY_ECHO = True  # Mostrar queries SQL en consola


class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    SQLALCHEMY_ECHO = False


# Diccionario de configuraciones disponibles
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
