"""
Script de prueba para verificar creación de usuario admin
"""

from app import create_app
from extensions import db
from models import User

app = create_app()

with app.app_context():
    # Buscar usuario admin
    admin = User.query.filter_by(username='admin').first()
    
    if admin:
        print("✅ Usuario admin encontrado:")
        print(f"  - Username: {admin.username}")
        print(f"  - Email: {admin.email}")
        print(f"  - Is Admin: {admin.is_admin}")
        print(f"  - Currency: {admin.currency}")
        print(f"  - Created: {admin.created_at}")
    else:
        print("❌ Usuario admin no encontrado")
    
    # Listar todos los usuarios
    all_users = User.query.all()
    print(f"\n📊 Total de usuarios en sistema: {len(all_users)}")
    for user in all_users:
        admin_badge = "👑 ADMIN" if user.is_admin else "👤 USER"
        print(f"  - {admin_badge} | {user.username} ({user.email})")
