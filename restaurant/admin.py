from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django import forms
from .models import ArticuloMenu, Pedido, ItemPedido, Categoria, PinRegistro

# Formulario personalizado para ArticuloMenu
class ArticuloMenuForm(forms.ModelForm):
    class Meta:
        model = ArticuloMenu
        fields = ['name', 'description', 'price', 'category', 'available', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'vTextField'}),
            'description': forms.Textarea(attrs={'class': 'vLargeTextField'}),
            'price': forms.NumberInput(attrs={'class': 'vDecimalField', 'step': '0.01'}),
            'category': forms.TextInput(attrs={'class': 'vTextField'}),
            'available': forms.CheckboxInput(attrs={'class': 'vCheckboxField'}),
            'image': forms.FileInput(attrs={'class': 'vFileField', 'accept': 'image/*'}),
        }

# Clase personalizada para ArticuloMenu
class ArticuloMenuAdmin(admin.ModelAdmin):
    form = ArticuloMenuForm
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
            'description': 'Sube una imagen del plato (JPG, PNG, WebP). Las imágenes se mostrarán en el menú público.'
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
admin.site.register(ArticuloMenu, ArticuloMenuAdmin)
admin.site.register(Pedido)
admin.site.register(ItemPedido)
admin.site.register(Categoria)
admin.site.register(PinRegistro)


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_groups')

    def get_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])
    get_groups.short_description = 'Groups'

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)