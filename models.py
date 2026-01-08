"""
CuentasClaras - Modelos de Base de Datos
Definición de entidades: User, Debtor, Debt
Autor: Fernando Poblete
"""

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
from extensions import db


class User(UserMixin, db.Model):
    """
    Modelo de Usuario
    Representa a un usuario registrado en el sistema
    """
    __tablename__ = 'user'
    
    # Campos
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    currency = db.Column(db.String(3), default='CLP', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relaciones
    debtors = db.relationship('Debtor', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """
        Genera y almacena el hash de la contraseña
        
        Args:
            password (str): Contraseña en texto plano
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """
        Verifica si la contraseña coincide con el hash almacenado
        
        Args:
            password (str): Contraseña a verificar
            
        Returns:
            bool: True si la contraseña es correcta
        """
        return check_password_hash(self.password_hash, password)
    
    def format_currency(self, amount):
        """
        Formatea un monto según la moneda preferida del usuario
        
        Args:
            amount (float): Monto a formatear
            
        Returns:
            str: Monto formateado con símbolo y separadores
        """
        if self.currency == 'USD':
            # Formato USD: $1.000,00 (punto para miles, coma para decimales)
            return f"${amount:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        elif self.currency == 'BRL':
            # Formato BRL: R$1.000,00
            return f"R${amount:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        else:
            # Formato CLP por defecto: $1.000 (sin decimales)
            return f"${amount:,.0f}".replace(',', '.')
    
    def __repr__(self):
        return f'<User {self.username}>'


class Debtor(db.Model):
    """
    Modelo de Deudor
    Representa a una persona que debe dinero al usuario
    """
    __tablename__ = 'debtor'
    
    # Campos
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    debts = db.relationship('Debt', backref='debtor', lazy=True, cascade='all, delete-orphan')
    
    def total_debt(self):
        """
        Calcula el total adeudado (deudas no pagadas)
        
        Returns:
            float: Suma de deudas pendientes
        """
        return sum(debt.amount for debt in self.debts if not debt.paid)
    
    def total_paid(self):
        """
        Calcula el total pagado
        
        Returns:
            float: Suma de deudas pagadas
        """
        return sum(debt.amount for debt in self.debts if debt.paid)
    
    def __repr__(self):
        return f'<Debtor {self.name}>'


class Debt(db.Model):
    """
    Modelo de Deuda
    Representa una deuda individual de un deudor
    """
    __tablename__ = 'debt'
    
    # Campos
    id = db.Column(db.Integer, primary_key=True)
    debtor_id = db.Column(db.Integer, db.ForeignKey('debtor.id'), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    initial_date = db.Column(db.Date, nullable=False, default=date.today)
    has_installments = db.Column(db.Boolean, default=False)
    installments_total = db.Column(db.Integer, default=1)
    installments_paid = db.Column(db.Integer, default=0)
    paid = db.Column(db.Boolean, default=False, index=True)
    notes = db.Column(db.Text)
    
    # Archivos adjuntos (guardados como JSON string con lista de nombres)
    debt_attachments = db.Column(db.Text)  # Comprobantes, PDFs de deuda, etc.
    payment_attachments = db.Column(db.Text)  # Evidencias de pago
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def days_elapsed(self):
        """
        Calcula los días transcurridos desde la fecha inicial
        
        Returns:
            int: Número de días
        """
        return (date.today() - self.initial_date).days
    
    def installment_amount(self):
        """
        Calcula el monto de cada cuota
        
        Returns:
            float: Monto por cuota
        """
        if self.has_installments and self.installments_total > 0:
            return self.amount / self.installments_total
        return self.amount
    
    def remaining_amount(self):
        """
        Calcula el monto restante por pagar
        
        Returns:
            float: Monto pendiente
        """
        if self.has_installments:
            return self.amount - (self.installments_paid * self.installment_amount())
        return self.amount if not self.paid else 0
    
    def get_debt_attachments(self):
        """
        Obtiene lista de archivos de deuda adjuntos
        
        Returns:
            list: Lista de nombres de archivos
        """
        if not self.debt_attachments:
            return []
        import json
        try:
            return json.loads(self.debt_attachments)
        except:
            return []
    
    def get_payment_attachments(self):
        """
        Obtiene lista de archivos de evidencia de pago
        
        Returns:
            list: Lista de nombres de archivos
        """
        if not self.payment_attachments:
            return []
        import json
        try:
            return json.loads(self.payment_attachments)
        except:
            return []
    
    def count_attachments(self):
        """
        Cuenta el total de archivos adjuntos
        
        Returns:
            int: Total de documentos adjuntos
        """
        return len(self.get_debt_attachments()) + len(self.get_payment_attachments())
    
    def __repr__(self):
        return f'<Debt ${self.amount} - Debtor {self.debtor_id}>'


class DebtHistory(db.Model):
    """
    Modelo de Historial de Deudas
    Registra todos los cambios y acciones sobre una deuda
    """
    __tablename__ = 'debt_history'
    
    # Campos
    id = db.Column(db.Integer, primary_key=True)
    debt_id = db.Column(db.Integer, db.ForeignKey('debt.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action_type = db.Column(db.String(50), nullable=False)  # created, edited, installment_paid, marked_paid, deleted
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relaciones
    debt = db.relationship('Debt', backref=db.backref('history', lazy=True, cascade='all, delete-orphan', order_by='DebtHistory.created_at.desc()'))
    user = db.relationship('User', backref='debt_actions')
    
    def __repr__(self):
        return f'<DebtHistory {self.action_type} - Debt {self.debt_id}>'
