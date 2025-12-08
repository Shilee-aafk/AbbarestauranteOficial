from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django import forms
from .models import MenuItem, Order, OrderItem, Category, RegistrationPin

# Custom form for MenuItem
class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['name', 'description', 'price', 'category', 'available', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'vTextField'}),
            'description': forms.Textarea(attrs={'class': 'vLargeTextField'}),
            'price': forms.NumberInput(attrs={'class': 'vDecimalField', 'step': '0.01'}),
            'category': forms.TextInput(attrs={'class': 'vTextField'}),
            'available': forms.CheckboxInput(attrs={'class': 'vCheckboxField'}),
            'image': forms.FileInput(attrs={'class': 'vFileField', 'accept': 'image/*'}),
        }

# Custom class for MenuItem
class MenuItemAdmin(admin.ModelAdmin):
    form = MenuItemForm
    list_display = ('name', 'category', 'price', 'available', 'image_thumbnail')
    list_filter = ('category', 'available')
    search_fields = ('name', 'description')
    list_editable = ('available',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category', 'price', 'available')
        }),
        ('Dish Image', {
            'fields': ('image', 'image_preview'),
            'description': 'Upload an image of the dish (JPG, PNG, WebP). Images will be shown in the public menu.'
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
    image_thumbnail.short_description = "Image"

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="300" style="max-width: 100%; border-radius: 8px;" />',
                obj.image.url
            )
        return "No image — upload one above ☝️"
    image_preview.short_description = "Preview"

# Register models
admin.site.register(MenuItem, MenuItemAdmin)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Category)
admin.site.register(RegistrationPin)


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_groups')

    def get_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])
    get_groups.short_description = 'Groups'

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)