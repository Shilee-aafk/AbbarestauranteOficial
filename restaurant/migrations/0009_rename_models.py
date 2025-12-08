# Migration to handle model renaming from Spanish to English
# This migration renames database tables and columns
# NOTE: For PostgreSQL (production on Render)

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0008_category_add'),
    ]

    operations = [
        # Direct rename: Just rename the columns that exist
        # The tables may already be renamed, but columns need to be fixed
        migrations.RunSQL(
            sql="""
            -- Rename columns in restaurant_orderitem table
            ALTER TABLE restaurant_orderitem RENAME COLUMN pedido_id TO order_id;
            ALTER TABLE restaurant_orderitem RENAME COLUMN articulo_menu_id TO menu_item_id;
            """,
            reverse_sql="""
            ALTER TABLE restaurant_orderitem RENAME COLUMN order_id TO pedido_id;
            ALTER TABLE restaurant_orderitem RENAME COLUMN menu_item_id TO articulo_menu_id;
            """,
        ),
        
        # Rename category_id column if it still exists with old name
        migrations.RunSQL(
            sql="""
            ALTER TABLE restaurant_menuitem RENAME COLUMN categoria_id TO category_id;
            """,
            reverse_sql="""
            ALTER TABLE restaurant_menuitem RENAME COLUMN category_id TO categoria_id;
            """,
        ),
    ]

