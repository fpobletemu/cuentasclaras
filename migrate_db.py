"""
Script de migración para agregar campos de archivos adjuntos a la tabla debt
"""

from app import create_app
from extensions import db

def migrate_database():
    """Agrega columnas de archivos adjuntos si no existen"""
    app = create_app()
    
    with app.app_context():
        # Verificar si necesitamos agregar las columnas
        from sqlalchemy import inspect, text
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('debt')]
        
        if 'debt_attachments' not in columns or 'payment_attachments' not in columns:
            print("Agregando columnas de archivos adjuntos...")
            
            # Agregar columnas usando SQL directo
            with db.engine.connect() as conn:
                if 'debt_attachments' not in columns:
                    conn.execute(text("ALTER TABLE debt ADD COLUMN debt_attachments TEXT"))
                    print("✓ Columna 'debt_attachments' agregada")
                
                if 'payment_attachments' not in columns:
                    conn.execute(text("ALTER TABLE debt ADD COLUMN payment_attachments TEXT"))
                    print("✓ Columna 'payment_attachments' agregada")
                
                conn.commit()
            
            print("Migración completada exitosamente!")
        else:
            print("Las columnas ya existen. No se requiere migración.")

if __name__ == '__main__':
    migrate_database()
