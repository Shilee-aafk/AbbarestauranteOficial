# Optimizaciones de Performance - QuerySet Optimization

## Cambios Realizados

### 1. API Orders Report (`api_orders_report`)
**Antes:**
```python
orders = Order.objects.all()
```

**Después:**
```python
orders = Order.objects.select_related('user').all()
```

**Impacto:** Reduce N+1 queries al obtener datos del usuario para cada pedido

### 2. Admin Dashboard (`admin_dashboard`)
**Antes:**
```python
orders = Order.objects.all()
```

**Después:**
```python
orders = Order.objects.select_related('user').all()
```

**Impacto:** Evita queries adicionales cuando se accede a datos del usuario

### 3. Waiter Order Detail (`api_waiter_order_detail`)
**Antes:**
```python
order = Order.objects.get(pk=pk)
# Luego acceder a order.orderitem_set.all() causa N+1 queries
for item in order.orderitem_set.all():
    # Acceder a item.menu_item causa query adicional por cada item
```

**Después:**
```python
order = Order.objects.prefetch_related('orderitem_set__menu_item').get(pk=pk)
```

**Impacto:** Reduce 1 + N queries a solo 3 queries (1 para order, 1 para orderitem_set, 1 para menu_item)

### 4. Create Order (`api_create_order`)
**Antes:**
```python
order = Order.objects.create(...)
items_list = order.orderitem_set.all()
for item in items_list:
    # Cada acceso a item.menu_item es una query
```

**Después:**
```python
order = Order.objects.prefetch_related('orderitem_set__menu_item').get(pk=order.id)
items_list = order.orderitem_set.all()
```

**Impacto:** Reduce N queries a solo 2 queries para obtener los items con sus detalles

## Queries Optimizadas por Vista

✅ **Cook Dashboard** - Ya estaba optimizado con `prefetch_related`
✅ **Waiter Dashboard** - Ya estaba optimizado con `prefetch_related`
✅ **Admin Dashboard** - Optimizado con `select_related`
✅ **Receptionist Dashboard** - Ya estaba optimizado
✅ **API Reports** - Optimizado con `select_related`
✅ **API Waiter Order Detail** - Optimizado con `prefetch_related`
✅ **API Create Order** - Optimizado con `prefetch_related`

## Resultados Esperados

- **Antes:** Consultas pueden oscilar entre 10-30 queries por página
- **Después:** Reducido a 3-8 queries por página
- **Mejora:** 60-75% menos queries a la base de datos
- **Impacto en UX:** Carga más rápida, especialmente en conexiones lentas

## Mejores Prácticas Implementadas

1. **select_related()** - Usado para relaciones ForeignKey (1-to-N)
   - Ejemplo: Order → User
   - Usa INNER JOIN en SQL

2. **prefetch_related()** - Usado para relaciones ManyToMany y reverse ForeignKey
   - Ejemplo: Order → OrderItem → MenuItem
   - Hace queries separadas pero las optimiza en Python

3. **Validación de Nulidad** - Antes de acceder a relaciones
   ```python
   if item.menu_item:  # Validar que menu_item no sea nulo
       # procesar
   ```

## Monitoreo

Para monitorear queries en desarrollo:

```python
from django.db import connection
from django.test.utils import CaptureQueriesContext

# En una vista
with CaptureQueriesContext(connection) as context:
    # Tu código
    pass

print(f"Queries executed: {len(context)}")
for query in context:
    print(query['sql'])
```

## Recursos Adicionales

- Django QuerySet API Reference: https://docs.djangoproject.com/en/5.2/ref/models/querysets/
- Database access optimization: https://docs.djangoproject.com/en/5.2/topics/db/optimization/
