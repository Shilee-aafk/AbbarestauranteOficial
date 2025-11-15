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

# Create default users and menu items on startup
def initialize_default_data():
    """Create default users and menu items if they don't exist"""
    try:
        from django.contrib.auth.models import User, Group
        from restaurant.models import MenuItem
        
        # Default users to create
        USERS = {
            'Administrador': {'username': 'admin_user', 'password': 'password123', 'is_superuser': True},
            'Recepcionista': {'username': 'recepcion_user', 'password': 'password123'},
            'Garzón': {'username': 'garzon_user', 'password': 'password123'},
            'Cocinero': {'username': 'cocinero_user', 'password': 'password123'},
        }
        
        # Create users
        for group_name, user_data in USERS.items():
            username = user_data['username']
            
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    password=user_data['password'],
                    is_superuser=user_data.get('is_superuser', False),
                    is_staff=user_data.get('is_superuser', False)
                )
                group, created = Group.objects.get_or_create(name=group_name)
                user.groups.add(group)
                user.save()
                print(f"✅ Created user: {username} (Group: {group_name})")
            else:
                print(f"ℹ️  User already exists: {username}")
        
        # Default menu items
        MENU_ITEMS = [
            # Entradas
            {'name': 'Ceviche Clásico', 'description': 'Pescado fresco marinado en jugo de limón, con cebolla roja, cilantro y ají limo.', 'price': 9800, 'category': 'Entradas'},
            {'name': 'Causa Limeña de Pollo', 'description': 'Suave puré de papa amarilla sazonado con ají y limón, relleno de pollo y mayonesa.', 'price': 7500, 'category': 'Entradas'},
            {'name': 'Tequeños de Queso', 'description': 'Crujientes bastones de masa frita rellenos de queso, acompañados de salsa de palta.', 'price': 6900, 'category': 'Entradas'},
            # Platos de Fondo
            {'name': 'Lomo Saltado', 'description': 'Trozos de lomo de res salteados con cebolla, tomate y ají amarillo, servido con papas fritas y arroz.', 'price': 12500, 'category': 'Platos de Fondo'},
            {'name': 'Aji de Gallina', 'description': 'Pechuga de gallina deshilachada en una cremosa salsa de ají amarillo, nueces y queso.', 'price': 10500, 'category': 'Platos de Fondo'},
            {'name': 'Seco de Cordero', 'description': 'Tierno cordero cocido a fuego lento en salsa de cilantro, acompañado de frijoles y arroz.', 'price': 13500, 'category': 'Platos de Fondo'},
            {'name': 'Arroz con Mariscos', 'description': 'Sabrosa mezcla de arroz con mariscos frescos, aderezo de ajíes y un toque de vino blanco.', 'price': 14200, 'category': 'Platos de Fondo'},
            # Postres
            {'name': 'Suspiro a la Limeña', 'description': 'Dulce de manjar blanco cubierto con merengue al oporto.', 'price': 4500, 'category': 'Postres'},
            {'name': 'Torta Tres Leches', 'description': 'Bizcocho esponjoso bañado en una mezcla de tres tipos de leche, cubierto con crema batida.', 'price': 5200, 'category': 'Postres'},
            # Bebestibles
            {'name': 'Jugo Natural de Frutilla', 'description': 'Jugo fresco preparado con frutillas de temporada.', 'price': 3500, 'category': 'Bebestibles'},
            {'name': 'Limonada Menta Jengibre', 'description': 'Refrescante limonada con toques de menta fresca y jengibre.', 'price': 3800, 'category': 'Bebestibles'},
            # Cócteles
            {'name': 'Pisco Sour', 'description': 'El clásico cóctel peruano con pisco, jugo de limón, jarabe de goma y clara de huevo.', 'price': 5500, 'category': 'Cócteles'},
            {'name': 'Mojito Clásico', 'description': 'Refrescante mezcla de ron, menta, limón, azúcar y agua con gas.', 'price': 6200, 'category': 'Cócteles'},
            # Vinos y Cervezas
            {'name': 'Copa de Vino Tinto (Carmenere)', 'description': 'Copa de vino tinto reserva, variedad Carmenere.', 'price': 4800, 'category': 'Vinos y Cervezas'},
            {'name': 'Cerveza Nacional', 'description': 'Botella de cerveza lager nacional.', 'price': 3500, 'category': 'Vinos y Cervezas'},
        ]
        
        # Create menu items
        created_count = 0
        for item_data in MENU_ITEMS:
            if not MenuItem.objects.filter(name=item_data['name']).exists():
                MenuItem.objects.create(**item_data)
                created_count += 1
        
        if created_count > 0:
            print(f"✅ Created {created_count} menu items")
        else:
            print("ℹ️  All menu items already exist")
            
    except Exception as e:
        print(f"⚠️  Could not initialize default data: {e}", file=sys.stderr)

# Run on startup
try:
    initialize_default_data()
except Exception as e:
    print(f"Warning: Could not initialize default data: {e}", file=sys.stderr)




