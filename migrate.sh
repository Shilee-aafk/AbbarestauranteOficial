#!/bin/bash
# Wrapper script to run migrate with proper Python environment
unset PYTHONHOME
python3 manage.py migrate
