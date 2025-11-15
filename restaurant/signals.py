import pusher
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, MenuItem

# --- Configuración del Cliente Pusher ---
pusher_client = None
if all([settings.PUSHER_APP_ID, settings.PUSHER_KEY, settings.PUSHER_SECRET, settings.PUSHER_CLUSTER]):
    pusher_client = pusher.Pusher(
        app_id=settings.PUSHER_APP_ID,
        key=settings.PUSHER_KEY,
        secret=settings.PUSHER_SECRET,
        cluster=settings.PUSHER_CLUSTER,
        ssl=True
    )

# --- Señales para Pedidos (Order) ---
@receiver(post_save, sender=Order)
def order_status_changed(sender, instance, created, **kwargs):
    """
    Cuando un pedido (Order) se crea o actualiza, envía notificaciones
    a los canales apropiados según el rol y el estado.
    """
    if not pusher_client:
        return

    order_data = {
        'id': instance.id,
        'client_identifier': instance.client_identifier,
        'status': instance.status,
        'status_display': instance.get_status_display(),
        'status_class': instance.status_class,
        'created_at': instance.created_at.isoformat(),
        'user_id': instance.user.id, # ID del garzón que creó el pedido
        'room_number': instance.room_number, # Número de habitación para recepción
        'total': float(instance.total_amount) if instance.total_amount else 0, # Total del pedido para actualizaciones de ventas
    }

    if created:
        # 1. Notificar a COCINA y ADMIN sobre un NUEVO pedido
        pusher_client.trigger(['cocina-channel', 'admin-channel'], 'nuevo-pedido', {
            'message': f"Nuevo pedido de: {order_data['client_identifier']}",
            'order': order_data
        })
    else:
        # Si un pedido existente cambia de estado, notificar a los canales relevantes.
        
        # 2. Notificar a TODOS los roles sobre una actualización general.
        #    Esto es útil para el admin y para mantener la consistencia.
        pusher_client.trigger(['cocina-channel', 'garzon-channel', 'admin-channel'], 'actualizacion-estado', {
            'order': order_data
        })

        # 3. Notificaciones ESPECÍFICAS por estado:
        if instance.status == 'ready':
            # Notificar a GARZONES y ADMIN que un pedido está LISTO para recoger.
            pusher_client.trigger(['garzon-channel', 'admin-channel'], 'pedido-listo', {
                'message': f"¡El pedido para '{instance.client_identifier}' está listo!",
                'order': order_data
            })

        if instance.status == 'charged_to_room':
            # Notificar a RECEPCIÓN y ADMIN que un pedido se cargó a una habitación.
            pusher_client.trigger(['recepcion-channel', 'admin-channel'], 'cargo-habitacion', {
                'message': f"Se cargó un pedido a la habitación {instance.room_number}",
                'order': order_data
            })

        if instance.status == 'paid':
            # Notificar a RECEPCIÓN y ADMIN que un pedido fue pagado.
            pusher_client.trigger(['recepcion-channel', 'admin-channel'], 'pedido-pagado', {
                'message': f"Pedido pagado: {order_data['client_identifier']}",
                'order': order_data
            })

# --- Señales para Items del Menú (MenuItem) ---
@receiver(post_save, sender=MenuItem)
def menu_item_changed(sender, instance, **kwargs):
    """
    Cuando la disponibilidad de un item del menú cambia, notifica a todos.
    """
    if not pusher_client:
        return

    # Notifica a los garzones y al admin sobre el cambio de disponibilidad.
    pusher_client.trigger(['garzon-channel', 'admin-channel'], 'item-disponibilidad', {
        'item_id': instance.id,
        'name': instance.name,
        'available': instance.available
    })