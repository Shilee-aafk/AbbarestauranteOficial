#!/usr/bin/env python
"""
Test script to verify media file serving works correctly
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AbbaRestaurante.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.conf import settings
from restaurant.models import MenuItem

def test_media_serving():
    """Test that media files can be served"""
    print("\n=== Testing Media File Serving ===\n")
    
    # Get item with image
    item = MenuItem.objects.filter(image__isnull=False).exclude(image='').first()
    
    if not item:
        print("❌ No menu items with images found")
        return False
    
    print(f"✓ Found menu item with image: {item.name}")
    print(f"  - Image name: {item.image.name}")
    print(f"  - Image URL: {item.image.url}")
    
    # Check if file exists on disk
    file_path = item.image.path
    if not os.path.exists(file_path):
        print(f"❌ Image file not found on disk: {file_path}")
        return False
    
    print(f"✓ Image file exists on disk")
    print(f"  - File path: {file_path}")
    print(f"  - File size: {os.path.getsize(file_path)} bytes")
    
    # Test the media serving view
    client = Client()
    # The URL should match the media URL in settings
    test_url = f'/media/{item.image.name}'
    print(f"\n✓ Testing URL: {test_url}")
    
    response = client.get(test_url)
    print(f"  - Response status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"  - Content-Type: {response.get('Content-Type', 'N/A')}")
        print(f"✅ Media file serving PASSED!")
        return True
    else:
        print(f"❌ Media file serving FAILED (status {response.status_code})")
        print(f"  - Response: {response.content[:200]}")
        return False

if __name__ == '__main__':
    success = test_media_serving()
    sys.exit(0 if success else 1)
