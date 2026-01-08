# CuentasClaras - Deployment Guide para Render.com

## 📋 Preparación Completada

Tu aplicación ya está lista para desplegarse en Render.com con las siguientes configuraciones:

### ✅ Archivos Creados/Modificados:

1. **requirements.txt** - Dependencias actualizadas con:
   - gunicorn (servidor WSGI para producción)
   - psycopg2-binary (driver PostgreSQL)
   - python-dotenv (gestión de variables de entorno)

2. **Procfile** - Comando para iniciar la aplicación

3. **render.yaml** - Configuración automática de Render (Blueprint)

4. **.env.example** - Plantilla de variables de entorno

5. **app.py** - Modificado para:
   - Soportar PostgreSQL en producción
   - Usar variables de entorno
   - Ajustar puerto dinámicamente

---

## 🚀 Pasos para Desplegar en Render.com

### Opción A: Deploy con Blueprint (Recomendado)

1. **Sube tu código a GitHub:**
   ```bash
   cd cuentasclaras
   git init
   git add .
   git commit -m "Preparar app para Render"
   git branch -M main
   git remote add origin https://github.com/TU_USUARIO/cuentasclaras.git
   git push -u origin main
   ```

2. **En Render.com:**
   - Ve a https://render.com y crea una cuenta
   - Click en "New +" → "Blueprint"
   - Conecta tu repositorio GitHub
   - Render detectará automáticamente `render.yaml`
   - Click en "Apply" para crear el servicio web + base de datos PostgreSQL

### Opción B: Deploy Manual

1. **Sube código a GitHub** (igual que Opción A)

2. **Crear Base de Datos PostgreSQL:**
   - En Render Dashboard → "New +" → "PostgreSQL"
   - Nombre: `cuentasclaras-db`
   - Plan: Free
   - Copia la "Internal Database URL"

3. **Crear Web Service:**
   - "New +" → "Web Service"
   - Conecta tu repo de GitHub
   - Configuración:
     - **Name:** cuentasclaras
     - **Region:** Oregon (o la más cercana)
     - **Branch:** main
     - **Runtime:** Python 3
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `gunicorn app:app`
     - **Plan:** Free

4. **Agregar Variables de Entorno:**
   - En "Environment" tab del servicio:
     ```
     SECRET_KEY = [genera uno aleatorio de 50+ caracteres]
     DATABASE_URL = [pega la Internal Database URL de PostgreSQL]
     FLASK_ENV = production
     ```

5. **Deploy:**
   - Click en "Create Web Service"
   - Render compilará e iniciará tu app (toma ~5 min)

---

## ⚠️ Consideraciones Importantes

### 1. **Base de Datos**
- PostgreSQL Free tier: 90 días gratis, luego necesitas plan paid o recrear
- Hacer backups periódicos
- Las tablas se crean automáticamente en el primer inicio

### 2. **Primer Usuario**
- No hay usuario predefinido
- Usa la página de registro para crear tu cuenta
- Considera agregar un usuario admin inicial si lo necesitas

### 3. **Moneda**
- Los usuarios pueden elegir entre CLP, USD y BRL en su perfil
- Por defecto se usa CLP

### 4. **Dominio Personalizado**
- Render da un dominio: `https://cuentasclaras-XXXX.onrender.com`
- Puedes conectar tu dominio propio en Settings → Custom Domains

### 5. **Plan Free Limitations**
- App "duerme" tras 15 min sin actividad
- Primera carga después de dormir toma ~30 seg
- 750 horas/mes gratis (suficiente para 1 servicio 24/7)

---

## 🔍 Verificación Post-Deploy

1. Visita tu URL de Render
2. Verifica que cargue la página de login
3. Crea una cuenta de usuario
4. Inicia sesión
5. Prueba crear un deudor
6. Agrega una deuda
7. Cambia la moneda en tu perfil
8. Verifica que los formatos se actualicen

---

## 🐛 Troubleshooting

**Error: "Application failed to respond"**
- Revisa logs en Render Dashboard → tu servicio → Logs
- Verifica que DATABASE_URL esté correctamente configurada

**Error de base de datos:**
- Verifica que la conexión PostgreSQL esté activa
- Revisa que DATABASE_URL tenga el formato correcto (postgresql://)

**Formato de moneda no se actualiza:**
- Verifica que el campo `currency` se creó en la tabla User
- Puede requerir recrear la base de datos si migraste desde SQLite

---

## 📞 Próximos Pasos

1. Deploy en Render siguiendo Opción A o B
2. Crear tu cuenta de usuario
3. Configurar tu moneda preferida en Perfil
4. (Opcional) Conectar dominio personalizado
5. (Opcional) Configurar GitHub Actions para auto-deploy

## 🔐 Seguridad en Producción

- ✅ SECRET_KEY generada automáticamente por Render
- ✅ HTTPS habilitado por defecto
- ✅ Base de datos con credenciales seguras
- ✅ Variables de entorno protegidas

¿Necesitas ayuda con algún paso específico?
