# CuentasClaras 💰

Aplicación web para gestionar préstamos y deudas personales de forma simple y organizada.

## 🎯 Características

### Gestión de Usuarios
- ✅ Registro de nuevos usuarios
- ✅ Inicio de sesión seguro con contraseñas encriptadas
- ✅ Sesiones persistentes

### Gestión de Deudores
- 👥 Registro de personas que deben dinero
- 📝 Información de contacto (nombre, teléfono, email)
- 📊 Visualización de totales por deudor
- ✏️ Edición y eliminación de deudores

### Gestión de Deudas
- 💵 Registro de deudas con monto y fecha inicial
- ⏰ Contador automático de días transcurridos
- 📅 Soporte para deudas con y sin cuotas
- 💳 Seguimiento de cuotas pagadas
- ✅ Marcar deudas como pagadas
- 📈 Barra de progreso para deudas con cuotas
- 📝 Notas adicionales por deuda

### Dashboard y Estadísticas
- 📊 Total por cobrar (deudas pendientes)
- 💰 Total cobrado (deudas pagadas)
- 👥 Número de deudores
- 📋 Deudas activas
- 🎨 Visualización con tarjetas coloridas

## 🛠️ Tecnologías

- **Backend:** Flask 3.0
- **Base de Datos:** SQLite con Flask-SQLAlchemy
- **Autenticación:** Flask-Login
- **Frontend:** Tailwind CSS
- **Interactividad:** HTMX
- **Seguridad:** Werkzeug (hash de contraseñas)

## 📦 Instalación

### 1. Clonar el repositorio
```bash
cd cuentasclaras
```

### 2. Crear entorno virtual (opcional pero recomendado)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Ejecutar la aplicación
```bash
python app.py
```

La aplicación estará disponible en: `http://localhost:5001`

## 🎮 Uso

### Primer Uso

1. **Registrarse:** Ve a la página de registro y crea tu cuenta
2. **Iniciar Sesión:** Ingresa con tu usuario y contraseña
3. **Agregar Deudor:** Desde el dashboard, haz clic en "Agregar Deudor" y completa la información
4. **Registrar Deuda:** Selecciona un deudor y agrega una nueva deuda con:
   - Monto
   - Fecha inicial
   - Tipo (pago único o con cuotas)
   - Notas opcionales

### Gestión de Deudas

**Deudas con Cuotas:**
- Indica el número total de cuotas al crear la deuda
- Usa el botón "Pagar Cuota" para ir registrando pagos
- La barra de progreso muestra el avance
- Se marca automáticamente como pagada al completar todas las cuotas

**Deudas sin Cuotas:**
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
├── cuentasclaras.db           # Base de datos SQLite (auto-generada)
├── templates/                  # Plantillas HTML
│   ├── base.html              # Plantilla base
│   ├── login.html             # Página de inicio de sesión
│   ├── register.html          # Página de registro
│   ├── dashboard.html         # Dashboard principal
│   └── debtor_detail.html     # Detalle de deudor y deudas
└── .github/
    └── copilot-instructions.md # Instrucciones del proyecto
```

## 🚀 Funcionalidades Futuras

- [ ] Exportar reportes a PDF/Excel
- [ ] Notificaciones por email
- [ ] Recordatorios automáticos
- [ ] Gráficos y análisis avanzados
- [ ] Categorías de deudas
- [ ] Monedas múltiples
- [ ] Calculadora de intereses
- [ ] Historial de cambios
- [ ] Backup automático

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

Desarrollado con ❤️ para ayudar a mantener las cuentas claras.

---

**CuentasClaras** - Porque las buenas relaciones empiezan con cuentas claras 🤝💰
