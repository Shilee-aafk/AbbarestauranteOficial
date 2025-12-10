import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AbbaRestaurante.settings')
django.setup()

from restaurant.models import Order
from django.utils import timezone
from decimal import Decimal

# Create test orders with different payment methods
payment_methods = ['cash', 'card', 'transfer', 'check', 'mixed']

print("Creando órdenes de prueba...\n")

for i, method in enumerate(payment_methods):
    order = Order.objects.create(
        room_number=f"Habitación {i+1}",
        total_amount=Decimal(str(50 + i*10)),
        tip_amount=Decimal(str(5 + i*2)),
        payment_method=method,
        status='paid'
    )
    print(f"✓ Orden {order.id}: Método={method}, Total=${order.total_amount}, Propina=${order.tip_amount}")

# Create a couple more orders
for i in range(2):
    order = Order.objects.create(
        room_number=f"Suite {i+1}",
        total_amount=Decimal('75.50'),
        tip_amount=Decimal('7.50'),
        payment_method='card',
        status='paid'
    )
    print(f"✓ Orden {order.id}: Método=card, Total=${order.total_amount}, Propina=${order.tip_amount}")

print("\n✅ Órdenes de prueba creadas exitosamente")
print(f"Hora actual (Santiago): {timezone.now()}")

# Check what orders are in the current month
from datetime import date
today = date.today()
month_start = today.replace(day=1)

orders_this_month = Order.objects.filter(
    created_at__date__gte=month_start
)
print(f"\nÓrdenes en diciembre 2025: {orders_this_month.count()}")
