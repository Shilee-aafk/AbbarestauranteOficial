#!/usr/bin/env python
"""
Script de inicialización para Render.
Ejecuta migraciones y crea datos iniciales sin necesidad de acceso a terminal.
Se ejecuta automáticamente durante el build en Render.
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AbbaRestaurante.settings')
django.setup()

from django.core.management import call_command
from django.db import connection

def run_migrations():
    """Ejecuta las migraciones de la base de datos."""
    print("🔄 Ejecutando migraciones...")
    try:
        call_command('migrate', verbosity=2)
        print("✅ Migraciones completadas exitosamente")
        return True
    except Exception as e:
        print(f"❌ Error en migraciones: {e}")
        return False

def create_initial_users():
    """Crea usuarios, roles y datos iniciales."""
    print("\n👥 Creando usuarios y datos iniciales...")
    try:
        call_command('crear_usuarios', verbosity=2)
        print("✅ Usuarios y datos iniciales creados exitosamente")
        return True
    except Exception as e:
        print(f"⚠️ Nota: {e}")
        # No fallar si el comando no existe, es opcional
        return True

def check_database():
    """Verifica que la base de datos está accesible."""
    print("🔗 Verificando conexión a base de datos...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Base de datos accesible")
        return True
    except Exception as e:
        print(f"❌ Error de conexión a BD: {e}")
        return False

def main():
    """Función principal."""
    print("\n" + "="*60)
    print("🚀 INICIALIZACIÓN DE RENDER")
    print("="*60 + "\n")
    
    # Verificar BD
    if not check_database():
        print("❌ No se pudo conectar a la base de datos")
        return 1
    
    # Ejecutar migraciones
    if not run_migrations():
        print("❌ Error durante las migraciones")
        return 1
    
    # Crear usuarios iniciales
    if not create_initial_users():
        print("⚠️ Adviso: No se pudieron crear usuarios iniciales")
    
    print("\n" + "="*60)
    print("✅ INICIALIZACIÓN COMPLETADA EXITOSAMENTE")
    print("="*60 + "\n")
    return 0

if __name__ == '__main__':
    sys.exit(main())
