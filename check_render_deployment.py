#!/usr/bin/env python
"""
Script para verificar que tu app está lista para desplegarse en Render.
Ejecuta: python check_render_deployment.py
"""

import os
import sys
from pathlib import Path

def check_file_exists(filename):
    """Verifica si un archivo existe en la raíz del proyecto."""
    path = Path(filename)
    exists = path.exists()
    status = "✅" if exists else "❌"
    print(f"{status} {filename}")
    return exists

def check_environment_variable(var_name):
    """Verifica si una variable de entorno está configurada."""
    exists = var_name in os.environ
    status = "✅" if exists else "⚠️"
    print(f"{status} {var_name}")
    return exists

def main():
    print("\n" + "="*60)
    print("🔍 VERIFICACIÓN DE CONFIGURACIÓN PARA RENDER")
    print("="*60 + "\n")
    
    # Verificar archivos necesarios
    print("📁 Archivos requeridos:")
    files_ok = all([
        check_file_exists("Procfile"),
        check_file_exists("runtime.txt"),
        check_file_exists("requirements.txt"),
        check_file_exists("manage.py"),
    ])
    
    print("\n📄 Archivos opcionales (pero recomendados):")
    optional_files = all([
        check_file_exists("render.yaml"),
        check_file_exists(".env.example"),
        check_file_exists("RENDER_DEPLOYMENT.md"),
    ])
    
    # Verificar variables de entorno
    print("\n🔐 Variables de entorno en desarrollo:")
    env_vars_ok = all([
        check_environment_variable("SECRET_KEY"),
        check_environment_variable("DATABASE_URL"),
    ])
    
    # Resultado final
    print("\n" + "="*60)
    if files_ok:
        print("✅ Tu proyecto está listo para desplegar en Render!")
        print("\n📋 Próximos pasos:")
        print("1. Haz commit y push de los cambios a GitHub")
        print("2. Ve a render.com y conecta tu repositorio")
        print("3. Sigue la guía en RENDER_DEPLOYMENT.md")
        print("4. Configura las variables de entorno en Render")
        return 0
    else:
        print("❌ Faltan algunos archivos. Por favor, verifica.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
