# Migration to handle model renaming from Spanish to English
# This migration renames database tables and columns
# NOTE: For PostgreSQL (production on Render)
# This migration is idempotent - it won't fail if columns are already renamed

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0008_category_add'),
    ]

    operations = [
        # Try to rename columns, but only if they exist with the old names
        # PostgreSQL: Use conditional syntax
        migrations.RunSQL(
            sql="""
            -- Rename columns in restaurant_orderitem table if they still have old names
            DO $$ 
            BEGIN
                -- Check if pedido_id exists and rename it
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'restaurant_orderitem' AND column_name = 'pedido_id'
                ) THEN
                    ALTER TABLE restaurant_orderitem RENAME COLUMN pedido_id TO order_id;
                END IF;
                
                -- Check if articulo_menu_id exists and rename it
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'restaurant_orderitem' AND column_name = 'articulo_menu_id'
                ) THEN
                    ALTER TABLE restaurant_orderitem RENAME COLUMN articulo_menu_id TO menu_item_id;
                END IF;
            END $$;
            
            -- Rename categoria_id if it exists in restaurant_menuitem
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'restaurant_menuitem' AND column_name = 'categoria_id'
                ) THEN
                    ALTER TABLE restaurant_menuitem RENAME COLUMN categoria_id TO category_id;
                END IF;
            END $$;
            """,
            reverse_sql="",
        ),
    ]

