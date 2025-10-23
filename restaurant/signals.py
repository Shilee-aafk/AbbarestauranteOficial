from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from .models import Order, MenuItem, Reservation, Group, RegistrationPin
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
    # total = float(sum(item.menu_item.price * item.quantity for item in order_items)) # No longer needed, use instance.total_amount
    items_payload = [{
        'name': item.menu_item.name,
        'quantity': item.quantity,
        'note': item.note
    } for item in order_items]

    # --- 2. Lógica de Notificaciones ---
    kitchen_payload = {
        'type': 'order_update',
        'order': {
            'id': instance.id,
            'status': instance.status,
            'identifier': instance.room_number or instance.client_identifier,
            'user_username': instance.user.username,
            'created_at': instance.created_at.isoformat(),
            'total': float(instance.total_amount), # Usar el nuevo campo total_amount
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
            'identifier': instance.room_number or instance.client_identifier, # No need to change, total is not here
            'total': float(instance.total_amount), # Usar el nuevo campo total_amount
            'items': items_payload,
        }
    }

    async_to_sync(channel_layer.group_send)('waiters', {'type': 'order_update', 'message': waiter_payload})
    
    if instance.status == 'charged_to_room':
        receptionist_payload = {
            'type': 'room_charge_update',
            'order': waiter_payload['order'] 
        }
        async_to_sync(channel_layer.group_send)('receptionists', {'type': 'receptionist_message', 'message': receptionist_payload})

    
    async_to_sync(channel_layer.group_send)('receptionists', {'type': 'order_update', 'message': waiter_payload})

    
    admin_payload = waiter_payload.copy()
    admin_payload['order']['user_username'] = instance.user.username
    admin_payload['order']['created_at'] = instance.created_at.isoformat()

    
    today = timezone.now().date()
    stats_and_sales = Order.objects.aggregate(
        total_today=Count('id', filter=Q(created_at__date=today)),
        preparing=Count('id', filter=Q(status='preparing')),
        ready=Count('id', filter=Q(status='ready')),
        completed=Count('id', filter=Q(status__in=['served', 'paid'])),
        total_sales_today=models.Sum( # Usar el nuevo campo total_amount
            'total_amount',
            filter=models.Q(status='paid', created_at__date=today),
            output_field=models.DecimalField()
        ) or decimal.Decimal(0)
    )
    admin_payload['stats'] = {k: v if v is not None else 0 for k, v in stats_and_sales.items()}


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


@receiver(post_save, sender=Reservation)
def reservation_notification(sender, instance, created, **kwargs):
    if created:
        # Payload for admin/receptionist
        admin_payload = {
            'type': 'reservation_update',
            'reservation': {
                'id': instance.id,
                'user': instance.user.username,
                'client_name': instance.client_name,
                'guests': instance.guests,
                'date': instance.date.isoformat(),
                'time': instance.time.strftime('%H:%M'),
            }
        }
        async_to_sync(channel_layer.group_send)('admin', {'type': 'admin_update', 'message': admin_payload})
