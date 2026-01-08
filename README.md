# CuentasClaras 💰

Aplicación web profesional para gestionar préstamos y deudas personales con arquitectura modular, autenticación segura y exportación a PDF.

**Autor:** Fernando Poblete

## 🎯 Características Principales

### 🔐 Autenticación y Seguridad
- Registro de usuarios con validación
- Login seguro con contraseñas hash (bcrypt)
- Sesiones persistentes con Flask-Login
- Protección de rutas privadas

### 👥 Gestión de Deudores
- CRUD completo (Crear, Leer, Actualizar, Eliminar)
- Información de contacto (nombre, teléfono, email)
- Cálculo automático de totales por deudor
- Vista detallada de todas las deudas por persona

### 💳 Gestión de Deudas
- Registro con monto y fecha inicial
- Contador automático de días transcurridos
- Sistema de cuotas opcional con progreso visual
- Marcar deudas como pagadas
- Pagar cuotas individuales
- Notas adicionales por deuda
- **Archivos adjuntos** (comprobantes, PDFs, evidencias de pago)
- Descarga de documentos adjuntos
- Historial completo por deudor

### 💱 Multi-Moneda
- Soporte para CLP (Peso Chileno), USD (Dólar), BRL (Real Brasileño)
- Formato automático con separadores correctos
- Configuración personalizable por usuario:
  - CLP: $1.000
  - USD: $1.000,00
  - BRL: R$1.000,00

### 📄 Exportación PDF
- Exportar deudas de un deudor específico
- Exportar reporte completo de todos los deudores
- PDFs profesionales con tablas y estadísticas
- Formato de moneda respetado en documentos
- **Contador de documentos adjuntos** por deuda en PDFs
- Marca de agua de seguridad con timestamp
- Timestamps múltiples para autenticidad
- Generación con ReportLab

### 📊 Dashboard y Estadísticas
- Total por cobrar (suma de todas las deudas)
- Total cobrado (suma de montos pagados)
- Número de deudores registrados
- Contador de deudas activas
- Tarjetas visuales con iconos

### 🎨 Interfaz y UX
- Diseño responsive (mobile-first)
- Landing page informativa con características
- Navbar adaptable con menú hamburguesa
- Modales para formularios
- Flash messages para feedback
- Tailwind CSS para estilos modernos

## 🏗️ Arquitectura

### Estructura Modular
```
cuentasclaras/
├── app.py              # Application factory
├── config.py           # Configuración por entorno
├── extensions.py       # Extensiones Flask (db, login)
├── models.py           # Modelos SQLAlchemy
├── pdf_generator.py    # Generación de PDFs
├── routes/             # Blueprints
│   ├── auth.py        # Autenticación
│   ├── main.py        # Landing, dashboard, profile
│   ├── debtor.py      # CRUD deudores
│   └── debt.py        # Operaciones deudas
├── templates/          # Plantillas Jinja2
├── requirements.txt    # Dependencias
├── Procfile           # Deploy Render
└── render.yaml        # Blueprint Render
```

### Blueprints (Rutas)
- **auth_bp**: `/register`, `/login`, `/logout`
- **main_bp**: `/`, `/dashboard`, `/profile`, `/export_all_pdf`
- **debtor_bp**: `/debtor/*` (CRUD + export PDF)
- **debt_bp**: `/debt/*` (add, pay, mark_paid, delete)

## 🛠️ Tecnologías

### Backend
- **Flask 3.0** - Framework web
- **Flask-SQLAlchemy 3.1.1** - ORM
- **Flask-Login 0.6.3** - Gestión de sesiones
- **ReportLab 4.2.5** - Generación PDF
- **Werkzeug** - Seguridad (hash passwords)

### Frontend
- **Tailwind CSS** - Framework CSS (CDN)
- **Jinja2** - Templates

### Base de Datos
- **SQLite** - Desarrollo
- **PostgreSQL** - Producción (Render.com)

### Deployment
- **Gunicorn 21.2.0** - Servidor WSGI
- **python-dotenv 1.0.0** - Variables de entorno
- **Render.com** - Hosting (configurado)

## 📦 Instalación Local

### Requisitos Previos
- Python 3.8+
- pip

### Pasos

1. **Clonar repositorio**
```bash
git clone <repo-url>
cd cuentasclaras
```

2. **Crear entorno virtual**
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno (opcional)**
```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tu configuración
# SECRET_KEY=tu-clave-secreta
# DATABASE_URL=sqlite:///cuentasclaras.db
```

5. **Ejecutar aplicación**
```bash
python app.py
```

La aplicación estará en: `http://localhost:5000`

## 🚀 Deployment en Render.com

Ver guía detallada en [DEPLOY_RENDER.md](DEPLOY_RENDER.md)

**Resumen:**
1. Conectar repositorio a Render
2. Usar `render.yaml` para configuración automática
3. Render creará PostgreSQL y Web Service automáticamente

## 🎮 Uso

### Flujo Típico

1. **Registro**: Crear cuenta con username, email y password
2. **Login**: Iniciar sesión
3. **Configurar Moneda**: Ir a Perfil y elegir CLP/USD/BRL
4. **Agregar Deudor**: Dashboard → "Agregar Deudor"
5. **Registrar Deuda**: Click en deudor → "Agregar Deuda"
   - Monto
   - Fecha inicial
   - Cuotas (opcional)
   - Notas
6. **Gestionar Pagos**: 
   - Pagar cuota individual
   - Marcar como pagada completamente
7. **Exportar**: 
   - Botón "Exportar PDF" en detalle de deudor
   - Botón "Exportar Todo a PDF" en dashboard

## 📝 Modelos de Datos

### User
- `id`: Integer (PK)
- `username`: String (único)
- `email`: String (único)
- `password_hash`: String
- `currency`: String (CLP/USD/BRL)
- `created_at`: DateTime
- **Relación**: uno a muchos con Debtor

### Debtor
- `id`: Integer (PK)
- `user_id`: Integer (FK)
- `name`: String
- `phone`: String (opcional)
- `email`: String (opcional)
- `created_at`: DateTime
- **Métodos**: `total_debt()`, `total_paid()`
- **Relación**: uno a muchos con Debt

### Debt
- `id`: Integer (PK)
- `debtor_id`: Integer (FK)
- `amount`: Float
- `initial_date`: Date
- `has_installments`: Boolean
- `installments_total`: Integer
- `installments_paid`: Integer
- `paid`: Boolean
- `notes`: Text
- `debt_attachments`: Text (JSON - archivos de deuda)
- `payment_attachments`: Text (JSON - evidencias de pago)
- **Métodos**: `days_elapsed()`, `installment_amount()`, `remaining_amount()`, `get_debt_attachments()`, `get_payment_attachments()`, `count_attachments()`

## 🤝 Contribuciones

Este es un proyecto personal desarrollado por Fernando Poblete.

## 📄 Licencia

Este proyecto es privado y de uso personal.

## 📧 Contacto

**Fernando Poblete**
- Proyecto: CuentasClaras - Gestión de Deudas Personales

---

**Versión:** 1.0.0  
**Última actualización:** Enero 2026
- Usa el botón "Marcar Pagado" cuando se complete el pago
- Contador de días muestra el tiempo transcurrido

## 📊 Modelos de Base de Datos

### User (Usuario)
- `id`: Identificador único
- `username`: Nombre de usuario (único)
- `email`: Correo electrónico (único)
- `password_hash`: Contraseña encriptada

### Debtor (Deudor)
- `id`: Identificador único
- `user_id`: Relación con usuario propietario
- `name`: Nombre del deudor
- `phone`: Teléfono (opcional)
- `email`: Email (opcional)
- `created_at`: Fecha de registro

### Debt (Deuda)
- `id`: Identificador único
- `debtor_id`: Relación con deudor
- `amount`: Monto de la deuda
- `initial_date`: Fecha inicial
- `has_installments`: ¿Tiene cuotas?
- `installments_total`: Total de cuotas
- `installments_paid`: Cuotas pagadas
- `paid`: Estado de pago
- `notes`: Notas adicionales
- `debt_attachments`: Archivos adjuntos de la deuda (JSON)
- `payment_attachments`: Evidencias de pago (JSON)

## 🔒 Seguridad

- ✅ Contraseñas hasheadas con Werkzeug
- ✅ Autenticación de sesiones con Flask-Login
- ✅ Validación de permisos por usuario
- ✅ Protección de rutas con `@login_required`
- ✅ Prevención de acceso no autorizado a datos de otros usuarios

## 🎨 Interfaz

- **Diseño Responsivo:** Funciona en desktop, tablet y móvil
- **Tailwind CSS:** Estilos modernos y profesionales
- **Modales Interactivos:** Para agregar/editar información
- **Feedback Visual:** Colores según estado (rojo=pendiente, verde=pagado)
- **Iconos SVG:** Interfaz limpia y clara

## 📁 Estructura del Proyecto

```
cuentasclaras/
├── app.py                      # Aplicación Flask principal
├── requirements.txt            # Dependencias
├── Procfile                    # Configuración Render/Heroku
├── render.yaml                 # Blueprint Render.com
├── .env.example                # Plantilla variables entorno
├── .gitignore                  # Archivos excluidos de Git
├── DEPLOY_RENDER.md            # Guía de despliegue
├── cuentasclaras.db           # Base de datos SQLite (auto-generada)
├── templates/                  # Plantillas HTML
│   ├── base.html              # Plantilla base
│   ├── landing.html           # Página de inicio
│   ├── login.html             # Inicio de sesión
│   ├── register.html          # Registro de usuarios
│   ├── dashboard.html         # Dashboard principal
│   ├── debtor_detail.html     # Detalle de deudor
│   └── profile.html           # Perfil de usuario
└── .github/
    └── copilot-instructions.md # Instrucciones del proyecto
```

## 🚀 Funcionalidades Futuras

- [ ] Exportar reportes a PDF/Excel
- [ ] Notificaciones por email
- [ ] Recordatorios automáticos
- [ ] Gráficos y análisis avanzados
- [ ] Categorías de deudas
- [ ] Calculadora de intereses
- [ ] Historial de cambios
- [ ] Backup automático
- [ ] Aplicación móvil (React Native)

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Si encuentras un bug o tienes una idea para mejorar la aplicación:

1. Crea un issue describiendo el problema/mejora
2. Fork el repositorio
3. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
4. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
5. Push a la rama (`git push origin feature/AmazingFeature`)
6. Abre un Pull Request

## 📝 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## 👨‍💻 Autor

**Fernando Poblete**
- GitHub: [@fpobletemu](https://github.com/fpobletemu)
- Proyecto: [CuentasClaras](https://github.com/fpobletemu/cuentasclaras)

Desarrollado con ❤️ para ayudar a mantener las cuentas claras y las relaciones sanas.

---

## 🌐 Enlaces

- [Repositorio en GitHub](https://github.com/fpobletemu/cuentasclaras)
- [Guía de Despliegue en Render](DEPLOY_RENDER.md)
- [Demo en Vivo](https://cuentasclaras.onrender.com) *(próximamente)*

---

**CuentasClaras** - Porque las buenas relaciones empiezan con cuentas claras 🤝💰
