# Migration to handle model renaming from Spanish to English
# This uses RunSQL to safely rename tables and columns

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0008_category_add'),
    ]

    operations = [
        # Rename columns in ItemPedido table BEFORE renaming the table
        migrations.RunSQL(
            # Forward: Rename columns
            """
            BEGIN;
            ALTER TABLE restaurant_itempedido RENAME COLUMN pedido_id TO order_id;
            ALTER TABLE restaurant_itempedido RENAME COLUMN articulo_menu_id TO menu_item_id;
            COMMIT;
            """,
            # Reverse
            """
            BEGIN;
            ALTER TABLE restaurant_itempedido RENAME COLUMN order_id TO pedido_id;
            ALTER TABLE restaurant_itempedido RENAME COLUMN menu_item_id TO articulo_menu_id;
            COMMIT;
            """,
        ),
        
        # Rename column in ArticuloMenu table
        migrations.RunSQL(
            # Forward
            """
            ALTER TABLE restaurant_articulomenu RENAME COLUMN categoria TO category;
            """,
            # Reverse
            """
            ALTER TABLE restaurant_articulomenu RENAME COLUMN category TO categoria;
            """,
        ),
        
        # Now rename the tables
        migrations.RunSQL(
            # Forward: Rename all tables
            """
            BEGIN;
            ALTER TABLE restaurant_categoria RENAME TO restaurant_category;
            ALTER TABLE restaurant_articulomenu RENAME TO restaurant_menuitem;
            ALTER TABLE restaurant_pedido RENAME TO restaurant_order;
            ALTER TABLE restaurant_itempedido RENAME TO restaurant_orderitem;
            ALTER TABLE restaurant_pinregistro RENAME TO restaurant_registrationpin;
            COMMIT;
            """,
            # Reverse: Rename back
            """
            BEGIN;
            ALTER TABLE restaurant_category RENAME TO restaurant_categoria;
            ALTER TABLE restaurant_menuitem RENAME TO restaurant_articulomenu;
            ALTER TABLE restaurant_order RENAME TO restaurant_pedido;
            ALTER TABLE restaurant_orderitem RENAME TO restaurant_itempedido;
            ALTER TABLE restaurant_registrationpin RENAME TO restaurant_pinregistro;
            COMMIT;
            """,
        ),
    ]

