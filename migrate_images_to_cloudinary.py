#!/usr/bin/env python
import os
import django
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AbbaRestaurante.settings')
django.setup()

from restaurant.models import MenuItem
from django.core.files.base import ContentFile
import cloudinary
import cloudinary.uploader

# Asegurar que Cloudinary está configurado
print("Configurando Cloudinary...")
print(f"Cloud Name: {cloudinary.config().cloud_name}")

# Carpeta donde están las imágenes locales
MEDIA_ROOT = Path('media') / 'menu_items'

if not MEDIA_ROOT.exists():
    print(f"⚠️ Carpeta {MEDIA_ROOT} no existe")
else:
    print(f"\n📁 Buscando imágenes en: {MEDIA_ROOT}\n")
    
    # Buscar todos los archivos de imagen
    image_files = list(MEDIA_ROOT.glob('*.*'))
    print(f"Encontradas {len(image_files)} imágenes\n")
    
    for image_path in image_files:
        filename = image_path.name
        print(f"Procesando: {filename}")
        
        try:
            # Abrir el archivo
            with open(image_path, 'rb') as f:
                # Subir a Cloudinary
                print(f"  → Subiendo a Cloudinary...")
                result = cloudinary.uploader.upload(
                    f,
                    public_id=f"restaurant/{Path(filename).stem}",
                    overwrite=True,
                    folder="restaurant/menu_items"
                )
                
                cloudinary_url = result.get('secure_url')
                print(f"  ✓ URL: {cloudinary_url}")
                
                # Buscar items con esta imagen
                items = MenuItem.objects.filter(image__endswith=filename)
                for item in items:
                    # Guardar la URL de Cloudinary en el campo image
                    item.image = cloudinary_url
                    item.save()
                    print(f"  ✓ Actualizado: {item.name}")
                
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
    
    print("\n✅ Migración completada!")
    
    # Mostrar resumen
    items_with_images = MenuItem.objects.filter(image__isnull=False).exclude(image='')
    print(f"\nItems con imágenes en BD: {items_with_images.count()}")
    for item in items_with_images:
        print(f"  - {item.name}: {item.image[:80]}...")
