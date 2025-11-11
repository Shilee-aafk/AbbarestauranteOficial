from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/cook/$', consumers.CookConsumer.as_asgi()),
    re_path(r'ws/waiter/$', consumers.WaiterConsumer.as_asgi()),
    re_path(r'ws/admin/$', consumers.AdminConsumer.as_asgi()),
    re_path(r'ws/receptionist/$', consumers.ReceptionistConsumer.as_asgi()),
    # La ruta de productos no parece usarse, la comentamos para simplificar
    # re_path(r'ws/productos/$', consumers.ProductConsumer.as_asgi()),
]
