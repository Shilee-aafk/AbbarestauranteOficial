from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, MenuItem
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

channel_layer = get_channel_layer()

@receiver(post_save, sender=Order)
def order_notification(sender, instance, created, **kwargs):
    # Payload for kitchen
    kitchen_payload = {
        'action': 'created' if created else 'updated',
        'order': {
            'id': instance.id,
            'status': instance.status,
            'table': instance.table.id if instance.table else None,
            'total': float(sum(item.menu_item.price * item.quantity for item in instance.orderitem_set.all())),
        },
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
        'action': 'created' if created else 'updated',
        'order': {
            'id': instance.id,
            'status': instance.status,
            'status_display': instance.get_status_display(),
            'table_id': instance.table.id,
            'table_number': instance.table.number,
        }
    }
    # Send to waiters group
    async_to_sync(channel_layer.group_send)('waiters', {'type': 'order.update', 'message': waiter_payload})

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
