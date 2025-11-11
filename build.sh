#!/usr/bin/env bash
# exit on error
set -o errexit

# Unset PYTHONHOME to avoid conflicts with the system Python
unset PYTHONHOME

# Create profile.d script if it doesn't exist
mkdir -p .profile.d
cat > .profile.d/python.sh << 'EOF'
#!/bin/bash
# Unset PYTHONHOME to avoid conflicts in Koyeb's containerized environment
unset PYTHONHOME
EOF
chmod +x .profile.d/python.sh

pip install -r requirements.txt

python3 manage.py collectstatic --no-input
python3 manage.py migrate
