#!/usr/bin/env python
"""
Test script to verify models are correctly renamed
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AbbaRestaurante.settings')
django.setup()

from restaurant.models import Order, OrderItem, MenuItem, Category, RegistrationPin

print("✅ Successfully imported all renamed models:")
print(f"   - Order: {Order}")
print(f"   - OrderItem: {OrderItem}")
print(f"   - MenuItem: {MenuItem}")
print(f"   - Category: {Category}")
print(f"   - RegistrationPin: {RegistrationPin}")

# Test basic operations
try:
    print("\n🔍 Testing database tables...")
    print(f"   - MenuItem count: {MenuItem.objects.count()}")
    print(f"   - Order count: {Order.objects.count()}")
    print(f"   - OrderItem count: {OrderItem.objects.count()}")
    print(f"   - Category count: {Category.objects.count()}")
    print(f"   - RegistrationPin count: {RegistrationPin.objects.count()}")
    print("✅ All database tables are accessible")
except Exception as e:
    print(f"❌ Error accessing database: {e}")
    sys.exit(1)

print("\n✅ All models are correctly renamed and accessible!")
