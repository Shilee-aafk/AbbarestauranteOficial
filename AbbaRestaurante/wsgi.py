"""
WSGI config for AbbaRestaurante project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Unset PYTHONHOME to avoid conflicts in containerized environments like Koyeb
os.environ.pop('PYTHONHOME', None)
# Clear PYTHONPATH to avoid path conflicts
os.environ.pop('PYTHONPATH', None)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AbbaRestaurante.settings')

application = get_wsgi_application()
