"""
Auto-migration handler for Render deployment.
Ejecuta migraciones automáticamente al iniciar la app.
"""
import os
import sys


def run_migrations_if_needed():
    """
    Ejecuta migraciones automáticamente si:
    1. Estamos en producción (no DEBUG)
    2. Las migraciones no se han ejecutado
    """
    try:
        # Detectar si estamos en producción
        IS_RENDER = 'RENDER' in os.environ
        IS_KOYEB = 'KOYEB_PUBLIC_DOMAIN' in os.environ
        IS_PYTHONANYWHERE = 'PYTHONANYWHERE_DOMAIN' in os.environ
        
        # Ejecutar SIEMPRE que estemos en un entorno cloud
        # No importa si estamos en desarrollo local o producción
        should_migrate = IS_RENDER or IS_KOYEB or IS_PYTHONANYWHERE
        
        if not should_migrate:
            return
        
        # No ejecutar si se especifica lo contrario
        if os.environ.get('SKIP_MIGRATIONS') == 'true':
            return
        
        print("🔄 Checking if migrations are needed...")
        
        # Importar Django después de la configuración inicial
        import django
        from django.core.management import call_command
        from django.db import connection
        from django.db.migrations.recorder import MigrationRecorder
        
        # Setup Django si no está configurado
        if not django.apps.apps.ready:
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AbbaRestaurante.settings')
            django.setup()
        
        # Ejecutar migraciones sin verificar primero
        try:
            print("⚠️ Running migrations...")
            call_command('migrate', verbosity=2, interactive=False)
            print("✅ Migrations completed successfully")
        except Exception as e:
            print(f"❌ Error running migrations: {e}")
            # No fallar, solo advertir
            import traceback
            traceback.print_exc()
    
    except Exception as e:
        print(f"⚠️ Auto-migration check failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_migrations_if_needed()
