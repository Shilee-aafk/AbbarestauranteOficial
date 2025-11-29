#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AbbaRestaurante.settings')
django.setup()

from django.conf import settings

print(f"DEBUG: {settings.DEBUG}")
print(f"DEFAULT_FILE_STORAGE: {settings.DEFAULT_FILE_STORAGE}")
print(f"MEDIA_URL: {settings.MEDIA_URL}")

# Intentar cargar Cloudinary
try:
    import cloudinary
    print(f"Cloudinary Cloud Name: {cloudinary.config().cloud_name}")
    print(f"Cloudinary API Key: {cloudinary.config().api_key[:10]}...")
except Exception as e:
    print(f"Error cargando Cloudinary: {e}")
