from django.core.management.base import BaseCommand
from restaurant.models import Order
from datetime import datetime, timedelta
from django.db.models import Sum, Count, Q
from django.utils import timezone

class Command(BaseCommand):
    help = 'Test del reporte de métodos de pago'

    def handle(self, *args, **options):
        from datetime import date
        import decimal
        
        today = timezone.now().date()
        month_start = today.replace(day=1)
        
        if today.month == 12:
            month_end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        
        # Convert dates to timezone-aware datetimes
        month_start_dt = timezone.make_aware(datetime.combine(month_start, datetime.min.time()))
        month_end_dt = timezone.make_aware(datetime.combine(month_end, datetime.max.time()))
        
        self.stdout.write(f"Filtrando desde: {month_start_dt}")
        self.stdout.write(f"Filtrando hasta: {month_end_dt}\n")
        
        # Filter orders
        orders = Order.objects.filter(
            Q(status='paid') | Q(status='charged_to_room'),
            created_at__gte=month_start_dt,
            created_at__lte=month_end_dt
        )
        
        self.stdout.write(f"✓ Total órdenes: {orders.count()}")
        
        # Payment methods summary
        payment_stats = orders.values('payment_method').annotate(
            count=Count('id'),
            total_sales=Sum('total_amount'),
            total_tips=Sum('tip_amount')
        ).order_by('-total_sales')
        
        grand_total = decimal.Decimal('0.00')
        grand_tips = decimal.Decimal('0.00')
        
        self.stdout.write("\n=== Métodos de Pago ===")
        for stat in payment_stats:
            method = stat['payment_method']
            count = stat['count']
            total = stat['total_sales'] or decimal.Decimal('0.00')
            tips = stat['total_tips'] or decimal.Decimal('0.00')
            
            grand_total += total
            grand_tips += tips
            
            self.stdout.write(f"{method}: {count} órdenes, ${total}, propinas ${tips}")
        
        self.stdout.write(f"\n=== Totales ===")
        self.stdout.write(f"Ventas totales: ${grand_total}")
        self.stdout.write(f"Propinas totales: ${grand_tips}")
        self.stdout.write(f"Promedio orden: ${grand_total / orders.count() if orders.count() > 0 else 0}")
