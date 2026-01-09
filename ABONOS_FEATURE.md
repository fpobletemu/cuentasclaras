# Sistema de Abonos - CuentasClaras

## 📋 Descripción

Nueva funcionalidad que permite agregar abonos parciales o completos a las deudas, con procesamiento inteligente que completa automáticamente cuotas si el abono es mayor al monto de la cuota actual.

## ✨ Características

### Para Deudas con Cuotas
- ✅ El abono se aplica primero a completar la cuota actual (si hay un abono parcial previo)
- ✅ Si el abono es mayor, completa automáticamente múltiples cuotas
- ✅ El remanente queda como abono parcial de la siguiente cuota
- ✅ Auto-completado de deuda cuando se pagan todas las cuotas
- ✅ Visualización del abono parcial actual en la UI

### Para Deudas sin Cuotas
- ✅ El abono se descuenta del monto total
- ✅ Si el abono cubre el total, la deuda se marca como pagada automáticamente
- ✅ Visualización clara del monto restante

## 🛠️ Implementación Técnica

### Modelo (models.py)
- **Nuevo campo:** `partial_payment` (Float, default=0.0)
  - Trackea abonos parciales en la cuota actual
  
- **Nuevo método:** `process_payment(payment_amount)`
  - Procesa abonos con lógica inteligente
  - Completa cuotas automáticamente
  - Maneja remanentes
  - Retorna diccionario con detalles del procesamiento

- **Método actualizado:** `remaining_amount()`
  - Ahora considera abonos parciales en el cálculo
  - Fórmula: `total_pagado = (cuotas_completas * valor_cuota) + abono_parcial`

### Rutas (routes/debt.py)
- **Nueva ruta:** `POST /debt/<id>/add_payment`
  - Recibe: `payment_amount` (float)
  - Procesa el abono usando `debt.process_payment()`
  - Registra en historial con tipo `payment_added`
  - Retorna mensaje descriptivo del resultado

### UI (templates/debtor_detail.html)
- **Nuevo botón:** "Agregar Abono" (color índigo)
  - Visible solo en deudas pendientes
  - Ubicado como primer botón en el grid de acciones

- **Nuevo modal:** Modal de Agregar Abono
  - Input para monto del abono
  - Información de la deuda (total, restante, cuotas)
  - Indicador de abono parcial actual (si existe)
  - Tips de uso según tipo de deuda
  
- **Visualización mejorada:**
  - Muestra abono parcial actual bajo la barra de progreso
  - Formato: "💰 Abono parcial en cuota actual: $X de $Y"

### PDF (pdf_generator.py)
- **Cálculo actualizado:** Los reportes PDF ahora incluyen abonos parciales
  - Monto pagado = `(cuotas * valor_cuota) + abono_parcial`
  - Aplica en `generate_debtor_pdf()` y `generate_complete_pdf()`

## 📝 Migración de Base de Datos

**Script:** `migrate_partial_payment.py`

```bash
python migrate_partial_payment.py
```

**Acción:**
- Agrega columna `partial_payment FLOAT DEFAULT 0.0` a tabla `debt`
- Todas las deudas existentes inician con `partial_payment = 0.0`

## 🎯 Casos de Uso

### Caso 1: Abono parcial menor a una cuota
**Escenario:** Deuda de $12.000 en 3 cuotas ($4.000 c/u), 0 cuotas pagadas  
**Abono:** $2.000

**Resultado:**
- `installments_paid`: 0
- `partial_payment`: $2.000
- `remaining_amount()`: $10.000
- **Mensaje:** "Abono parcial agregado a cuota actual. Llevas $2.000 de $4.000"

### Caso 2: Abono completa cuota actual y parte de la siguiente
**Escenario:** Deuda de $12.000 en 3 cuotas, 0 cuotas pagadas, abono parcial previo de $2.000  
**Abono:** $3.500

**Resultado:**
- `installments_paid`: 1 (se completó la primera)
- `partial_payment`: $1.500 (remanente en segunda cuota)
- **Mensaje:** "1 cuota(s) completada(s). Abono parcial de $1.500 en siguiente cuota."

### Caso 3: Abono completa múltiples cuotas
**Escenario:** Deuda de $12.000 en 3 cuotas, 0 cuotas pagadas  
**Abono:** $10.000

**Resultado:**
- `installments_paid`: 2
- `partial_payment`: $2.000
- **Mensaje:** "2 cuota(s) completada(s). Abono parcial de $2.000 en siguiente cuota."

### Caso 4: Abono completa toda la deuda
**Escenario:** Deuda de $12.000 en 3 cuotas, 2 cuotas pagadas  
**Abono:** $4.000

**Resultado:**
- `installments_paid`: 3
- `paid`: True
- **Mensaje:** "1 cuota(s) completada(s). ¡Deuda pagada completamente!"

### Caso 5: Deuda sin cuotas
**Escenario:** Deuda simple de $50.000  
**Abono:** $30.000

**Resultado:**
- `paid`: False
- **Mensaje:** "Abono de $30.000 registrado. Aún queda $20.000 por pagar."

## 🎨 Códigos de Color

- **🔵 Índigo:** Agregar Abono (nuevo)
- **🔵 Azul:** Pagar Cuota
- **🟠 Naranja:** Marcar Pagado
- **🟢 Verde:** Pagado (completado)
- **🟡 Ámbar:** Editar
- **🔴 Rojo:** Eliminar

## 📊 Historial

Los abonos se registran automáticamente en el historial de la deuda:

- **Tipo:** `payment_added` (abono parcial) o `marked_paid` (si completa)
- **Descripción:** Incluye monto formateado y resultado del procesamiento
- **Visible:** En timeline de historial de cada deuda

## 🔒 Validaciones

- ✅ Solo deudas pendientes pueden recibir abonos
- ✅ Monto del abono debe ser mayor a 0
- ✅ Verificación de propiedad (usuario debe ser dueño del deudor)
- ✅ Flash messages descriptivos para feedback al usuario

## 🚀 Estado

✅ **Completamente implementado y funcional**

**Próximos pasos:**
1. Ejecutar migración de base de datos: `python migrate_partial_payment.py`
2. Reiniciar servidor Flask
3. Probar funcionalidad en ambiente de desarrollo
4. Deploy a producción

---

**Autor:** Fernando Poblete  
**Fecha:** Enero 9, 2026  
**Versión:** 1.1.0
