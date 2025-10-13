import json
from channels.generic.websocket import AsyncWebsocketConsumer

class OrderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'cocina'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def order_message(self, event):
        await self.send(text_data=json.dumps(event['message']))

class WaiterConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'waiters'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def order_update(self, event):
        await self.send(text_data=json.dumps(event['message']))


class ProductConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'productos'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def product_message(self, event):
        await self.send(text_data=json.dumps(event['message']))
