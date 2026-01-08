"""
Script para resetear contraseña de usuario
Uso: python reset_password.py
"""

from werkzeug.security import generate_password_hash
import sqlite3
import getpass

def reset_password():
    username = input("Ingresa el username: ")
    
    # Verificar que el usuario existe
    conn = sqlite3.connect('instance/cuentasclaras.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM user WHERE username = ?", (username,))
    user = cursor.fetchone()
    
    if not user:
        print(f"❌ Usuario '{username}' no encontrado")
        conn.close()
        return
    
    # Pedir nueva contraseña
    print("\nIngresa la nueva contraseña:")
    new_password = getpass.getpass("Contraseña: ")
    confirm_password = getpass.getpass("Confirmar contraseña: ")
    
    if new_password != confirm_password:
        print("❌ Las contraseñas no coinciden")
        conn.close()
        return
    
    # Generar hash y actualizar
    password_hash = generate_password_hash(new_password)
    cursor.execute("UPDATE user SET password_hash = ? WHERE username = ?", 
                   (password_hash, username))
    conn.commit()
    conn.close()
    
    print(f"✅ Contraseña actualizada exitosamente para '{username}'")

if __name__ == '__main__':
    reset_password()
