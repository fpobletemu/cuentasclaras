from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Configuración de base de datos (PostgreSQL en producción, SQLite en desarrollo)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///cuentasclaras.db')
# Render usa postgres:// pero SQLAlchemy necesita postgresql://
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'tu-clave-secreta-cambiar-en-produccion')

db = SQLAlchemy(app)

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ============== MODELOS ==============

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    currency = db.Column(db.String(3), default='CLP', nullable=False)
    debtors = db.relationship('Debtor', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def format_currency(self, amount):
        """Formatea el monto según la moneda del usuario"""
        if self.currency == 'USD':
            # USD: $1,000.00
            return f"${amount:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        elif self.currency == 'BRL':
            # BRL: R$1.000,00
            return f"R${amount:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        else:  # CLP por defecto
            # CLP: $1.000 (sin decimales)
            return f"${amount:,.0f}".replace(',', '.')

class Debtor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    debts = db.relationship('Debt', backref='debtor', lazy=True, cascade='all, delete-orphan')
    
    def total_debt(self):
        return sum(debt.amount for debt in self.debts if not debt.paid)
    
    def total_paid(self):
        return sum(debt.amount for debt in self.debts if debt.paid)

class Debt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    debtor_id = db.Column(db.Integer, db.ForeignKey('debtor.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    initial_date = db.Column(db.Date, nullable=False, default=date.today)
    has_installments = db.Column(db.Boolean, default=False)
    installments_total = db.Column(db.Integer, default=1)
    installments_paid = db.Column(db.Integer, default=0)
    paid = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    
    def days_elapsed(self):
        return (date.today() - self.initial_date).days
    
    def installment_amount(self):
        if self.has_installments and self.installments_total > 0:
            return self.amount / self.installments_total
        return self.amount
    
    def remaining_amount(self):
        if self.has_installments:
            return self.amount - (self.installments_paid * self.installment_amount())
        return self.amount if not self.paid else 0

# ============== RUTAS ==============

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('landing.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('El nombre de usuario ya existe', 'error')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('El email ya está registrado', 'error')
            return redirect(url_for('register'))
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('¡Registro exitoso! Por favor inicia sesión', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        
        flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        currency = request.form.get('currency')
        if currency in ['USD', 'CLP', 'BRL']:
            current_user.currency = currency
            db.session.commit()
            flash('Moneda actualizada exitosamente', 'success')
        else:
            flash('Moneda no válida', 'error')
        return redirect(url_for('profile'))
    
    return render_template('profile.html')

@app.route('/dashboard')
@login_required
def dashboard():
    debtors = Debtor.query.filter_by(user_id=current_user.id).all()
    
    # Calcular estadísticas totales
    total_owed = sum(debtor.total_debt() for debtor in debtors)
    total_paid = sum(debtor.total_paid() for debtor in debtors)
    total_debtors = len(debtors)
    active_debts = sum(len([d for d in debtor.debts if not d.paid]) for debtor in debtors)
    
    stats = {
        'total_owed': total_owed,
        'total_paid': total_paid,
        'total_debtors': total_debtors,
        'active_debts': active_debts
    }
    
    return render_template('dashboard.html', debtors=debtors, stats=stats)

@app.route('/debtor/add', methods=['POST'])
@login_required
def add_debtor():
    name = request.form.get('name')
    phone = request.form.get('phone', '')
    email = request.form.get('email', '')
    
    debtor = Debtor(
        user_id=current_user.id,
        name=name,
        phone=phone,
        email=email
    )
    db.session.add(debtor)
    db.session.commit()
    
    flash(f'Deudor {name} agregado exitosamente', 'success')
    return redirect(url_for('dashboard'))

@app.route('/debtor/<int:debtor_id>')
@login_required
def view_debtor(debtor_id):
    debtor = Debtor.query.get_or_404(debtor_id)
    
    if debtor.user_id != current_user.id:
        flash('No tienes permiso para ver este deudor', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('debtor_detail.html', debtor=debtor)

@app.route('/debtor/<int:debtor_id>/edit', methods=['POST'])
@login_required
def edit_debtor(debtor_id):
    debtor = Debtor.query.get_or_404(debtor_id)
    
    if debtor.user_id != current_user.id:
        return jsonify({'error': 'No autorizado'}), 403
    
    debtor.name = request.form.get('name', debtor.name)
    debtor.phone = request.form.get('phone', debtor.phone)
    debtor.email = request.form.get('email', debtor.email)
    
    db.session.commit()
    flash('Deudor actualizado exitosamente', 'success')
    return redirect(url_for('view_debtor', debtor_id=debtor_id))

@app.route('/debtor/<int:debtor_id>/delete', methods=['POST'])
@login_required
def delete_debtor(debtor_id):
    debtor = Debtor.query.get_or_404(debtor_id)
    
    if debtor.user_id != current_user.id:
        return jsonify({'error': 'No autorizado'}), 403
    
    db.session.delete(debtor)
    db.session.commit()
    
    flash('Deudor eliminado exitosamente', 'success')
    return redirect(url_for('dashboard'))

@app.route('/debt/add', methods=['POST'])
@login_required
def add_debt():
    debtor_id = request.form.get('debtor_id')
    amount = float(request.form.get('amount'))
    initial_date = datetime.strptime(request.form.get('initial_date'), '%Y-%m-%d').date()
    has_installments = request.form.get('has_installments') == 'true'
    installments_total = int(request.form.get('installments_total', 1))
    notes = request.form.get('notes', '')
    
    debtor = Debtor.query.get_or_404(debtor_id)
    if debtor.user_id != current_user.id:
        return jsonify({'error': 'No autorizado'}), 403
    
    debt = Debt(
        debtor_id=debtor_id,
        amount=amount,
        initial_date=initial_date,
        has_installments=has_installments,
        installments_total=installments_total if has_installments else 1,
        notes=notes
    )
    db.session.add(debt)
    db.session.commit()
    
    flash('Deuda agregada exitosamente', 'success')
    return redirect(url_for('view_debtor', debtor_id=debtor_id))

@app.route('/debt/<int:debt_id>/pay_installment', methods=['POST'])
@login_required
def pay_installment(debt_id):
    debt = Debt.query.get_or_404(debt_id)
    
    if debt.debtor.user_id != current_user.id:
        return jsonify({'error': 'No autorizado'}), 403
    
    if debt.has_installments and debt.installments_paid < debt.installments_total:
        debt.installments_paid += 1
        
        if debt.installments_paid >= debt.installments_total:
            debt.paid = True
        
        db.session.commit()
        flash('Cuota pagada exitosamente', 'success')
    
    return redirect(url_for('view_debtor', debtor_id=debt.debtor_id))

@app.route('/debt/<int:debt_id>/mark_paid', methods=['POST'])
@login_required
def mark_paid(debt_id):
    debt = Debt.query.get_or_404(debt_id)
    
    if debt.debtor.user_id != current_user.id:
        return jsonify({'error': 'No autorizado'}), 403
    
    debt.paid = True
    if debt.has_installments:
        debt.installments_paid = debt.installments_total
    
    db.session.commit()
    flash('Deuda marcada como pagada', 'success')
    return redirect(url_for('view_debtor', debtor_id=debt.debtor_id))

@app.route('/debt/<int:debt_id>/delete', methods=['POST'])
@login_required
def delete_debt(debt_id):
    debt = Debt.query.get_or_404(debt_id)
    
    if debt.debtor.user_id != current_user.id:
        return jsonify({'error': 'No autorizado'}), 403
    
    debtor_id = debt.debtor_id
    db.session.delete(debt)
    db.session.commit()
    
    flash('Deuda eliminada exitosamente', 'success')
    return redirect(url_for('view_debtor', debtor_id=debtor_id))

# ============== INICIALIZACIÓN ==============

with app.app_context():
    db.create_all()
    print('✓ Base de datos inicializada')

if __name__ == '__main__':
    # En desarrollo usa el servidor de Flask, en producción usa gunicorn
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)
