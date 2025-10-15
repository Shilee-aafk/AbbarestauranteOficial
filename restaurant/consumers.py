import json
from channels.generic.websocket import AsyncWebsocketConsumer

class CookConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'cocina'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def order_message(self, event):
        await self.send(text_data=json.dumps(event['message']))

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
        await self.send(text_data=json.dumps(event['message'])) # event['message'] is the full payload

class ProductConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'productos'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def product_message(self, event):
        await self.send(text_data=json.dumps(event['message']))

class AdminConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'admin'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def admin_update(self, event):
        await self.send(text_data=json.dumps(event['message']))

class ReceptionistConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'receptionists'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def order_update(self, event):
        await self.send(text_data=json.dumps(event['message']))
