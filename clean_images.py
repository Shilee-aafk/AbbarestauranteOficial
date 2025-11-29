#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AbbaRestaurante.settings')
django.setup()

from restaurant.models import MenuItem

# Ver qué imágenes hay
items = MenuItem.objects.filter(image__isnull=False).exclude(image='')
print(f"Items con imágenes: {items.count()}")
for item in items:
    print(f"  - {item.name}: {item.image.name}")

# Limpiar las imágenes
items.update(image='')
print("\n✓ Imágenes limpiadas. Ahora puedes subirlas nuevamente desde el dashboard.")
