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
        Sin decimales .00 innecesarios, solo cuando sea necesario y máximo 2
        
        Args:
            amount (float): Monto a formatear
            
        Returns:
            str: Monto formateado con símbolo y separadores
        """
        # Redondear a 2 decimales
        amount = round(amount, 2)
        
        # Determinar si tiene decimales significativos
        has_decimals = (amount % 1) != 0
        
        if self.currency == 'USD':
            # Formato USD: $1.000 o $1.000,50 (punto para miles, coma para decimales)
            if has_decimals:
                formatted = f"{amount:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                # Eliminar ceros innecesarios (ej: $1.000,50 OK, $1.000,00 -> $1.000)
                if formatted.endswith(',00'):
                    formatted = formatted[:-3]
                elif formatted.endswith('0') and ',' in formatted:
                    formatted = formatted.rstrip('0').rstrip(',')
                return f"${formatted}"
            else:
                return f"${amount:,.0f}".replace(',', '.')
        elif self.currency == 'BRL':
            # Formato BRL: R$1.000 o R$1.000,50
            if has_decimals:
                formatted = f"{amount:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                if formatted.endswith(',00'):
                    formatted = formatted[:-3]
                elif formatted.endswith('0') and ',' in formatted:
                    formatted = formatted.rstrip('0').rstrip(',')
                return f"R${formatted}"
            else:
                return f"R${amount:,.0f}".replace(',', '.')
        else:
            # Formato CLP: $1.000 (sin decimales si es entero, con decimales si es necesario)
            if has_decimals:
                formatted = f"{amount:,.2f}".replace(',', '.')
                if formatted.endswith(',00'):
                    formatted = formatted[:-3]
                elif formatted.endswith('0') and ',' in formatted:
                    formatted = formatted.rstrip('0').rstrip(',')
                return f"${formatted}"
            else:
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
    partial_payment = db.Column(db.Float, default=0.0)  # Abono parcial en la cuota actual
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
            # Monto total pagado = cuotas completas + abono parcial
            total_paid = (self.installments_paid * self.installment_amount()) + self.partial_payment
            return self.amount - total_paid
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
    
    def _format_amount(self, amount):
        """
        Formatea un monto sin decimales innecesarios
        Solo muestra decimales cuando es necesario y máximo 2
        
        Args:
            amount (float): Monto a formatear
            
        Returns:
            str: Monto formateado sin símbolo de moneda
        """
        amount = round(amount, 2)
        
        # Si es entero, no mostrar decimales
        if amount % 1 == 0:
            return f"{int(amount):,}".replace(',', '.')
        
        # Si tiene decimales, formatear con máximo 2 y eliminar ceros innecesarios
        formatted = f"{amount:,.2f}".replace(',', '.')
        # Eliminar ceros a la derecha después del punto decimal
        if ',' in formatted or '.' in formatted[-3:]:
            parts = formatted.split(',') if ',' in formatted else formatted.split('.')
            if len(parts) == 2:
                decimal_part = parts[1].rstrip('0')
                if decimal_part:
                    return f"{parts[0]},{decimal_part}"
                return parts[0]
        return formatted
    
    def process_payment(self, payment_amount):
        """
        Procesa un abono a la deuda
        Si la deuda tiene cuotas, aplica el pago y completa cuotas automáticamente si es necesario
        
        Args:
            payment_amount (float): Monto del abono
            
        Returns:
            dict: Información sobre el procesamiento (cuotas completadas, remanente, etc.)
        """
        result = {
            'installments_completed': 0,
            'remaining_payment': 0,
            'debt_completed': False,
            'message': ''
        }
        
        if not self.has_installments:
            # Para deudas sin cuotas, se marca como pagada si el abono >= monto restante
            remaining = self.amount
            if payment_amount >= remaining:
                self.paid = True
                result['debt_completed'] = True
                result['remaining_payment'] = payment_amount - remaining
                if result['remaining_payment'] > 0:
                    result['message'] = f'Deuda pagada completamente. Sobrante: {self._format_amount(result["remaining_payment"])}'
                else:
                    result['message'] = 'Deuda pagada completamente'
            else:
                result['message'] = f'Abono de {self._format_amount(payment_amount)} registrado. Aún queda {self._format_amount(remaining - payment_amount)} por pagar.'
            return result
        
        # Para deudas con cuotas
        installment_value = self.installment_amount()
        available_payment = payment_amount
        
        # Primero, completar la cuota actual si hay abono parcial previo
        if self.partial_payment > 0:
            remaining_in_current = installment_value - self.partial_payment
            if available_payment >= remaining_in_current:
                # Completa la cuota actual
                available_payment -= remaining_in_current
                self.installments_paid += 1
                self.partial_payment = 0
                result['installments_completed'] += 1
            else:
                # Solo suma al abono parcial
                self.partial_payment += available_payment
                result['remaining_payment'] = self.partial_payment
                result['message'] = f'Abono parcial agregado a cuota actual. Llevas {self._format_amount(self.partial_payment)} de {self._format_amount(installment_value)}'
                return result
        
        # Completar cuotas completas con el dinero disponible
        while available_payment >= installment_value and self.installments_paid < self.installments_total:
            available_payment -= installment_value
            self.installments_paid += 1
            result['installments_completed'] += 1
        
        # Si sobra dinero y aún hay cuotas pendientes, guardar como abono parcial
        if available_payment > 0 and self.installments_paid < self.installments_total:
            self.partial_payment = available_payment
            result['remaining_payment'] = available_payment
        
        # Verificar si se completó la deuda
        if self.installments_paid >= self.installments_total:
            self.paid = True
            result['debt_completed'] = True
            result['remaining_payment'] = available_payment
        
        # Mensaje resumen
        if result['installments_completed'] > 0:
            result['message'] = f"{result['installments_completed']} cuota(s) completada(s)."
            if self.partial_payment > 0:
                result['message'] += f" Abono parcial de {self._format_amount(self.partial_payment)} en siguiente cuota."
            if result['debt_completed']:
                result['message'] += " ¡Deuda pagada completamente!"
        
        return result
    
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
