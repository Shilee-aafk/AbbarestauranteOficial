from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from restaurant.models import ArticuloMenu, Pedido, ItemPedido, PinRegistro

class Command(BaseCommand):
    help = 'Setup permissions for user groups'

    def handle(self, *args, **options):
        # Get content types
        articulo_menu_ct = ContentType.objects.get_for_model(ArticuloMenu)
        pedido_ct = ContentType.objects.get_for_model(Pedido)
        item_pedido_ct = ContentType.objects.get_for_model(ItemPedido)
        user_ct = ContentType.objects.get_for_model(User)

        # Define permissions for each group
        permissions = {
            'Administrador': [
                # ArticuloMenu permissions
                Permission.objects.get(content_type=articulo_menu_ct, codename='add_articulomenu'),
                Permission.objects.get(content_type=articulo_menu_ct, codename='change_articulomenu'),
                Permission.objects.get(content_type=articulo_menu_ct, codename='delete_articulomenu'),
                Permission.objects.get(content_type=articulo_menu_ct, codename='view_articulomenu'),
                # Pedido permissions
                Permission.objects.get(content_type=pedido_ct, codename='add_pedido'),
                Permission.objects.get(content_type=pedido_ct, codename='change_pedido'),
                Permission.objects.get(content_type=pedido_ct, codename='delete_pedido'),
                Permission.objects.get(content_type=pedido_ct, codename='view_pedido'),
                # ItemPedido permissions
                Permission.objects.get(content_type=item_pedido_ct, codename='add_itempedido'),
                Permission.objects.get(content_type=item_pedido_ct, codename='change_itempedido'),
                Permission.objects.get(content_type=item_pedido_ct, codename='delete_itempedido'),
                Permission.objects.get(content_type=item_pedido_ct, codename='view_itempedido'),
                # User permissions
                Permission.objects.get(content_type=user_ct, codename='add_user'),
                Permission.objects.get(content_type=user_ct, codename='change_user'),
                Permission.objects.get(content_type=user_ct, codename='delete_user'),
                Permission.objects.get(content_type=user_ct, codename='view_user'),
            ],
            'Recepcionista': [
                # View permissions
                Permission.objects.get(content_type=articulo_menu_ct, codename='view_articulomenu'),
                Permission.objects.get(content_type=pedido_ct, codename='view_pedido'),
                Permission.objects.get(content_type=item_pedido_ct, codename='view_itempedido'),
            ],
            'Cocinero': [
                # View permissions
                Permission.objects.get(content_type=pedido_ct, codename='view_pedido'),
                Permission.objects.get(content_type=item_pedido_ct, codename='view_itempedido'),
                Permission.objects.get(content_type=articulo_menu_ct, codename='view_articulomenu'),
                # Order status changes
                Permission.objects.get(content_type=pedido_ct, codename='change_pedido'),
            ],
            'Garzón': [
                # View permissions
                Permission.objects.get(content_type=articulo_menu_ct, codename='view_articulomenu'),
                Permission.objects.get(content_type=pedido_ct, codename='view_pedido'),
                Permission.objects.get(content_type=item_pedido_ct, codename='view_itempedido'),
                # Order creation and management
                Permission.objects.get(content_type=pedido_ct, codename='add_pedido'),
                Permission.objects.get(content_type=item_pedido_ct, codename='add_itempedido'),
                Permission.objects.get(content_type=pedido_ct, codename='change_pedido'),
                Permission.objects.get(content_type=item_pedido_ct, codename='change_itempedido'),
            ],
        }

        # Assign permissions to groups
        for group_name, perms in permissions.items():
            group, created = Group.objects.get_or_create(name=group_name)
            group.permissions.set(perms)
            self.stdout.write(f'Permissions assigned to group: {group_name}')

        self.stdout.write(self.style.SUCCESS('Successfully set up permissions for all groups'))
