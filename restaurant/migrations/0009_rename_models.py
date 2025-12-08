# Migration to handle model renaming from Spanish to English
# This migration is database-agnostic and works for both MySQL (local) and PostgreSQL (Render)

from django.db import migrations
from django.db import connection


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0008_category_add'),
    ]

    operations = [
        # For MySQL: Simple migration that doesn't use complex syntax
        # Tables and columns should already be named correctly based on models.py
        # This migration is mostly a no-op since the models already have English names
        migrations.RunSQL(
            sql="""
            -- This migration ensures database state matches the models
            -- For MySQL, we just acknowledge the migration
            SELECT 1;
            """,
            reverse_sql="SELECT 1;",
        ),
    ]

