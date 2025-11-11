#!/usr/bin/env bash
# exit on error
set -o errexit

# Force use of system Python instead of Koyeb's Python environment
export PATH="/usr/bin:$PATH"

# Unset conflicting environment variables
unset PYTHONHOME
unset PYTHONPATH

# Create profile.d script if it doesn't exist
mkdir -p .profile.d
cat > .profile.d/python.sh << 'EOF'
#!/bin/bash
# Force system Python and unset conflicting variables
export PATH="/usr/bin:$PATH"
unset PYTHONHOME
unset PYTHONPATH
EOF
chmod +x .profile.d/python.sh

# Create migrate wrapper script
cat > migrate.sh << 'EOF'
#!/bin/bash
# Force system Python for migrate
export PATH="/usr/bin:$PATH"
unset PYTHONHOME
unset PYTHONPATH
exec env -i PATH="/usr/bin:/bin:/usr/local/bin" /usr/bin/python3 manage.py migrate
EOF
chmod +x migrate.sh

pip install -r requirements.txt

python3 manage.py collectstatic --no-input
./migrate.sh
