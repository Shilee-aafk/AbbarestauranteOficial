#!/usr/bin/env python
"""
Script para eliminar la tabla restaurant_category de la base de datos de Render
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AbbaRestaurante.settings')

# Asegurarse de que estamos usando la BD de Render si existe DATABASE_URL
if 'DATABASE_URL' not in os.environ:
    print("⚠️  DATABASE_URL no está configurado. Usando BD local de desarrollo.")
    print("Si necesitas usar la BD de Render, define la variable DATABASE_URL")
else:
    print("✅ Usando DATABASE_URL de Render")

django.setup()

from django.db import connection
from django.db.utils import OperationalError

def drop_category_table():
    """Elimina la tabla restaurant_category"""
    try:
        with connection.cursor() as cursor:
            # Verificar si la tabla existe
            cursor.execute("""
                SELECT TABLE_NAME FROM information_schema.TABLES 
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'restaurant_category'
            """)
            
            if cursor.fetchone():
                print("🗑️  Tabla 'restaurant_category' encontrada. Eliminando...")
                cursor.execute('DROP TABLE IF EXISTS restaurant_category')
                print("✅ Tabla 'restaurant_category' eliminada exitosamente")
            else:
                print("ℹ️  La tabla 'restaurant_category' no existe")
                
        return True
    except OperationalError as e:
        print(f"❌ Error operacional: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    success = drop_category_table()
    sys.exit(0 if success else 1)
