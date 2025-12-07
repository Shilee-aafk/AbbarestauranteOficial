#!/usr/bin/env python
"""
Script to test image upload functionality
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AbbaRestaurante.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User, Group
from restaurant.models import ArticuloMenu
from django.core.files.base import ContentFile
from PIL import Image
from io import BytesIO

def create_test_image(name='test_image.jpg', size=(100, 100)):
    """Create a simple test image"""
    img = Image.new('RGB', size, color='red')
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    return ContentFile(img_byte_arr.read(), name=name)

def test_image_upload():
    """Test the image upload process"""
    print("\n=== Testing Image Upload ===\n")
    
    # Get or create admin user
    admin_user = User.objects.filter(username='admin').first()
    if not admin_user:
        print("❌ Admin user not found. Please create it first.")
        return
    
    # Get or create a test menu item
    item, created = ArticuloMenu.objects.get_or_create(
        name='Test Dish',
        defaults={
            'description': 'Test dish for image upload',
            'price': 10.00,
            'category': 'Test',
            'available': True
        }
    )
    print(f"{'✓ Created' if created else '✓ Found'} menu item: {item.name} (ID: {item.id})")
    
    # Check initial state
    print(f"\nBefore upload:")
    print(f"  - image field: {item.image.name if item.image else 'None'}")
    print(f"  - image exists: {bool(item.image)}")
    
    # Create and assign test image
    print(f"\nUploading test image...")
    test_img = create_test_image()
    item.image = test_img
    item.save()
    
    # Reload and check
    item.refresh_from_db()
    print(f"\nAfter upload:")
    print(f"  - image field: {item.image.name if item.image else 'None'}")
    print(f"  - image exists: {bool(item.image)}")
    
    if item.image:
        print(f"  - image URL: {item.image.url}")
        print(f"  - image path: {item.image.path}")
        print(f"  - file exists on disk: {os.path.exists(item.image.path)}")
        print(f"\n✅ Image upload test PASSED!")
    else:
        print(f"\n❌ Image upload test FAILED - image not saved!")
        return False
    
    return True

if __name__ == '__main__':
    success = test_image_upload()
    sys.exit(0 if success else 1)
