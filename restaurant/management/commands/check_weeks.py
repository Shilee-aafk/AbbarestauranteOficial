from django.core.management.base import BaseCommand
from restaurant.models import Order
from datetime import datetime

class Command(BaseCommand):
    help = 'Mostrar órdenes y sus semanas'

    def handle(self, *args, **options):
        self.stdout.write("Órdenes recientes:\n")
        for order in Order.objects.filter(status__in=['paid', 'charged_to_room']).order_by('-id')[:10]:
            week_num = order.created_at.isocalendar()[1]
            year = order.created_at.isocalendar()[0]
            self.stdout.write(f"ID: {order.id}, Fecha: {order.created_at.date()}, Week {week_num}/{year}")
        
        self.stdout.write("\n--- Análisis de semanas ---")
        from datetime import date
        from django.utils import timezone
        
        today = timezone.now().date()
        self.stdout.write(f"Hoy: {today}, Semana: {today.isocalendar()[1]}")
        
        # ISO week starts on Monday
        iso_cal = today.isocalendar()
        self.stdout.write(f"ISO Calendar: year={iso_cal[0]}, week={iso_cal[1]}, weekday={iso_cal[2]}")
        
        # December 10, 2025 is Wednesday of week 50
        dec_10 = date(2025, 12, 10)
        self.stdout.write(f"\n10 Dec 2025 ISO week: {dec_10.isocalendar()[1]}")
