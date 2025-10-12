from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/pedidos/cocina/$', consumers.OrderConsumer.as_asgi()),
    re_path(r'ws/productos/$', consumers.ProductConsumer.as_asgi()),
]
