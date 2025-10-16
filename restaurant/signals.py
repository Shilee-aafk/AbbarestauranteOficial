from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from .models import Order, MenuItem, Table, Reservation, Ingredient, RecipeIngredient
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction, models
from django.db.models import Count, Q

channel_layer = get_channel_layer()

@receiver(pre_save, sender=Order)
def store_previous_order_status(sender, instance, **kwargs):
    """
    Antes de guardar una orden, almacena su estado anterior en el objeto
    para poder compararlo después de que se guarde.
    """
    if instance.pk:
        try:
            instance._previous_status = Order.objects.get(pk=instance.pk).status
        except Order.DoesNotExist:
            instance._previous_status = None

@receiver(post_save, sender=Order)
def order_post_save_handler(sender, instance, created, **kwargs):
    """
    Manejador unificado que se ejecuta después de guardar una orden.
    1. Descuenta el inventario si el pedido se marca como 'paid'.
    2. Envía notificaciones a los diferentes canales (cocina, garzones, admin).
    """
    from django.utils import timezone

    # Payload for kitchen
    order_items = instance.orderitem_set.all()
    total = float(sum(item.menu_item.price * item.quantity for item in order_items))
    items_payload = [{
        'name': item.menu_item.name,
        'quantity': item.quantity,
        'note': item.note
    } for item in order_items]

    # --- 1. Lógica de Descuento de Inventario ---
    # Se ejecuta solo si el estado ha cambiado a 'paid' desde otro estado.
    if not created and instance.status == 'paid' and getattr(instance, '_previous_status', None) != 'paid':
        with transaction.atomic():
            for order_item in instance.orderitem_set.select_related('menu_item'):
                recipe_items = RecipeIngredient.objects.filter(menu_item=order_item.menu_item).select_related('ingredient')
                for recipe_item in recipe_items:
                    ingredient = recipe_item.ingredient
                    quantity_to_deduct = recipe_item.quantity_required * order_item.quantity
                    Ingredient.objects.filter(id=ingredient.id).update(stock_quantity=models.F('stock_quantity') - quantity_to_deduct)

    # --- 2. Lógica de Notificaciones ---
    kitchen_payload = {
        'type': 'order_update',
        'order': {
            'id': instance.id,
            'status': instance.status,
            'table_number': instance.table.number if instance.table else 'N/A',
            'user_username': instance.user.username,
            'created_at': instance.created_at.isoformat(),
            'total': total,
            'items': items_payload,
        }
    }
    # Send to kitchen group
    async_to_sync(channel_layer.group_send)(
        'cocina',
        {
            'type': 'order_update', # Cambiado para coincidir con el handler del consumer
            'message': kitchen_payload,
        },
    )

    # Payload for waiters
    waiter_payload = {
        'type': 'order_update',
        'order': {
            'id': instance.id,
            'status': instance.status,
            'status_display': instance.get_status_display(),
            'status_class': instance.status_class,
            'table_id': instance.table.id,
            'table_number': instance.table.number,
            'total': total,
            'items': items_payload,
        }
    }
    # Send to waiters group
    async_to_sync(channel_layer.group_send)('waiters', {'type': 'order_update', 'message': waiter_payload})

    # Send to receptionists group (same payload as waiters is fine)
    async_to_sync(channel_layer.group_send)('receptionists', {'type': 'order_update', 'message': waiter_payload})

    # Payload for admin
    # Reutilizamos el payload de los garzones y le añadimos la información extra para el admin.
    admin_payload = waiter_payload.copy()
    admin_payload['order']['user_username'] = instance.user.username
    admin_payload['order']['created_at'] = instance.created_at.isoformat()

    # Add overall stats and table status to the admin payload
    stats = Order.objects.aggregate(
        total_today=Count('id', filter=Q(created_at__date=timezone.now().date())),
        preparing=Count('id', filter=Q(status='preparing')),
        ready=Count('id', filter=Q(status='ready')),
        completed=Count('id', filter=Q(status__in=['served', 'paid']))
    )
    admin_payload['stats'] = stats

    occupied_tables_ids = Order.objects.filter(
        status__in=['pending', 'preparing', 'ready', 'served']
    ).values_list('table_id', flat=True)
    admin_payload['table_status'] = [
        {'id': t.id, 'is_available': t.id not in occupied_tables_ids}
        for t in Table.objects.all()
    ]


    async_to_sync(channel_layer.group_send)('admin', {'type': 'admin_update', 'message': admin_payload})

@receiver(post_save, sender=MenuItem)
def product_notification(sender, instance, created, **kwargs):
    payload = {
        'action': 'created' if created else 'updated',
        'product': {
            'id': instance.id,
            'name': instance.name,
            'price': float(instance.price),
        },
    }
    async_to_sync(channel_layer.group_send)(
        'productos',
        {
            'type': 'product_message',
            'message': payload,
        },
    )

    # Payload for admin
    admin_payload = {
        'model': 'menu_item',
        'action': 'created' if created else 'updated',
        'data': {
            'id': instance.id,
            'name': instance.name,
            'description': instance.description,
            'price': float(instance.price),
            'category': instance.category,
            'available': instance.available
        }
    }
    async_to_sync(channel_layer.group_send)('admin', {'type': 'admin_update', 'message': admin_payload})

@receiver(post_save, sender=Ingredient)
def ingredient_stock_notification(sender, instance, created, **kwargs):
    """
    Envía una notificación al grupo de administradores si el stock de un ingrediente es bajo.
    También envía una actualización general del inventario.
    """
    # Notificación específica de stock bajo
    if instance.is_low_stock:
        low_stock_payload = {
            'type': 'inventory_alert',
            'ingredient': {
                'id': instance.id,
                'name': instance.name,
                'stock_quantity': float(instance.stock_quantity),
                'unit': instance.unit,
                'low_stock_threshold': float(instance.low_stock_threshold)
            }
        }
        async_to_sync(channel_layer.group_send)('admin', {'type': 'admin_update', 'message': low_stock_payload})


@receiver(post_save, sender=Reservation)
def reservation_notification(sender, instance, created, **kwargs):
    if created:
        # Payload for admin/receptionist
        admin_payload = {
            'type': 'reservation_update',
            'reservation': {
                'id': instance.id,
                'user': instance.user.username,
                'table': instance.table.number,
                'guests': instance.guests,
                'date': instance.date.isoformat(),
                'time': instance.time.strftime('%H:%M'),
            }
        }
        async_to_sync(channel_layer.group_send)('admin', {'type': 'admin_update', 'message': admin_payload})

@receiver(post_save, sender=Table)
def table_notification(sender, instance, created, **kwargs):
    # Payload for admin
    admin_payload = {
        'model': 'table',
        'action': 'created' if created else 'updated',
        'data': {
            'id': instance.id,
            'number': instance.number,
            'capacity': instance.capacity,
        }
    }
    async_to_sync(channel_layer.group_send)('admin', {'type': 'admin_update', 'message': admin_payload})
