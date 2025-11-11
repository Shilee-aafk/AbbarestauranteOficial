from django.conf import settings

def export_settings(request):
    return {
        'PUSHER_KEY': settings.PUSHER_KEY,
        'PUSHER_CLUSTER': settings.PUSHER_CLUSTER,
    }