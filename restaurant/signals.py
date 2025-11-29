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

    # Obtener items del pedido
    items = []
    for item in instance.orderitem_set.all():
        items.append({
            'name': item.menu_item.name,
            'quantity': item.quantity,
            'note': item.note or '',
            'is_prepared': item.is_prepared,
        })

    order_data = {
        'id': instance.id,
        'client_identifier': instance.client_identifier,
        'identifier': instance.room_number or instance.client_identifier,
        'status': instance.status,
        'status_display': instance.get_status_display(),
        'status_class': instance.status_class,
        'created_at': instance.created_at.isoformat(),
        'user_id': instance.user.id,
        'room_number': instance.room_number,
        'total': float(instance.total_amount) if instance.total_amount else 0,
        'items': items,  # AGREGADO: Items del pedido para cocina
    }

    if created:
        # 1. Notificar a COCINA, ADMIN y GARZON sobre un NUEVO pedido
        try:
            print(f"[PUSHER] Enviando nuevo-pedido #{instance.id} a cocina-channel, admin-channel y garzon-channel")
            pusher_client.trigger(['cocina-channel', 'admin-channel', 'garzon-channel'], 'nuevo-pedido', {
                'message': f"Nuevo pedido de: {order_data['client_identifier']}",
                'order': order_data
            })
        except Exception as e:
            print(f"Error sending nuevo-pedido notification: {str(e)}")
    else:
        # Para órdenes existentes, SOLO notificar si update_fields está vacío o contiene 'status'
        # Esto evita notificaciones cuando solo se actualiza total_amount
        update_fields = kwargs.get('update_fields')
        
        # Si update_fields es None (guardado completo) o contiene 'status', enviar notificación
        if update_fields is None or 'status' in update_fields:
            try:
                # 3. Notificaciones ESPECÍFICAS por estado (tienen prioridad):
                if instance.status == 'ready':
                    # Solo enviar pedido-listo, sin actualizacion-estado redundante
                    pusher_client.trigger(['garzon-channel'], 'pedido-listo', {
                        'message': f"¡El pedido para '{instance.client_identifier}' está listo!",
                        'order': order_data
                    })

                elif instance.status == 'charged_to_room':
                    # Notificar a recepción que se cargó a habitación
                    pusher_client.trigger(['recepcion-channel'], 'cargo-habitacion', {
                        'message': f"Se cargó un pedido a la habitación {instance.room_number}",
                        'order': order_data
                    })

                elif instance.status == 'paid':
                    # Notificar a recepción que se pagó
                    pusher_client.trigger(['recepcion-channel'], 'pedido-pagado', {
                        'message': f"Pedido pagado: {order_data['client_identifier']}",
                        'order': order_data
                    })
                
                else:
                    # Para otros estados (pending, preparing, cancelled), enviar actualizacion-estado
                    pusher_client.trigger(['cocina-channel', 'garzon-channel'], 'actualizacion-estado', {
                        'order': order_data
                    })
            except Exception as e:
                print(f"Error sending status update notification: {str(e)}")

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