from django.core.management.base import BaseCommand
from restaurant.models import Order
from datetime import date, datetime, timedelta
from django.utils import timezone
from django.db.models import Q

class Command(BaseCommand):
    help = 'Debug de filtrado de órdenes'

    def handle(self, *args, **options):
        self.stdout.write("=== DEBUG ÓRDENES ===\n")
        
        # Get one order to examine
        order = Order.objects.latest('id')
        self.stdout.write(f"Última orden ID: {order.id}")
        self.stdout.write(f"  created_at (raw): {order.created_at}")
        self.stdout.write(f"  created_at tzinfo: {order.created_at.tzinfo}")
        self.stdout.write(f"  created_at.date(): {order.created_at.date()}")
        
        # Get current date in Santiago
        today_santiago = timezone.now().date()
        self.stdout.write(f"\nFecha actual (Santiago): {today_santiago}")
        
        month_start = today_santiago.replace(day=1)
        self.stdout.write(f"Inicio de mes: {month_start}")
        
        # Create datetimes with timezone
        month_start_dt = timezone.make_aware(datetime.combine(month_start, datetime.min.time()))
        self.stdout.write(f"\nMonth start datetime (aware): {month_start_dt}")
        self.stdout.write(f"  tzinfo: {month_start_dt.tzinfo}")
        
        # Test direct comparison
        self.stdout.write(f"\nComparación order.created_at >= month_start_dt:")
        self.stdout.write(f"  {order.created_at} >= {month_start_dt}")
        self.stdout.write(f"  Resultado: {order.created_at >= month_start_dt}")
        
        # Test filter with datetime
        self.stdout.write(f"\n--- Testing filter with datetime ---")
        orders_gte = Order.objects.filter(created_at__gte=month_start_dt)
        self.stdout.write(f"Filter (created_at__gte=month_start_dt): {orders_gte.count()} órdenes")
        
        # Test filter with date only
        self.stdout.write(f"\n--- Testing filter with date ---")
        orders_date = Order.objects.filter(created_at__date__gte=month_start)
        self.stdout.write(f"Filter (created_at__date__gte=month_start): {orders_date.count()} órdenes")
        
        # Test filter with Q
        self.stdout.write(f"\n--- Testing filter with Q ---")
        orders_q = Order.objects.filter(
            Q(status='paid') | Q(status='charged_to_room'),
            created_at__gte=month_start_dt
        )
        self.stdout.write(f"Filter (status + created_at__gte): {orders_q.count()} órdenes")
        
        # Show all orders and their status
        self.stdout.write(f"\n--- All orders ---")
        for o in Order.objects.all().order_by('-id')[:5]:
            self.stdout.write(f"ID: {o.id}, status: {o.status}, created_at: {o.created_at}")
