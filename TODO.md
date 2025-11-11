# Tareas para Corregir Errores y Agregar Actualizaciones en Tiempo Real

## Errores Identificados
- [x] Corregir mensajes de toast incompletos en `updateOrderStatus` en waiter_dashboard.html
- [x] Corregir mensajes de toast incompletos en `updateOrderStatus` en receptionist_dashboard.html
- [x] Verificar consistencia en endpoints de API

## Funcionalidad de Actualización en Tiempo Real
- [x] Agregar actualización en tiempo real para `total_sales_today` en receptionist_dashboard.html
- [x] Asegurar que todos los cambios de estado de pedidos (pago, cargo a habitación) actualicen la UI inmediatamente
- [x] Mejorar el modal de pago para actualizar totales de ventas vía WebSocket después del pago
- [x] Agregar eventos de WebSocket faltantes para actualizaciones de pedidos
- [x] Probar funcionalidad en tiempo real en todos los escenarios

## Archivos a Modificar
- [x] restaurant/templates/restaurant/waiter_dashboard.html
- [x] restaurant/templates/restaurant/receptionist_dashboard.html

## Pruebas
- [ ] Probar pagos y verificación de actualización de totales
- [ ] Probar cambios de estado de pedidos
- [ ] Verificar notificaciones en tiempo real
