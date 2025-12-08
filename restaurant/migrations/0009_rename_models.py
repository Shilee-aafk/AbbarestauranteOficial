# Generated migration to rename models from Spanish to English

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0008_category_add'),
    ]

    operations = [
        # Step 1: Rename Categoria to Category
        migrations.RenameModel(
            old_name='Categoria',
            new_name='Category',
        ),
        
        # Step 2: Rename ArticuloMenu to MenuItem
        migrations.RenameModel(
            old_name='ArticuloMenu',
            new_name='MenuItem',
        ),
        
        # Step 3: Rename the field in MenuItem
        migrations.RenameField(
            model_name='menuitem',
            old_name='categoria',
            new_name='category',
        ),
        
        # Step 4: Rename Pedido to Order
        migrations.RenameModel(
            old_name='Pedido',
            new_name='Order',
        ),
        
        # Step 5: Rename ItemPedido to OrderItem
        migrations.RenameModel(
            old_name='ItemPedido',
            new_name='OrderItem',
        ),
        
        # Step 6: Rename the field relationships in OrderItem
        migrations.RenameField(
            model_name='orderitem',
            old_name='pedido',
            new_name='order',
        ),
        migrations.RenameField(
            model_name='orderitem',
            old_name='articulo_menu',
            new_name='menu_item',
        ),
        
        # Step 7: Rename PinRegistro to RegistrationPin
        migrations.RenameModel(
            old_name='PinRegistro',
            new_name='RegistrationPin',
        ),
        
        # Step 8: Update through model on Order.items field
        migrations.AlterField(
            model_name='order',
            name='items',
            field=models.ManyToManyField(through='restaurant.OrderItem', to='restaurant.MenuItem'),
        ),
    ]
