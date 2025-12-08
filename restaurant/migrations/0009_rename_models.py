# Migration to handle model renaming from Spanish to English

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0008_category_add'),
    ]

    operations = [
        # Rename table using database operations that work across different DBs
        migrations.RunSQL(
            # Forward: Rename old table to new table
            """
            ALTER TABLE restaurant_articulomenu RENAME TO restaurant_menuitem;
            ALTER TABLE restaurant_pedido RENAME TO restaurant_order;
            ALTER TABLE restaurant_itempedido RENAME TO restaurant_orderitem;
            ALTER TABLE restaurant_categoria RENAME TO restaurant_category;
            ALTER TABLE restaurant_pinregistro RENAME TO restaurant_registrationpin;
            """,
            # Reverse: Rename back to old table names (if we ever need to rollback)
            """
            ALTER TABLE restaurant_menuitem RENAME TO restaurant_articulomenu;
            ALTER TABLE restaurant_order RENAME TO restaurant_pedido;
            ALTER TABLE restaurant_orderitem RENAME TO restaurant_itempedido;
            ALTER TABLE restaurant_category RENAME TO restaurant_categoria;
            ALTER TABLE restaurant_registrationpin RENAME TO restaurant_pinregistro;
            """,
            # This migration is database-specific
            # For PostgreSQL compatibility
        ),
    ]

