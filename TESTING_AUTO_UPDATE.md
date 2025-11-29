# Testing - Auto Actualización del Monitor

## Cambios Realizados

### 1. **Backend (views.py)**
Se modificó la función `save_order()` para retornar una respuesta JSON completa con todos los datos del pedido:

```python
{
    "success": True,
    "order_id": 1,
    "order": {
        "id": 1,
        "identifier": "Habitación 101",
        "room_number": "101",
        "client_identifier": "Juan",
        "status": "pending",
        "status_display": "Pendiente",
        "status_class": "bg-yellow-100 text-yellow-800",
        "items": [
            {
                "id": 1,
                "name": "Pizza",
                "price": 12.99,
                "quantity": 2,
                "note": "Sin cebolla"
            }
        ],
        "total": 25.98,
        "tip_amount": 0.0,
        "created_at": "2025-11-29T10:30:00",
        "updated_at": "2025-11-29T10:30:00"
    }
}
```

### 2. **Frontend (app.js)**
Se agregaron dos mejoras principales:

#### a) setupPusherListeners()
Escucha eventos en tiempo real desde Pusher para actualizar el monitor cuando otros usuarios hacen cambios:
- `newOrder` - Cuando se crea un nuevo pedido
- `orderUpdated` - Cuando se actualiza el estado
- `orderReady` - Cuando un pedido está listo

#### b) Actualización local inmediata en cartSubmitBtn
Cuando el usuario crea un pedido:
1. Envía POST a `/restaurant/save_order/`
2. **Inmediatamente** actualiza el monitor con los datos retornados
3. No espera a que llegue el evento de Pusher
4. Pusher también actualizará a otros usuarios en tiempo real

## Pasos para Probar

### En Desarrollo (Local)

1. **Abre la Waiter Dashboard**
   - Inicia sesión como garzón
   - Deberías ver la vista principal con botones

2. **Crea un pedido**
   - Haz clic en "Comenzar Pedido de Mesa" o "Comenzar Pedido de Barra"
   - Ingresa un identificador (ej: "Habitación 101" o "Juan")
   - Selecciona mesa/habitación si aplica
   - Haz clic en "Comenzar"

3. **Agrega items al carrito**
   - Selecciona items del menú
   - Haz clic en "Agregar al Pedido"
   - El carrito se actualiza visualmente

4. **Abre el carrito modal**
   - Haz clic en el ícono del carrito (esquina superior)
   - Deberías ver todos los items

5. **Envía el pedido**
   - Haz clic en "Enviar Pedido"
   - Abre DevTools (F12) → Console
   - Deberías ver estos logs:
     ```
     ✅ Respuesta completa: {order_id: 1, order: {...}, success: true}
     Order data: {id: 1, identifier: "Habitación 101", ...}
     ✅ Actualizando monitor con nuevo pedido: {...}
     ✅ Monitor actualizado correctamente
     ```

6. **Verifica la actualización**
   - El toast debe mostrar: "Pedido #1 creado exitosamente"
   - El monitor (si está visible) se actualiza con el nuevo pedido
   - NO deberías necesitar recargar la página
   - La vista vuelve a la principal

### En Producción (Cloud)

1. Repite los pasos anteriores pero en la URL de producción
2. Abre DevTools (F12) → Console
3. Verifica que ves los mismos logs que en desarrollo
4. Si no aparece el pedido en el monitor:
   - Verifica que el monitor HTML esté correctamente renderizado
   - Revisa si hay errores JavaScript en Console
   - Comprueba que `ordersManager` está disponible en window

## Posibles Problemas y Soluciones

### Problema 1: "No hay data.order o ordersManager disponible"
**Causa**: El ordersManager no se inicializó correctamente
**Solución**: 
- Abre Console
- Escribe: `window.ordersManager`
- Deberías ver una instancia del OrdersManager
- Si ves `undefined`, revisa los logs de inicialización

### Problema 2: "Monitor actualizado pero no se ve"
**Causa**: El monitor HTML no está visible o tiene problemas de CSS
**Solución**:
- Verifica que la sección "En Preparación" existe en el HTML
- Abre DevTools (F12) → Elements
- Busca `#in-progress-orders-list-monitor`
- Verifica que es visible (no está en `display: none`)

### Problema 3: "Error al actualizar monitor: Cannot read property 'items'"
**Causa**: Los datos retornados no tienen la estructura esperada
**Solución**:
- En Console, copia la respuesta completa
- Verifica que `order.items` es un array
- Verifica que cada item tiene: `id`, `name`, `quantity`

### Problema 4: "El pedido aparece pero sin items"
**Causa**: La API `/restaurant/save_order/` no retorna los items correctamente
**Solución**:
- Revisa que el backend obtiene correctamente los items en la transacción
- Ejecuta: `python manage.py shell`
- Verifica: `Order.objects.latest('id').orderitem_set.all()`

## Debugging en DevTools

### Para ver la respuesta completa:
```javascript
// En Console
const response = await fetch('/restaurant/save_order/', {
  method: 'POST',
  headers: {'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken()},
  body: JSON.stringify({
    items: [{id: 1, quantity: 2, note: ''}],
    client_identifier: 'Test',
    room_number: '101',
    tip_amount: 0
  })
});
const data = await response.json();
console.log(JSON.stringify(data, null, 2));
```

### Para verificar que ordersManager existe:
```javascript
// En Console
window.ordersManager?.handleOrderUpdate({
  id: 999,
  identifier: 'Test Order',
  status: 'pending',
  status_display: 'Pendiente',
  status_class: 'bg-yellow-100 text-yellow-800',
  items: [{id: 1, name: 'Test Item', quantity: 1, note: ''}],
  total: 10.00
});
```

## Flujo Completo Esperado

```
1. Usuario crea pedido
   ↓
2. POST /restaurant/save_order/ ← Backend
   ↓
3. Backend retorna order completo (con items, status, etc.)
   ↓
4. Frontend parsea respuesta JSON
   ↓
5. Llama ordersManager.handleOrderUpdate(order)
   ↓
6. Monitor se actualiza localmente CON el nuevo pedido ✅
   ↓
7. Toast muestra "Pedido #X creado exitosamente"
   ↓
8. Backend envía evento vía Pusher: 'nuevo-pedido'
   ↓
9. Otros usuarios ven el pedido en tiempo real (redundancia)
```

## Notas Importantes

- ✅ La actualización DEBE ser automática sin recargar
- ✅ No debe aparecer "Cargando..." ni spinner indefinido
- ✅ El pedido debe aparecer en la sección "En Preparación"
- ✅ Todos los campos (ID, Total, Items) deben ser correctos
- ✅ El estado debe ser "Pendiente" inicialmente
- ✅ Funciona tanto en desarrollo como en producción

## Si aún no funciona:

1. Limpia el caché del navegador (Ctrl+Shift+Delete)
2. Recarga la página (Ctrl+F5)
3. Abre DevTools (F12) y deja la Console abierta
4. Crea un pedido de prueba
5. Comparte todos los mensajes que aparezcan en la Console
