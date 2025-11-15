"""
Auto-migration handler for Render deployment.
Ejecuta migraciones automáticamente al iniciar la app.
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AbbaRestaurante.settings')
django.setup()

from django.core.management import call_command
from django.db import connection
from django.db.migrations.recorder import MigrationRecorder


def run_migrations_if_needed():
    """
    Ejecuta migraciones automáticamente si:
    1. Estamos en producción (no DEBUG)
    2. Las migraciones no se han ejecutado
    """
    try:
        # Detectar si estamos en producción
        DEBUG = os.environ.get('DEBUG', 'True') == 'True'
        IS_RENDER = 'RENDER' in os.environ
        IS_KOYEB = 'KOYEB_PUBLIC_DOMAIN' in os.environ
        
        # Solo ejecutar en producción
        if not (IS_RENDER or IS_KOYEB or 'PYTHONANYWHERE_DOMAIN' in os.environ):
            return
        
        # No ejecutar si se especifica lo contrario
        if os.environ.get('SKIP_MIGRATIONS') == 'true':
            return
        
        print("🔄 Checking if migrations are needed...")
        
        # Verificar si la tabla de migraciones existe
        with connection.cursor() as cursor:
            try:
                recorder = MigrationRecorder(connection)
                applied = list(recorder.applied_migrations())
                
                if applied:
                    print(f"✅ Migrations already applied ({len(applied)} migrations)")
                    return
                else:
                    print("⚠️ No migrations applied yet, running migrations...")
            except Exception as e:
                print(f"⚠️ Could not check migrations: {e}")
                return
        
        # Ejecutar migraciones
        try:
            call_command('migrate', verbosity=2, interactive=False)
            print("✅ Migrations completed successfully")
        except Exception as e:
            print(f"❌ Error running migrations: {e}")
            # No fallar, solo advertir
    
    except Exception as e:
        print(f"⚠️ Auto-migration check failed: {e}")


if __name__ == '__main__':
    run_migrations_if_needed()
