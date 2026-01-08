# Convenciones de Código - CuentasClaras

## 📋 Estructura General

### Arquitectura
- **Patrón**: Application Factory con Flask Blueprints
- **Separación**: Config → Extensions → Models → Routes → Views
- **Nomenclatura módulos**: snake_case (config.py, pdf_generator.py)

### Organización de Archivos
```
cuentasclaras/
├── app.py              # Factory principal
├── config.py           # Configuraciones
├── extensions.py       # Extensiones Flask
├── models.py           # Modelos SQLAlchemy
├── pdf_generator.py    # Utilidades PDF
├── routes/             # Blueprints
│   ├── __init__.py
│   ├── auth.py
│   ├── main.py
│   ├── debtor.py
│   └── debt.py
└── templates/          # Plantillas Jinja2
```

## 🐍 Python

### Estilo de Código
- **Estándar**: PEP 8
- **Indentación**: 4 espacios
- **Líneas**: Máximo 100 caracteres (flexible)
- **Imports**: 
  1. Librería estándar
  2. Third-party
  3. Locales

### Nomenclatura

#### Variables y Funciones
```python
# snake_case para variables y funciones
user_id = 123
total_debt = 1000.50

def calculate_total():
    pass

def format_currency_for_pdf(amount, currency):
    pass
```

#### Clases
```python
# PascalCase para clases
class User(UserMixin, db.Model):
    pass

class DebtorManager:
    pass
```

#### Constantes
```python
# UPPER_SNAKE_CASE para constantes
MAX_INSTALLMENTS = 100
DEFAULT_CURRENCY = 'CLP'
```

### Docstrings

#### Módulos
```python
"""
CuentasClaras - Nombre del Módulo
Descripción breve del propósito
Autor: Fernando Poblete
"""
```

#### Funciones
```python
def calculate_amount(price, quantity):
    """
    Calcula el monto total multiplicando precio por cantidad
    
    Args:
        price (float): Precio unitario
        quantity (int): Cantidad de items
    
    Returns:
        float: Monto total calculado
    """
    return price * quantity
```

#### Clases y Métodos
```python
class User(db.Model):
    """
    Modelo de Usuario
    Representa a un usuario registrado en el sistema
    """
    
    def set_password(self, password):
        """
        Genera y almacena el hash de la contraseña
        
        Args:
            password (str): Contraseña en texto plano
        """
        self.password_hash = generate_password_hash(password)
```

### Comentarios

#### Comentarios de Sección
```python
# ============================================
# Configuración de Base de Datos
# ============================================

# Validar entrada de usuario
if not username:
    return error
```

#### Comentarios Inline
```python
total = amount * quantity  # Calcular total sin impuestos
formatted = format_currency(total)  # Aplicar formato de moneda
```

## 🎨 HTML/Jinja2

### Estructura de Templates
```html
{% extends "base.html" %}

{% block title %}Título - CuentasClaras{% endblock %}

{% block content %}
<!-- Contenido principal -->
<div class="container">
    <!-- Secciones claramente separadas -->
</div>
{% endblock %}
```

### Nombres de Clases CSS (Tailwind)
- Usar clases utilitarias de Tailwind
- Responsive: mobile-first con breakpoints (sm:, md:, lg:, xl:)
- Colores consistentes: green-600 (principal), red-600 (alertas), blue-600 (acciones)

### Nomenclatura de IDs y Elementos
```html
<!-- kebab-case para IDs -->
<div id="modal-add-debtor"></div>
<div id="mobile-menu"></div>

<!-- Nombres descriptivos -->
<button id="mobile-menu-button"></button>
<form id="form-register-user"></form>
```

## 🗄️ Base de Datos

### Nombres de Tablas
```python
__tablename__ = 'user'      # Singular, minúsculas
__tablename__ = 'debtor'
__tablename__ = 'debt'
```

### Nombres de Columnas
```python
# snake_case, descriptivos
user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
created_at = db.Column(db.DateTime, default=datetime.utcnow)
password_hash = db.Column(db.String(200))
installments_total = db.Column(db.Integer)
```

### Relaciones
```python
# Nombrar con sustantivo plural para uno-a-muchos
debtors = db.relationship('Debtor', backref='user', lazy=True)
debts = db.relationship('Debt', backref='debtor', lazy=True)
```

## 🛣️ Rutas (Blueprints)

### Estructura de Blueprint
```python
"""
CuentasClaras - Rutas de [Módulo]
Descripción de funcionalidad
Autor: Fernando Poblete
"""

from flask import Blueprint, render_template, request, redirect, url_for

# Crear blueprint con prefijo descriptivo
auth_bp = Blueprint('auth', __name__)
debtor_bp = Blueprint('debtor', __name__, url_prefix='/debtor')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Descripción de la ruta
    GET: Qué hace en GET
    POST: Qué hace en POST
    """
    pass
```

### Nomenclatura de Rutas
- **URL**: kebab-case (`/add-debtor`, `/export-pdf`)
- **Función**: snake_case (`def add_debtor()`, `def export_pdf()`)
- **Endpoint**: `blueprint.funcion` (`auth.login`, `debtor.detail`)

### Convenciones de Verbos HTTP
- `GET`: Obtener/Mostrar
- `POST`: Crear/Modificar
- Operaciones de eliminación: POST con confirmación

## 🎯 Flask

### url_for
```python
# Usar siempre con namespace del blueprint
url_for('auth.login')
url_for('main.dashboard')
url_for('debtor.detail', debtor_id=1)
```

### Flash Messages
```python
# Categorías: 'success', 'error', 'info', 'warning'
flash('Operación exitosa', 'success')
flash('Error al procesar', 'error')
```

### Redirecciones
```python
# Siempre usar url_for, nunca hardcodear
return redirect(url_for('main.dashboard'))
return redirect(url_for('debtor.detail', debtor_id=debtor.id))
```

## 📝 Documentación

### Comentarios en Español
- Todo el código está comentado en español
- Docstrings en español
- Mensajes de usuario en español

### README y Docs
- Secciones claras con emojis
- Ejemplos de código cuando sea necesario
- Instrucciones paso a paso

## 🔒 Seguridad

### Passwords
```python
# SIEMPRE usar hash, NUNCA almacenar texto plano
from werkzeug.security import generate_password_hash, check_password_hash

password_hash = generate_password_hash(password)
is_valid = check_password_hash(password_hash, password)
```

### Validación de Input
```python
# Validar antes de procesar
if not name:
    flash('El nombre es obligatorio', 'error')
    return redirect(url_for('main.dashboard'))

# Verificar permisos
if debtor.user_id != current_user.id:
    flash('No tienes permiso', 'error')
    return redirect(url_for('main.dashboard'))
```

## 📦 Git

### Commits
- Mensajes descriptivos en español
- Formato: `Tipo: Descripción breve`
  - `Feature: Agregar exportación PDF`
  - `Fix: Corregir formato de moneda`
  - `Refactor: Modularizar código en blueprints`
  - `Docs: Actualizar README`

### .gitignore
- Ignorar `__pycache__/`
- Ignorar `.env`
- Ignorar `*.db`, `*.sqlite`
- Ignorar `*_old.py`, `*.bak`
- Ignorar `.venv/`, `venv/`

## 🧪 Testing (Futuro)

### Nomenclatura Tests
```python
# Archivos: test_*.py
# Funciones: test_descripcion_accion()

def test_user_can_register():
    pass

def test_debtor_total_debt_calculation():
    pass
```

---

**Autor:** Fernando Poblete  
**Versión:** 1.0.0  
**Última actualización:** Enero 2026
