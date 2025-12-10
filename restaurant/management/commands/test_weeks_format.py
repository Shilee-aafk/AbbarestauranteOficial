from django.core.management.base import BaseCommand
from restaurant.models import Order
from datetime import datetime, date, timedelta
from django.db.models import Sum, Count, Q
from django.utils import timezone
import decimal

class Command(BaseCommand):
    help = 'Test del formato de semanas'

    def handle(self, *args, **options):
        today = timezone.now().date()
        month_start = today.replace(day=1)
        
        if today.month == 12:
            month_end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        
        # Convert dates to timezone-aware datetimes
        month_start_dt = timezone.make_aware(datetime.combine(month_start, datetime.min.time()))
        month_end_dt = timezone.make_aware(datetime.combine(month_end, datetime.max.time()))
        
        orders = Order.objects.filter(
            Q(status='paid') | Q(status='charged_to_room'),
            created_at__gte=month_start_dt,
            created_at__lte=month_end_dt
        )
        
        # === WEEKLY BREAKDOWN ===
        weekly_stats = {}
        for order in orders:
            year, week_num, weekday = order.created_at.isocalendar()
            week_key = f"W{week_num}"
            
            if week_key not in weekly_stats:
                # Calculate week start (Monday) and end (Sunday)
                order_date = order.created_at.date()
                week_start = order_date - timedelta(days=weekday - 1)
                week_end = week_start + timedelta(days=6)
                
                weekly_stats[week_key] = {
                    'week_num': week_num,
                    'week_start': week_start,
                    'week_end': week_end,
                    'count': 0,
                    'total': decimal.Decimal('0.00'),
                    'total_tips': decimal.Decimal('0.00')
                }
            
            weekly_stats[week_key]['count'] += 1
            weekly_stats[week_key]['total'] += order.total_amount or decimal.Decimal('0.00')
            weekly_stats[week_key]['total_tips'] += order.tip_amount or decimal.Decimal('0.00')
        
        weekly_data = []
        for week_key in sorted(weekly_stats.keys()):
            stat = weekly_stats[week_key]
            # Format as "8-14 Dic" or similar
            start_date = stat['week_start'].strftime('%d')
            end_date = stat['week_end'].strftime('%d %b').lower()
            week_label = f"{start_date}-{end_date}"
            
            weekly_data.append({
                'week': week_label,
                'week_num': stat['week_num'],
                'week_start': str(stat['week_start']),
                'week_end': str(stat['week_end']),
                'count': stat['count'],
                'total': float(stat['total']),
                'total_tips': float(stat['total_tips']),
                'average': float(stat['total'] / stat['count']) if stat['count'] > 0 else 0
            })
        
        self.stdout.write("=== Formato de Semanas ===")
        for week in weekly_data:
            self.stdout.write(f"Semana: {week['week']}, Órdenes: {week['count']}, Total: ${week['total']}")
