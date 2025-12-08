from django.db import models
from django.contrib.auth.models import User, Group
import cloudinary.api

class Category(models.Model):
    """
    Category to group menu dishes.
    Validates that there are no duplicate categories (case-insensitive).
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Normalizar el nombre: trim y preservar mayúsculas como se escriba
        self.name = self.name.strip()
        super().save(*args, **kwargs)

class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, default='General')
    available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='menu_items/', blank=True, null=True)

    class Meta:
        verbose_name = 'Menu Item'
        verbose_name_plural = 'Menu Items'

    def __str__(self):
        return self.name
    
    @property
    def image_url(self):
        """
        Get the image URL, handling both Cloudinary and local storage.
        """
        if not self.image:
            return None
        
        image_str = str(self.image)
        
        # If it's a Cloudinary reference, convert to URL
        if image_str.startswith('cloudinary:'):
            public_id = image_str.replace('cloudinary:', '')
            return f'https://res.cloudinary.com/dvjcrc3ei/image/upload/{public_id}'
        
        # Otherwise return the image URL normally
        return self.image.url if self.image else None

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
        ('served', 'Served'),
        ('paid', 'Paid'),
        ('charged_to_room', 'Charged to Room'),
        ('cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room_number = models.CharField(max_length=10, blank=True, null=True, help_text="Guest room number")
    client_identifier = models.CharField(max_length=100, help_text="Client identifier (e.g., 'Bar 1', 'John Doe')", default='Old Order')
    items = models.ManyToManyField(MenuItem, through='OrderItem')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    tip_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

    def get_status_display(self):
        """Returns the status name in English"""
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    @property
    def status_class(self):
        return {
            'pending': 'bg-gray-100 text-gray-800',
            'preparing': 'bg-yellow-100 text-yellow-800',
            'ready': 'bg-green-100 text-green-800',
            'served': 'bg-blue-100 text-blue-800',
            'paid': 'bg-indigo-100 text-indigo-800',
            'charged_to_room': 'bg-purple-100 text-purple-800',
            'cancelled': 'bg-red-100 text-red-800',
        }.get(self.status, 'bg-gray-100 text-gray-800')


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    note = models.TextField(blank=True, null=True)
    is_prepared = models.BooleanField(default=False, help_text="Mark if this item has been prepared/completed")

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name}"

class RegistrationPin(models.Model):
    """
    A single-use PIN to register new users with a specific role.
    """
    pin = models.CharField(max_length=10, unique=True, help_text="10-character registration PIN.")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, help_text="The role to be assigned to the user.")
    created_at = models.DateTimeField(auto_now_add=True)
    used_by = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, help_text="User who used this PIN.")

    class Meta:
        verbose_name = 'Registration PIN'
        verbose_name_plural = 'Registration PINs'

    def __str__(self):
        status = "Used" if self.used_by else "Active"
        return f"PIN for '{self.group.name}' ({status})"
