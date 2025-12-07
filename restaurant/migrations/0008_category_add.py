# Generated migration - Add Category model with proper data migration

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0007_menuitem_image'),
    ]

    operations = [
        # 1. Create the Category model
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'Categories',
                'ordering': ['name'],
            },
        ),
        
        # 2. Update Order model (just fix the field)
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('pending', 'Pendiente'), ('preparing', 'En Preparación'), ('ready', 'Listo'), ('served', 'Servido'), ('paid', 'Pagado'), ('charged_to_room', 'Cargado a Habitación'), ('cancelled', 'Cancelado')], default='pending', max_length=20),
        ),
    ]
