"""
WSGI config for AbbaRestaurante project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AbbaRestaurante.settings')

application = get_wsgi_application()

# Auto-run migrations on Render startup
try:
    from AbbaRestaurante.auto_migrate import run_migrations_if_needed
    run_migrations_if_needed()
except Exception as e:
    print(f"Warning: Could not run auto-migrations: {e}", file=sys.stderr)

