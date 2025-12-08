import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from restaurant.models import MenuItem
from django.db import transaction

class Command(BaseCommand):
    help = 'Crea roles, usuarios y datos iniciales (ej. menú) para el sistema.'

    # Define los usuarios a crear. Puedes cambiar los nombres de usuario y contraseñas aquí.
    # La contraseña 'password123' es solo para desarrollo. ¡Cámbiala en producción!
    USERS = {
        'Administrador': {'username': 'Administrador', 'password': 'password123', 'is_superuser': True},
        'Recepcionista': {'username': 'Recepcionista', 'password': 'password123'},
        'Garzón': {'username': 'Garzon', 'password': 'password123'},
        'Cocinero': {'username': 'Cocinero', 'password': 'password123'},
    }

    MENU_ITEMS = [
        {
            'name': 'Ceviche Clásico',
            'description': 'Pescado fresco marinado en jugo de limón, con cebolla roja, cilantro y ají limo.',
            'price': 9800,
            'categoria': 'Entradas'
        },
        {
            'name': 'Causa Limeña de Pollo',
            'description': 'Suave puré de papa amarilla sazonado con ají y limón, relleno de pollo y mayonesa.',
            'price': 7500,
            'categoria': 'Entradas'
        },
        {
            'name': 'Tequeños de Queso',
            'description': 'Crujientes bastones de masa frita rellenos de queso, acompañados de salsa de palta.',
            'price': 6900,
            'categoria': 'Entradas'
        },
        # --- Platos de Fondo ---
        {
            'name': 'Lomo Saltado',
            'description': 'Trozos de lomo de res salteados con cebolla, tomate y ají amarillo, servido con papas fritas y arroz.',
            'price': 12500,
            'categoria': 'Platos de Fondo'
        },
        {
            'name': 'Aji de Gallina',
            'description': 'Pechuga de gallina deshilachada en una cremosa salsa de ají amarillo, nueces y queso.',
            'price': 10500,
            'categoria': 'Platos de Fondo'
        },
        {
            'name': 'Seco de Cordero',
            'description': 'Tierno cordero cocido a fuego lento en salsa de cilantro, acompañado de frijoles y arroz.',
            'price': 13500,
            'categoria': 'Platos de Fondo'
        },
        {
            'name': 'Arroz con Mariscos',
            'description': 'Sabrosa mezcla de arroz con mariscos frescos, aderezo de ajíes y un toque de vino blanco.',
            'price': 14200,
            'categoria': 'Platos de Fondo'
        },
        # --- Postres ---
        {
            'name': 'Suspiro a la Limeña',
            'description': 'Dulce de manjar blanco cubierto con merengue al oporto.',
            'price': 4500,
            'categoria': 'Postres'
        },
        {
            'name': 'Torta Tres Leches',
            'description': 'Bizcocho esponjoso bañado en una mezcla de tres tipos de leche, cubierto con crema batida.',
            'price': 5200,
            'categoria': 'Postres'
        },
        # --- Bebestibles (Sin Alcohol) ---
        {
            'name': 'Jugo Natural de Frutilla',
            'description': 'Jugo fresco preparado con frutillas de temporada.',
            'price': 3500,
            'categoria': 'Bebestibles'
        },
        {
            'name': 'Limonada Menta Jengibre',
            'description': 'Refrescante limonada con toques de menta fresca y jengibre.',
            'price': 3800,
            'categoria': 'Bebestibles'
        },
        # --- Cócteles (Bar) ---
        {
            'name': 'Pisco Sour',
            'description': 'El clásico cóctel peruano con pisco, jugo de limón, jarabe de goma y clara de huevo.',
            'price': 5500,
            'categoria': 'Cócteles'
        },
        {
            'name': 'Mojito Clásico',
            'description': 'Refrescante mezcla de ron, menta, limón, azúcar y agua con gas.',
            'price': 6200,
            'categoria': 'Cócteles'
        },
        # --- Vinos y Cervezas (Bar) ---
        {
            'name': 'Copa de Vino Tinto (Carmenere)',
            'description': 'Copa de vino tinto reserva, variedad Carmenere.',
            'price': 4800,
            'categoria': 'Vinos y Cervezas'
        },
        {
            'name': 'Cerveza Nacional',
            'description': 'Botella de cerveza lager nacional.',
            'price': 3500,
            'categoria': 'Vinos y Cervezas'
        },
    ]

    # Define los permisos para cada rol. Usa el 'codename' del permiso.
    # Puedes encontrar los codenames en la tabla auth_permission de tu base de datos.
    ROLE_PERMISSIONS = {
        'Recepcionista': [
            'view_order', 'change_order', # Para ver y cobrar pedidos
            'add_reservation', 'change_reservation', 'delete_reservation', 'view_reservation' # Gestionar reservas
        ],
        'Garzón': [
            'add_order', 'change_order', 'view_order', # Gestionar sus propios pedidos
            'view_menuitem' # Ver el menú
        ],
        'Cocinero': [
            'change_order', 'view_order', # Ver y actualizar estado de pedidos
            'view_menuitem' # Ver el menú
        ],
        # El Administrador es superusuario, por lo que ya tiene todos los permisos.
        # No es necesario asignarlos explícitamente, pero se podría hacer si no fuera superuser.
    }

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('--- Iniciando la configuración de datos iniciales ---'))

        # --- SECCIÓN 1: CREAR USUARIOS Y ROLES ---
        self.stdout.write(self.style.NOTICE('\n>>> Creando roles y usuarios...'))
        for role_name, user_info in self.USERS.items():
            # --- 1. Crear el rol (Grupo) si no existe ---
            try:
                group, created = Group.objects.get_or_create(name=role_name)
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Rol '{role_name}' creado exitosamente."))
                else:
                    self.stdout.write(self.style.NOTICE(f"Rol '{role_name}' ya existía."))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error creando el rol '{role_name}': {e}"))
                continue # Si no se puede crear el rol, no continuar con el usuario

            # --- 2. Crear el usuario si no existe ---
            username = user_info['username']
            password = user_info['password']

            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.NOTICE(f"Usuario '{username}' ya existe. Saltando creación."))
            else:
                try:
                    # Crear usuario normal o superusuario
                    if user_info.get('is_superuser'):
                        user = User.objects.create_superuser(username=username, password=password, email=f"{username}@example.com")
                    else:
                        user = User.objects.create_user(username=username, password=password, email=f"{username}@example.com")

                    # Asignar el usuario al grupo correspondiente
                    user.groups.add(group)
                    self.stdout.write(self.style.SUCCESS(f"Usuario '{username}' creado y asignado al rol '{role_name}'."))

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error creando el usuario '{username}': {e}"))

        # --- SECCIÓN 2: ASIGNAR PERMISOS A LOS ROLES ---
        self.stdout.write(self.style.NOTICE('\n>>> Asignando permisos a los roles...'))
        for role_name, permissions_codenames in self.ROLE_PERMISSIONS.items():
            try:
                role = Group.objects.get(name=role_name)
                permissions_to_add = Permission.objects.filter(codename__in=permissions_codenames)
                
                # Usamos set() para añadir todos los permisos de una vez, evitando duplicados.
                role.permissions.set(permissions_to_add)
                
                self.stdout.write(self.style.SUCCESS(f"Permisos asignados correctamente al rol '{role_name}'."))
            except Group.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"El rol '{role_name}' no fue encontrado. Saltando asignación de permisos."))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error asignando permisos a '{role_name}': {e}"))


        # --- SECCIÓN 2: CREAR PLATOS DEL MENÚ ---
        self.stdout.write(self.style.NOTICE('\n>>> Creando platos del menú...'))
        for item_data in self.MENU_ITEMS:
            try:
                # Use the name as a unique identifier to avoid duplicates
                item, created = MenuItem.objects.get_or_create(
                    name=item_data['name'],
                    defaults=item_data
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Dish '{item.name}' created successfully."))
                else:
                    self.stdout.write(self.style.NOTICE(f"Dish '{item.name}' already existed."))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error creating dish '{item_data['name']}': {e}"))

        self.stdout.write(self.style.SUCCESS('--- Proceso finalizado ---'))