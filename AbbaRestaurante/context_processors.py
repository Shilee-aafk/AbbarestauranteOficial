from django.conf import settings

def export_settings(request):
    # Usamos getattr para proporcionar un valor por defecto si el setting no existe.
    # Esto hace que el procesador sea más robusto ante errores de configuración.
    return {
        'PUSHER_KEY': getattr(settings, 'PUSHER_KEY', ''),
        'PUSHER_CLUSTER': getattr(settings, 'PUSHER_CLUSTER', ''),
    }