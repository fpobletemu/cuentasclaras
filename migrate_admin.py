"""
Script de migración para agregar columna is_admin a la tabla user
Ejecutar: python migrate_admin.py
Autor: Fernando Poblete
"""

import sqlite3
import os

def migrate_admin_column():
    """Agrega columna is_admin a la tabla user si no existe"""
    
    db_path = 'instance/cuentasclaras.db'
    
    if not os.path.exists(db_path):
        print("❌ Base de datos no encontrada")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Verificar columnas existentes
    cursor.execute("PRAGMA table_info(user)")
    columns = [col[1] for col in cursor.fetchall()]
    
    print("📊 Columnas actuales en tabla 'user':")
    for col in columns:
        print(f"  - {col}")
    
    # Verificar y agregar columna is_admin
    if 'is_admin' not in columns:
        print("\n🔄 Agregando columna is_admin...")
        try:
            cursor.execute("ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT 0 NOT NULL")
            conn.commit()
            print("✅ Columna is_admin agregada exitosamente")
        except Exception as e:
            print(f"❌ Error al agregar columna: {e}")
            conn.rollback()
    else:
        print("\n⚠️  Columna 'is_admin' ya existe")
    
    # Verificar columnas finales
    cursor.execute("PRAGMA table_info(user)")
    columns = [col[1] for col in cursor.fetchall()]
    print("\n📊 Columnas finales en tabla 'user':")
    for col in columns:
        print(f"  - {col}")
    
    conn.close()

if __name__ == '__main__':
    print("=" * 60)
    print("   MIGRACIÓN Admin - Tabla User")
    print("=" * 60)
    migrate_admin_column()
    print("\n" + "=" * 60)
