"""
ASGI config for AbbaRestaurante project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

# Unset PYTHONHOME to avoid conflicts in containerized environments like Koyeb
os.environ.pop('PYTHONHOME', None)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AbbaRestaurante.settings')

# La importación de get_asgi_application() debe hacerse ANTES de django.setup()
http_application = get_asgi_application()

# Ahora, después de obtener la aplicación http, importamos el enrutamiento de channels
import restaurant.routing # noqa

application = ProtocolTypeRouter({
    'http': http_application,
    'websocket': AuthMiddlewareStack(
        URLRouter(
            restaurant.routing.websocket_urlpatterns
        )
    ),
})
