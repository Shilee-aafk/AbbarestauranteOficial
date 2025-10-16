from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/cook-updates/$', consumers.CookConsumer.as_asgi()),
    re_path(r'ws/productos/$', consumers.ProductConsumer.as_asgi()),
    re_path(r'ws/waiter-updates/$', consumers.WaiterConsumer.as_asgi()),
    re_path(r'ws/admin-updates/$', consumers.AdminConsumer.as_asgi()),
    re_path(r'ws/receptionist-updates/$', consumers.ReceptionistConsumer.as_asgi()),
]
