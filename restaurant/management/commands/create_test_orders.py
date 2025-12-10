from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from restaurant.models import Order
from decimal import Decimal
from django.utils import timezone

class Command(BaseCommand):
    help = 'Crea órdenes de prueba con diferentes métodos de pago'

    def handle(self, *args, **options):
        # Get or create a user for the orders
        user, created = User.objects.get_or_create(
            username='test_waiter',
            defaults={'first_name': 'Test', 'last_name': 'Waiter'}
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f"Usuario creado: {user.username}"))
        else:
            self.stdout.write(f"Usando usuario existente: {user.username}")
        
        # Create test orders with different payment methods
        payment_methods = ['cash', 'card', 'transfer', 'check', 'mixed']

        self.stdout.write(self.style.SUCCESS("\nCreando órdenes de prueba...\n"))

        for i, method in enumerate(payment_methods):
            order = Order.objects.create(
                user=user,
                room_number=str(100 + i),
                total_amount=Decimal(str(50 + i*10)),
                tip_amount=Decimal(str(5 + i*2)),
                payment_method=method,
                status='paid'
            )
            self.stdout.write(f"✓ Orden {order.id}: Método={method}, Total=${order.total_amount}, Propina=${order.tip_amount}")

        # Create a couple more orders
        for i in range(2):
            order = Order.objects.create(
                user=user,
                room_number=str(200 + i),
                total_amount=Decimal('75.50'),
                tip_amount=Decimal('7.50'),
                payment_method='card',
                status='paid'
            )
            self.stdout.write(f"✓ Orden {order.id}: Método=card, Total=${order.total_amount}, Propina=${order.tip_amount}")

        self.stdout.write(self.style.SUCCESS("\n✅ Órdenes de prueba creadas exitosamente"))
        self.stdout.write(f"Hora actual (Santiago): {timezone.now()}")

        # Check what orders are in the current month
        from datetime import date
        today = date.today()
        month_start = today.replace(day=1)

        orders_this_month = Order.objects.filter(
            created_at__date__gte=month_start
        )
        self.stdout.write(self.style.SUCCESS(f"\n✓ Órdenes en diciembre 2025: {orders_this_month.count()}"))
