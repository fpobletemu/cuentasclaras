"""
Script de migración para agregar el campo partial_payment a la tabla debt
Este campo trackea los abonos parciales aplicados a la cuota actual

Ejecutar con: python migrate_partial_payment.py
"""

from app import create_app
from extensions import db
from sqlalchemy import text

def migrate_partial_payment():
    """
    Agrega la columna partial_payment a la tabla debt si no existe
    """
    app = create_app()
    
    with app.app_context():
        try:
            # Verificar si la columna ya existe
            result = db.session.execute(text("PRAGMA table_info(debt)"))
            columns = [row[1] for row in result]
            
            if 'partial_payment' in columns:
                print("✅ La columna 'partial_payment' ya existe en la tabla 'debt'")
                return
            
            # Agregar la columna
            print("🔄 Agregando columna 'partial_payment' a la tabla 'debt'...")
            db.session.execute(text("ALTER TABLE debt ADD COLUMN partial_payment FLOAT DEFAULT 0.0"))
            db.session.commit()
            
            print("✅ Migración completada exitosamente")
            print("   - Se agregó la columna 'partial_payment' (FLOAT, default: 0.0)")
            print("   - Todas las deudas existentes tienen partial_payment = 0.0")
            
        except Exception as e:
            print(f"❌ Error durante la migración: {e}")
            db.session.rollback()

if __name__ == '__main__':
    print("="*60)
    print("MIGRACIÓN: Agregar campo partial_payment a tabla debt")
    print("="*60)
    migrate_partial_payment()
    print("="*60)
