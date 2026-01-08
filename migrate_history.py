"""
Script de migración para agregar tabla debt_history
Ejecutar: python migrate_history.py
"""

from app import create_app
from extensions import db
from models import DebtHistory

def migrate_history():
    """Crea la tabla debt_history en la base de datos"""
    app = create_app()
    
    with app.app_context():
        try:
            # Crear tabla debt_history
            db.create_all()
            print("✅ Tabla 'debt_history' creada exitosamente")
            
            # Verificar que la tabla existe
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'debt_history' in tables:
                print("✅ Verificación: Tabla 'debt_history' existe en la base de datos")
                
                # Mostrar columnas
                columns = inspector.get_columns('debt_history')
                print("\n📋 Columnas de debt_history:")
                for col in columns:
                    print(f"   - {col['name']}: {col['type']}")
            else:
                print("❌ Error: Tabla 'debt_history' no se encuentra en la base de datos")
                
        except Exception as e:
            print(f"❌ Error durante la migración: {str(e)}")
            return False
    
    return True

if __name__ == '__main__':
    print("🔄 Iniciando migración de base de datos...")
    print("Agregando tabla 'debt_history' para historial de cambios\n")
    
    if migrate_history():
        print("\n✅ Migración completada exitosamente")
        print("La aplicación ahora registrará todos los cambios en las deudas")
    else:
        print("\n❌ Migración fallida. Revisa los errores anteriores")
