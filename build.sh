#!/usr/bin/env bash
# exit on error
set -o errexit
# Instala las dependencias usando el Python del buildpack
pip install -r requirements.txt

# Recolecta los archivos estáticos
python manage.py collectstatic --no-input

# Aplica las migraciones de la base de datos
python manage.py migrate
