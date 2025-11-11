import pusher
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order  # Asegúrate de que el modelo se llame 'Order'

# Inicializa el cliente de Pusher una sola vez
pusher_client = None
if all([settings.PUSHER_APP_ID, settings.PUSHER_KEY, settings.PUSHER_SECRET, settings.PUSHER_CLUSTER]):
    pusher_client = pusher.Pusher(
        app_id=settings.PUSHER_APP_ID,
        key=settings.PUSHER_KEY,
        secret=settings.PUSHER_SECRET,
        cluster=settings.PUSHER_CLUSTER,
        ssl=True
    )

@receiver(post_save, sender=Order)
def notify_new_order(sender, instance, created, **kwargs):
    """
    Cuando se crea un nuevo pedido (Order), envía una notificación a Pusher.
    """
    if created and pusher_client:
        # Serializa los datos del pedido que quieres enviar
        order_data = {
            'id': instance.id,
            'client_identifier': instance.client_identifier,
            'status': instance.status,
            'created_at': instance.created_at.isoformat(),
        }

        # Dispara el evento en el canal 'cocina-channel'
        pusher_client.trigger('cocina-channel', 'nuevo-pedido', {
            'message': f"Nuevo pedido de: {order_data['client_identifier']}",
            'order': order_data
        })