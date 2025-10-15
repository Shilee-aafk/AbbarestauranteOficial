from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, MenuItem, Table, Reservation
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

channel_layer = get_channel_layer()

@receiver(post_save, sender=Order)
def order_notification(sender, instance, created, **kwargs):
    from django.utils import timezone
    # Payload for kitchen
    order_items = instance.orderitem_set.all()
    total = float(sum(item.menu_item.price * item.quantity for item in order_items))
    items_payload = [{
        'name': item.menu_item.name,
        'quantity': item.quantity,
        'note': item.note
    } for item in order_items]

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
            'type': 'order_message',
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
    admin_payload = {
        'type': 'order_update',
        'order': {
            'id': instance.id,
            'status': instance.status,
            'status_display': instance.get_status_display(),
            'status_class': instance.status_class,
            'table_id': instance.table.id,
            'table_number': instance.table.number,
            'user_username': instance.user.username,
            'created_at': instance.created_at.isoformat(),
            'total': total,
            'items': items_payload,
        }
    }
    # Add overall stats and table status to the admin payload
    admin_payload['stats'] = {
        'total_orders_today': Order.objects.filter(created_at__date=timezone.now().date()).count(),
        'preparing_count': Order.objects.filter(status='preparing').count(),
        'ready_count': Order.objects.filter(status='ready').count(),
        'completed_count': Order.objects.filter(status__in=['served', 'paid']).count(),
    }
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
