from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from restaurant.models import MenuItem, Reservation, Order, OrderItem

class Command(BaseCommand):
    help = 'Setup permissions for user groups'

    def handle(self, *args, **options):
        # Get content types
        menuitem_ct = ContentType.objects.get_for_model(MenuItem)
        reservation_ct = ContentType.objects.get_for_model(Reservation)
        order_ct = ContentType.objects.get_for_model(Order)
        orderitem_ct = ContentType.objects.get_for_model(OrderItem)
        user_ct = ContentType.objects.get_for_model(User)

        # Define permissions for each group
        permissions = {
            'Administrador': [
                # MenuItem permissions
                Permission.objects.get(content_type=menuitem_ct, codename='add_menuitem'),
                Permission.objects.get(content_type=menuitem_ct, codename='change_menuitem'),
                Permission.objects.get(content_type=menuitem_ct, codename='delete_menuitem'),
                Permission.objects.get(content_type=menuitem_ct, codename='view_menuitem'),
                # Reservation permissions
                Permission.objects.get(content_type=reservation_ct, codename='add_reservation'),
                Permission.objects.get(content_type=reservation_ct, codename='change_reservation'),
                Permission.objects.get(content_type=reservation_ct, codename='delete_reservation'),
                Permission.objects.get(content_type=reservation_ct, codename='view_reservation'),
                # Order permissions
                Permission.objects.get(content_type=order_ct, codename='add_order'),
                Permission.objects.get(content_type=order_ct, codename='change_order'),
                Permission.objects.get(content_type=order_ct, codename='delete_order'),
                Permission.objects.get(content_type=order_ct, codename='view_order'),
                # OrderItem permissions
                Permission.objects.get(content_type=orderitem_ct, codename='add_orderitem'),
                Permission.objects.get(content_type=orderitem_ct, codename='change_orderitem'),
                Permission.objects.get(content_type=orderitem_ct, codename='delete_orderitem'),
                Permission.objects.get(content_type=orderitem_ct, codename='view_orderitem'),
                # User permissions
                Permission.objects.get(content_type=user_ct, codename='add_user'),
                Permission.objects.get(content_type=user_ct, codename='change_user'),
                Permission.objects.get(content_type=user_ct, codename='delete_user'),
                Permission.objects.get(content_type=user_ct, codename='view_user'),
            ],
            'Recepcionista': [
                # View permissions
                Permission.objects.get(content_type=menuitem_ct, codename='view_menuitem'),
                Permission.objects.get(content_type=reservation_ct, codename='view_reservation'),
                Permission.objects.get(content_type=order_ct, codename='view_order'),
                Permission.objects.get(content_type=orderitem_ct, codename='view_orderitem'),
                # Reservation management
                Permission.objects.get(content_type=reservation_ct, codename='add_reservation'),
                Permission.objects.get(content_type=reservation_ct, codename='change_reservation'),
                Permission.objects.get(content_type=reservation_ct, codename='delete_reservation'),
            ],
            'Cocinero': [
                # View permissions
                Permission.objects.get(content_type=order_ct, codename='view_order'),
                Permission.objects.get(content_type=orderitem_ct, codename='view_orderitem'),
                Permission.objects.get(content_type=menuitem_ct, codename='view_menuitem'),
                # Order status changes
                Permission.objects.get(content_type=order_ct, codename='change_order'),
            ],
            'Garzón': [
                # View permissions
                Permission.objects.get(content_type=menuitem_ct, codename='view_menuitem'),
                Permission.objects.get(content_type=order_ct, codename='view_order'),
                Permission.objects.get(content_type=orderitem_ct, codename='view_orderitem'),
                # Order creation and management
                Permission.objects.get(content_type=order_ct, codename='add_order'),
                Permission.objects.get(content_type=orderitem_ct, codename='add_orderitem'),
                Permission.objects.get(content_type=order_ct, codename='change_order'),
                Permission.objects.get(content_type=orderitem_ct, codename='change_orderitem'),
            ],
        }

        # Assign permissions to groups
        for group_name, perms in permissions.items():
            group, created = Group.objects.get_or_create(name=group_name)
            group.permissions.set(perms)
            self.stdout.write(f'Permissions assigned to group: {group_name}')

        self.stdout.write(self.style.SUCCESS('Successfully set up permissions for all groups'))
