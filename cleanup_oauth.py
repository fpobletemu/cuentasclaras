"""
Script para eliminar columnas de OAuth de la tabla user
Ejecutar: python cleanup_oauth.py
"""

import sqlite3
import os

def cleanup_oauth():
    db_path = 'instance/cuentasclaras.db'
    
    if not os.path.exists(db_path):
        print("❌ Base de datos no encontrada")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔄 Limpiando columnas de OAuth...")
    
    # SQLite no permite DROP COLUMN directamente, hay que recrear la tabla
    try:
        # Crear tabla temporal con estructura correcta
        cursor.execute("""
            CREATE TABLE user_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(80) UNIQUE NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(200) NOT NULL,
                currency VARCHAR(3) NOT NULL DEFAULT 'CLP',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_admin BOOLEAN DEFAULT 0 NOT NULL
            )
        """)
        
        # Copiar datos
        cursor.execute("""
            INSERT INTO user_new (id, username, email, password_hash, currency, created_at, is_admin)
            SELECT id, username, email, password_hash, currency, created_at, is_admin
            FROM user
        """)
        
        # Eliminar tabla vieja y renombrar
        cursor.execute("DROP TABLE user")
        cursor.execute("ALTER TABLE user_new RENAME TO user")
        
        conn.commit()
        print("✅ Columnas de OAuth eliminadas exitosamente")
        
        # Verificar estructura final
        cursor.execute("PRAGMA table_info(user)")
        columns = [col[1] for col in cursor.fetchall()]
        print("\n📊 Estructura final de tabla 'user':")
        for col in columns:
            print(f"  - {col}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    
    conn.close()

if __name__ == '__main__':
    cleanup_oauth()
