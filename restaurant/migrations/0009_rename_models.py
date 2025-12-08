# Migration to handle model renaming from Spanish to English
# This migration renames database tables and columns that were previously in Spanish

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0008_category_add'),
    ]

    operations = [
        # Drop foreign key constraints before renaming columns
        migrations.RunSQL(
            sql="""
            ALTER TABLE restaurant_itempedido DROP CONSTRAINT restaurant_itempedido_pedido_id_fkey;
            ALTER TABLE restaurant_itempedido DROP CONSTRAINT restaurant_itempedido_articulo_menu_id_fkey;
            """,
            reverse_sql="""
            -- These will be recreated when we reverse the rename
            """,
        ),
        
        # Now do the renames
        migrations.RunSQL(
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
        
        # Recreate foreign key constraints with new names
        migrations.RunSQL(
            sql="""
            ALTER TABLE restaurant_orderitem ADD CONSTRAINT restaurant_orderitem_order_id_fkey 
                FOREIGN KEY (order_id) REFERENCES restaurant_order(id) ON DELETE CASCADE;
            ALTER TABLE restaurant_orderitem ADD CONSTRAINT restaurant_orderitem_menu_item_id_fkey 
                FOREIGN KEY (menu_item_id) REFERENCES restaurant_menuitem(id) ON DELETE CASCADE;
            """,
            reverse_sql="""
            ALTER TABLE restaurant_itempedido ADD CONSTRAINT restaurant_itempedido_pedido_id_fkey 
                FOREIGN KEY (pedido_id) REFERENCES restaurant_pedido(id) ON DELETE CASCADE;
            ALTER TABLE restaurant_itempedido ADD CONSTRAINT restaurant_itempedido_articulo_menu_id_fkey 
                FOREIGN KEY (articulo_menu_id) REFERENCES restaurant_articulomenu(id) ON DELETE CASCADE;
            """,
        ),
    ]

