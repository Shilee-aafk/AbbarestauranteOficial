"""
WSGI config for AbbaRestaurante project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys
import django

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AbbaRestaurante.settings')

# Initialize Django
django.setup()

application = get_wsgi_application()

# Create default users on startup if they don't exist
def create_default_users():
    """Create default users if they don't exist"""
    try:
        from django.contrib.auth.models import User, Group
        
        # Default users to create
        USERS = {
            'Administrador': {'username': 'admin_user', 'password': 'password123', 'is_superuser': True},
            'Recepcionista': {'username': 'recepcion_user', 'password': 'password123'},
            'Garzón': {'username': 'garzon_user', 'password': 'password123'},
            'Cocinero': {'username': 'cocinero_user', 'password': 'password123'},
        }
        
        for group_name, user_data in USERS.items():
            username = user_data['username']
            
            # Check if user already exists
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    password=user_data['password'],
                    is_superuser=user_data.get('is_superuser', False),
                    is_staff=user_data.get('is_superuser', False)
                )
                
                # Add user to group
                group, created = Group.objects.get_or_create(name=group_name)
                user.groups.add(group)
                user.save()
                
                print(f"✅ Created user: {username} (Group: {group_name})")
            else:
                print(f"ℹ️  User already exists: {username}")
    except Exception as e:
        print(f"⚠️  Could not create default users: {e}", file=sys.stderr)

# Run on startup
try:
    create_default_users()
except Exception as e:
    print(f"Warning: Could not initialize default users: {e}", file=sys.stderr)



