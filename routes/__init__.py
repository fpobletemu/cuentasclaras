"""
Inicializador del paquete de rutas
Permite importar blueprints de forma más limpia
Autor: Fernando Poblete
"""

from routes.auth import auth_bp
from routes.main import main_bp
from routes.debtor import debtor_bp
from routes.debt import debt_bp

__all__ = ['auth_bp', 'main_bp', 'debtor_bp', 'debt_bp']
