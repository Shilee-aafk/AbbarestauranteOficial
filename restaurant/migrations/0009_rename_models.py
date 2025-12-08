# Migration to handle model renaming from Spanish to English
# This migration renames database tables and columns
# NOTE: Works for PostgreSQL (used in production on Render)

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0008_category_add'),
    ]

    operations = [
        # For PostgreSQL: Rename tables and columns
        migrations.RunSQL(
            sql="""
            -- Rename columns first (they need to exist in the old tables)
            ALTER TABLE IF EXISTS restaurant_itempedido RENAME COLUMN IF EXISTS pedido_id TO order_id;
            ALTER TABLE IF EXISTS restaurant_itempedido RENAME COLUMN IF EXISTS articulo_menu_id TO menu_item_id;
            ALTER TABLE IF EXISTS restaurant_articulomenu RENAME COLUMN IF EXISTS categoria_id TO category_id;
            
            -- Rename tables
            ALTER TABLE IF EXISTS restaurant_categoria RENAME TO restaurant_category;
            ALTER TABLE IF EXISTS restaurant_articulomenu RENAME TO restaurant_menuitem;
            ALTER TABLE IF EXISTS restaurant_pedido RENAME TO restaurant_order;
            ALTER TABLE IF EXISTS restaurant_itempedido RENAME TO restaurant_orderitem;
            ALTER TABLE IF EXISTS restaurant_pinregistro RENAME TO restaurant_registrationpin;
            """,
            reverse_sql="",  # No reverse for this
        ),
    ]

