# Migration to handle model renaming from Spanish to English
# This migration renames database tables and columns that were previously in Spanish

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0008_category_add'),
    ]

    operations = [
        # This migration uses state_operations to tell Django what the final state should be,
        # and database_operations to actually perform the renames in PostgreSQL
        
        migrations.RunSQL(
            # PostgreSQL: Rename tables and columns
            sql="""
            -- Rename columns in ItemPedido table first
            ALTER TABLE restaurant_itempedido RENAME COLUMN pedido_id TO order_id;
            ALTER TABLE restaurant_itempedido RENAME COLUMN articulo_menu_id TO menu_item_id;
            
            -- Rename column in ArticuloMenu table
            ALTER TABLE restaurant_articulomenu RENAME COLUMN categoria_id TO category_id;
            
            -- Rename the tables
            ALTER TABLE restaurant_categoria RENAME TO restaurant_category;
            ALTER TABLE restaurant_articulomenu RENAME TO restaurant_menuitem;
            ALTER TABLE restaurant_pedido RENAME TO restaurant_order;
            ALTER TABLE restaurant_itempedido RENAME TO restaurant_orderitem;
            ALTER TABLE restaurant_pinregistro RENAME TO restaurant_registrationpin;
            """,
            reverse_sql="""
            -- Reverse order: rename tables back
            ALTER TABLE restaurant_category RENAME TO restaurant_categoria;
            ALTER TABLE restaurant_menuitem RENAME TO restaurant_articulomenu;
            ALTER TABLE restaurant_order RENAME TO restaurant_pedido;
            ALTER TABLE restaurant_orderitem RENAME TO restaurant_itempedido;
            ALTER TABLE restaurant_registrationpin RENAME TO restaurant_pinregistro;
            
            -- Rename columns back
            ALTER TABLE restaurant_articulomenu RENAME COLUMN category_id TO categoria_id;
            ALTER TABLE restaurant_itempedido RENAME COLUMN menu_item_id TO articulo_menu_id;
            ALTER TABLE restaurant_itempedido RENAME COLUMN order_id TO pedido_id;
            """,
        ),
    ]

