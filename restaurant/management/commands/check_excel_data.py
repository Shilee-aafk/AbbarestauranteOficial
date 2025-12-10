from django.core.management.base import BaseCommand
from restaurant.models import Order
from datetime import datetime

class Command(BaseCommand):
    help = 'Verificar órdenes para el excel'

    def handle(self, *args, **options):
        all_orders = Order.objects.all()
        self.stdout.write(f"Total órdenes en BD: {all_orders.count()}")
        
        for order in all_orders.order_by('-id')[:10]:
            self.stdout.write(f"ID: {order.id}, Estado: {order.status}, Total: {order.total_amount}, Método: {order.get_payment_method_display()}")
