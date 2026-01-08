# Changelog

Todos los cambios importantes del proyecto CuentasClaras serán documentados en este archivo.

## [1.0.0] - 2026-01-08

### ✨ Funcionalidades Implementadas

#### Arquitectura
- ✅ Implementada arquitectura modular con Flask Blueprints
- ✅ Application Factory pattern en `app.py`
- ✅ Separación de configuración por entorno (desarrollo/producción)
- ✅ Extensiones Flask centralizadas en `extensions.py`
- ✅ Modelos de datos documentados en `models.py`

#### Autenticación y Usuarios
- ✅ Sistema completo de registro de usuarios
- ✅ Login seguro con hash de contraseñas (Werkzeug)
- ✅ Sesiones persistentes con Flask-Login
- ✅ Protección de rutas con decorador @login_required
- ✅ Perfil de usuario con configuración de moneda

#### Gestión de Deudores
- ✅ CRUD completo (Crear, Leer, Actualizar, Eliminar)
- ✅ Información de contacto (nombre, teléfono, email)
- ✅ Cálculo automático de totales por deudor
- ✅ Vista detallada de deudas por deudor

#### Gestión de Deudas
- ✅ Registro de deudas con monto y fecha
- ✅ Contador automático de días transcurridos
- ✅ Sistema opcional de cuotas con progreso visual
- ✅ Pago de cuotas individuales
- ✅ **Auto-completado de deuda al pagar última cuota**
- ✅ Botón "Marcar Pagado" solo para deudas sin cuotas
- ✅ Modal de confirmación con opción de adjuntar evidencia
- ✅ **Sistema de edición de deudas:**
  - Editar monto, cuotas, y notas
  - Botón de edición en header de cada deuda
  - Adjuntar archivos adicionales de evidencia
  - Actualizar sistema de cuotas
- ✅ Notas adicionales por deuda
- ✅ Cálculo de montos restantes
- ✅ **Sistema de archivos adjuntos:**
  - Adjuntar documentos al crear deudas (comprobantes, contratos)
  - Adjuntar evidencias de pago al marcar como pagado
  - Botón de adjuntar evidencia (aparece después de registrar pagos)
  - Validación de formatos: **Solo imágenes (PNG, JPG, JPEG) y PDF**
  - Límite de **5MB por archivo** (reducido para optimización)
  - Descarga de archivos adjuntos
  - Organización automática por usuario y deuda
  - Eliminación automática al borrar deuda
  - **Funcionalidad temporalmente deshabilitada en UI**
- ✅ **Sistema de historial de cambios:**
  - Registro automático de todas las acciones
  - Timeline visual colapsable por deuda
  - Iconos de colores según tipo de acción
  - Tipos: creada, editada, cuota pagada, pagada, eliminada

#### Historial General
- ✅ **Página de historial completo del usuario** (`/history`)
- ✅ Vista de todos los movimientos realizados
- ✅ **Sistema de filtros avanzados:**
  - Filtrar por deudor específico
  - Filtrar por tipo de acción
  - Filtrar por rango de fechas (desde/hasta)
  - Combinación de múltiples filtros
- ✅ Timeline visual con iconos de colores
- ✅ Enlace directo a cada deudor desde historial
- ✅ Contador de resultados dinámico
- ✅ Enlace en navbar (desktop y móvil)
- ✅ Estado vacío con mensaje informativo

#### Interfaz de Usuario
- ✅ **Diseño de botones optimizado:**
  - Grid de 2 columnas en mobile para mejor legibilidad
  - Tamaños uniformes (lg:w-32 en desktop)
  - Padding consistente (px-4 py-2.5)
  - Botón "Editar" reubicado al header de la deuda
- ✅ **Códigos de color semánticos:**
  - 🔵 Azul: Pagar Cuota (acción disponible)
  - 🟠 Naranja: Marcar Pagado (estado pendiente)
  - 🟢 Verde: Pagado (estado completado, deshabilitado)
  - 🟡 Ámbar: Editar (modificar deuda)
  - ⚫ Gris/Slate: Adjuntar (deshabilitado temporalmente)
  - 🔴 Rojo: Eliminar (acción destructiva)
- ✅ Responsive design mejorado para mobile y desktop
- ✅ Estados visuales claros (pagado/pendiente)
- ✅ Iconos SVG para mejor comprensión

#### Multi-Moneda
- ✅ Soporte para CLP, USD, BRL
- ✅ Formato automático con separadores correctos:
  - CLP: $1.000
  - USD: $1.000,00
  - BRL: R$1.000,00
- ✅ Configuración por usuario en perfil

#### Exportación PDF
- ✅ Módulo `pdf_generator.py` con ReportLab
- ✅ Exportar deudas de un deudor específico
- ✅ Exportar reporte completo de todos los deudores
- ✅ PDFs profesionales con tablas y estadísticas
- ✅ Formato de moneda respetado en documentos
- ✅ Diseño con colores y estructura clara
- ✅ **Seguridad de documentos:**
  - Marca de agua diagonal con timestamp en cada página
  - Timestamp en esquina superior derecha
  - Número de página en footer
  - Nota de autenticidad al final
  - Contador de documentos adjuntos por deuda

#### UI/UX
- ✅ Landing page responsive con características
- ✅ Dashboard con estadísticas en tarjetas
- ✅ Diseño mobile-first con Tailwind CSS
- ✅ Navbar adaptable con menú hamburguesa
- ✅ Modales para formularios (agregar deudor/deuda)
- ✅ Flash messages para feedback de operaciones
- ✅ Barras de progreso para cuotas
- ✅ Iconos SVG para mejor visualización

#### Deployment
- ✅ Configuración para Render.com
- ✅ Soporte para PostgreSQL en producción
- ✅ Archivo `render.yaml` para deployment automático
- ✅ `Procfile` para Gunicorn
- ✅ Variables de entorno con python-dotenv
- ✅ Guía de deployment en `DEPLOY_RENDER.md`

### 🏗️ Estructura de Blueprints

#### auth_bp (Autenticación)
- `GET/POST /register` - Registro de usuarios
- `GET/POST /login` - Inicio de sesión
- `GET /logout` - Cerrar sesión

#### main_bp (Principal)
- `GET /` - Landing page
- `GET /dashboard` - Dashboard con estadísticas
- `GET/POST /profile` - Perfil y configuración
- `GET /history` - **Historial general con filtros**
- `GET /export_all_pdf` - Exportar reporte completo

#### debtor_bp (Deudores)
- `POST /debtor/add` - Crear deudor
- `GET /debtor/<id>` - Ver detalle
- `POST /debtor/<id>/edit` - Editar
- `POST /debtor/<id>/delete` - Eliminar
- `GET /debtor/<id>/export_pdf` - Exportar PDF

#### debt_bp (Deudas)
- `POST /debt/add` - Crear deuda (con archivos adjuntos)
- `POST /debt/<id>/edit` - **Editar deuda (monto, cuotas, notas)**
- `POST /debt/<id>/pay_installment` - Pagar cuota (auto-completa si es la última)
- `POST /debt/<id>/mark_paid` - Marcar pagada (con modal y evidencia opcional)
- `POST /debt/<id>/delete` - Eliminar (elimina archivos físicos)
- `POST /debt/<id>/add_payment_evidence` - Adjuntar evidencia de pago
- `GET /debt/<id>/download/<filename>` - Descargar archivo adjunto

### 📦 Dependencias

```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
ReportLab==4.2.5
Gunicorn==21.2.0
psycopg2-binary==2.9.9
python-dotenv==1.0.0
Werkzeug==3.0.1
SQLAlchemy==2.0.36
```

### 🧹 Limpieza y Optimización

- ✅ Eliminado archivo obsoleto `app_old.py` (backup monolítico)
- ✅ Limpiados archivos `__pycache__`
- ✅ Actualizado `.gitignore` para ignorar temporales y backups
- ✅ Código documentado con docstrings en español
- ✅ Comentarios claros en toda la aplicación
- ✅ README actualizado con documentación completa
- ✅ Copilot instructions actualizadas

### 📝 Documentación

- ✅ README.md completo con guías de instalación y uso
- ✅ DEPLOY_RENDER.md con instrucciones de deployment
- ✅ .github/copilot-instructions.md actualizado
- ✅ Comentarios inline en todo el código
- ✅ Docstrings en funciones y métodos

### 🎯 Estado del Proyecto

**Proyecto:** 100% funcional y listo para producción

**Características:**
- ✅ Código limpio y modular
- ✅ Arquitectura escalable con blueprints
- ✅ Separación de responsabilidades clara
- ✅ Documentación completa
- ✅ Listo para deployment en Render.com

---

**Autor:** Fernando Poblete  
**Fecha:** Enero 8, 2026
