"""
Utility functions for the restaurant app.
"""
from django.conf import settings


def get_cloudinary_url(public_id):
    """
    Get the full Cloudinary URL for a given public ID.
    Uses dynamic configuration from settings.
    
    Args:
        public_id (str): The Cloudinary public ID
        
    Returns:
        str: The full Cloudinary URL
    """
    cloud_name = getattr(settings, 'CLOUDINARY_STORAGE', {}).get('CLOUD_NAME', 'dvjcrc3ei')
    return f'https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}'


def get_cloudinary_cloud_name():
    """
    Get the Cloudinary cloud name from settings.
    
    Returns:
        str: The Cloudinary cloud name
    """
    return getattr(settings, 'CLOUDINARY_STORAGE', {}).get('CLOUD_NAME', 'dvjcrc3ei')
