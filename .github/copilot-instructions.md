# CuentasClaras - Flask Debt Management App

## Project Overview
Aplicación web profesional para gestión de préstamos y deudas personales con autenticación de usuarios, seguimiento detallado y exportación a PDF.

## Tech Stack
- Flask 3.0 con arquitectura modular (Blueprints)
- Flask-SQLAlchemy 3.1.1 + Flask-Login 0.6.3
- ReportLab 4.2.5 para generación de PDFs
- Tailwind CSS (CDN) para UI responsive
- SQLite (desarrollo) / PostgreSQL (producción)
- Gunicorn para deployment

## Arquitectura Modular

### Estructura del Proyecto
```
cuentasclaras/
├── app.py                 # Application factory
├── config.py             # Configuración (desarrollo/producción)
├── extensions.py         # Inicialización de extensiones Flask
├── models.py             # Modelos: User, Debtor, Debt
├── pdf_generator.py      # Generación de reportes PDF
├── routes/               # Blueprints organizados por funcionalidad
│   ├── __init__.py
│   ├── auth.py          # Login, register, logout
│   ├── main.py          # Landing, dashboard, profile
│   ├── debtor.py        # CRUD de deudores
│   └── debt.py          # Operaciones sobre deudas
├── templates/           # Plantillas Jinja2
└── requirements.txt
```

## Database Models

### User
- id, username, email, password_hash
- currency (CLP/USD/BRL)
- created_at
- Relación: uno a muchos con Debtor

### Debtor
- id, user_id, name, phone, email, created_at
- Métodos: total_debt(), total_paid()
- Relación: uno a muchos con Debt

### Debt
- id, debtor_id, amount, initial_date
- has_installments, installments_total, installments_paid
- paid, notes
- debt_attachments, payment_attachments (JSON)
- Métodos: days_elapsed(), installment_amount(), remaining_amount()
- Métodos: get_debt_attachments(), get_payment_attachments(), count_attachments()

## Features Implementadas

### Autenticación
- ✅ Registro de usuarios con validación
- ✅ Login con hash de contraseñas (werkzeug)
- ✅ Protección de rutas con @login_required
- ✅ Sesiones seguras con Flask-Login

### Gestión de Deudores
- ✅ CRUD completo (crear, leer, actualizar, eliminar)
- ✅ Información de contacto (teléfono, email)
- ✅ Cálculo automático de totales por deudor

### Gestión de Deudas
- ✅ Registro de deudas con fecha inicial
- ✅ Seguimiento de días transcurridos
- ✅ Sistema de cuotas opcional (installments)
- ✅ Progreso visual con barras
- ✅ Marcar como pagadas
- ✅ Notas adicionales
- ✅ **Sistema de archivos adjuntos:**
  - Adjuntar documentos al crear deudas
  - Adjuntar evidencias de pago
  - Descarga de archivos
  - Validación de formatos (PDF, PNG, JPG, DOC, DOCX, TXT)
  - 16MB máximo por archivo
  - Organización automática por usuario/deuda

### Multi-Moneda
- ✅ Soporte para CLP, USD, BRL
- ✅ Formato automático según moneda del usuario
- ✅ Configuración por perfil

### Exportación PDF
- ✅ Exportar deudas de un deudor específico
- ✅ Exportar reporte completo de todos los deudores
- ✅ PDFs profesionales con tablas y estadísticas
- ✅ Formato de moneda correcto en PDFs
- ✅ Marca de agua de seguridad con timestamp
- ✅ Contador de documentos adjuntos por deuda
- ✅ Exportar reporte completo de todos los deudores
- ✅ PDFs profesionales con tablas y estadísticas
- ✅ Formato de moneda correcto en PDFs

### UI/UX
- ✅ Diseño responsive (mobile-first)
- ✅ Landing page con características
- ✅ Dashboard con estadísticas
- ✅ Navbar con menú hamburguesa en móvil
- ✅ Modales para formularios
- ✅ Flash messages para feedback

### Deployment
- ✅ Configuración para Render.com
- ✅ Soporte PostgreSQL en producción
- ✅ Variables de entorno con python-dotenv
- ✅ Procfile y render.yaml configurados

## Blueprints y Rutas

### auth_bp (sin prefijo)
- GET/POST /register - Registro de usuarios
- GET/POST /login - Inicio de sesión
- GET /logout - Cerrar sesión

### main_bp (sin prefijo)
- GET / - Landing page
- GET /dashboard - Dashboard principal (requiere auth)
- GET/POST /profile - Perfil y configuración (requiere auth)
- GET /export_all_pdf - Exportar reporte completo (requiere auth)

### debtor_bp (prefijo: /debtor)
- POST /debtor/add - Crear deudor
- GET /debtor/<id> - Ver detalle de deudor
- POST /debtor/<id>/edit - Editar deudor
- POST /debtor/<id>/delete - Eliminar deudor
- GET /debtor/<id>/export_pdf - Exportar PDF del deudor

### debt_bp (prefijo: /debt)
- POST /debt/add - Crear deuda
- POST /debt/<id>/pay_installment - Pagar cuota
- POST /debt/<id>/mark_paid - Marcar como pagada
- POST /debt/<id>/delete - Eliminar deuda

## Configuration

### Development
- DEBUG=True
- SQLite database
- SQLALCHEMY_ECHO=True (SQL logs)

### Production
- DEBUG=False
- PostgreSQL via DATABASE_URL
- SECRET_KEY desde variable de entorno

## Project Status
✅ Arquitectura modular implementada
✅ Código limpio y documentado
✅ Separación de responsabilidades clara
✅ Todas las funcionalidades operativas
✅ Listo para deployment

## Author
Fernando Poblete
