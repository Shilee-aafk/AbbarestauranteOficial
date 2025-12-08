# Migration to handle model renaming from Spanish to English
# This migration renames database tables and columns that were previously in Spanish

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0008_category_add'),
    ]

    operations = [
        # Rename all tables first
        migrations.RunSQL(
            sql="""
            ALTER TABLE restaurant_categoria RENAME TO restaurant_category;
            ALTER TABLE restaurant_articulomenu RENAME TO restaurant_menuitem;
            ALTER TABLE restaurant_pedido RENAME TO restaurant_order;
            ALTER TABLE restaurant_itempedido RENAME TO restaurant_orderitem;
            ALTER TABLE restaurant_pinregistro RENAME TO restaurant_registrationpin;
            """,
            reverse_sql="""
            ALTER TABLE restaurant_category RENAME TO restaurant_categoria;
            ALTER TABLE restaurant_menuitem RENAME TO restaurant_articulomenu;
            ALTER TABLE restaurant_order RENAME TO restaurant_pedido;
            ALTER TABLE restaurant_orderitem RENAME TO restaurant_itempedido;
            ALTER TABLE restaurant_registrationpin RENAME TO restaurant_pinregistro;
            """,
        ),
        
        # Rename columns in the tables
        migrations.RunSQL(
            sql="""
            ALTER TABLE restaurant_orderitem RENAME COLUMN pedido_id TO order_id;
            ALTER TABLE restaurant_orderitem RENAME COLUMN articulo_menu_id TO menu_item_id;
            ALTER TABLE restaurant_menuitem RENAME COLUMN categoria_id TO category_id;
            """,
            reverse_sql="""
            ALTER TABLE restaurant_itempedido RENAME COLUMN order_id TO pedido_id;
            ALTER TABLE restaurant_itempedido RENAME COLUMN menu_item_id TO articulo_menu_id;
            ALTER TABLE restaurant_articulomenu RENAME COLUMN category_id TO categoria_id;
            """,
        ),
    ]

