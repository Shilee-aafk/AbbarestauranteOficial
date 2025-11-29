from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import MenuItem, Order, OrderItem

# Clase personalizada para MenuItem
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'available', 'image_thumbnail')
    list_filter = ('category', 'available')
    search_fields = ('name', 'description')
    list_editable = ('available',)
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'description', 'category', 'price', 'available')
        }),
        ('Imagen del Plato', {
            'fields': ('image', 'image_preview'),
            'description': 'Sube una imagen del plato. Las imágenes se mostrarán en el menú público.'
        }),
    )
    readonly_fields = ('image_preview',)

    def image_thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="80" height="80" style="object-fit: cover; border-radius: 5px;" />',
                obj.image.url
            )
        return "—"
    image_thumbnail.short_description = "Imagen"

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="300" style="max-width: 100%; border-radius: 8px;" />',
                obj.image.url
            )
        return "Sin imagen — sube una arriba ☝️"
    image_preview.short_description = "Vista previa"

# Registrar modelos
admin.site.register(MenuItem, MenuItemAdmin)
admin.site.register(Order)
admin.site.register(OrderItem)


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_groups')

    def get_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])
    get_groups.short_description = 'Groups'

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
