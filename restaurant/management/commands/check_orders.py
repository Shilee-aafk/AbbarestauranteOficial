from django.core.management.base import BaseCommand
from restaurant.models import Order
from datetime import date
from django.utils import timezone

class Command(BaseCommand):
    help = 'Verifica órdenes y su fecha'

    def handle(self, *args, **options):
        self.stdout.write("Órdenes creadas recientemente:\n")
        for order in Order.objects.all().order_by('-id')[:10]:
            self.stdout.write(f"ID: {order.id}, created_at UTC: {order.created_at}, date: {order.created_at.date()}")

        today = date.today()
        self.stdout.write(f"\nHoy (date.today()): {today}")

        month_start = today.replace(day=1)
        self.stdout.write(f"Inicio de mes: {month_start}")

        # Test the filter
        orders = Order.objects.filter(created_at__date__gte=month_start)
        self.stdout.write(f"\nÓrdenes filtradas (created_at__date__gte={month_start}): {orders.count()}")
        
        # Try with timezone-aware date
        from django.utils import timezone
        now_santiago = timezone.now()
        today_santiago = now_santiago.date()
        self.stdout.write(f"\nAhora en Santiago: {now_santiago}")
        self.stdout.write(f"Hoy en Santiago: {today_santiago}")
        
        month_start_santiago = today_santiago.replace(day=1)
        orders_tz = Order.objects.filter(created_at__date__gte=month_start_santiago)
        self.stdout.write(f"Órdenes filtradas con fecha Santiago: {orders_tz.count()}")
