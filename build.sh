#!/usr/bin/env bash
# exit on error
set -o errexit

# Unset PYTHONHOME to avoid conflicts with the system Python
unset PYTHONHOME

pip install -r requirements.txt

python3 manage.py collectstatic --no-input
python3 manage.py migrate
