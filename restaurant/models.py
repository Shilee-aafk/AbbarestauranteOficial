from django.db import models
from django.contrib.auth.models import User, Group
from django.conf import settings
import cloudinary.api
from .utils import get_cloudinary_url

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

    def save(self, *args, **kwargs):
        """Clean and validate data before saving"""
        # Limpiar espacios en blanco
        self.name = self.name.strip()
        self.category = self.category.strip()
        
        # Convert price to Decimal if it's a string
        if isinstance(self.price, str):
            from decimal import Decimal, InvalidOperation
            try:
                self.price = Decimal(self.price)
            except (InvalidOperation, ValueError):
                raise ValueError("El precio debe ser un número válido.")
        
        # Validar que el precio sea positivo
        if self.price < 0:
            raise ValueError("El precio no puede ser negativo.")
        
        super().save(*args, **kwargs)
    
    @property
    def image_url(self):
        """
        Get the image URL, handling both Cloudinary and local storage.
        Uses dynamic Cloudinary configuration from settings.
        """
        if not self.image:
            return None
        
        image_str = str(self.image)
        
        # If it's a Cloudinary reference, convert to URL using dynamic cloud_name
        if image_str.startswith('cloudinary:'):
            public_id = image_str.replace('cloudinary:', '')
            return get_cloudinary_url(public_id)
        
        # Otherwise return the image URL normally
        return self.image.url if self.image else None

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('preparing', 'En preparación'),
        ('ready', 'Listo'),
        ('served', 'Servido'),
        ('paid', 'Pagado'),
        ('charged_to_room', 'Cargado a Habitación'),
        ('cancelled', 'Cancelado'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Efectivo'),
        ('card', 'Tarjeta'),
        ('transfer', 'Transferencia'),
        ('check', 'Cheque'),
        ('mixed', 'Mixto'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room_number = models.CharField(max_length=10, blank=True, null=True, help_text="Guest room number")
    client_identifier = models.CharField(max_length=100, blank=True, null=True, help_text="Client identifier (e.g., 'Bar 1', 'John Doe')")
    items = models.ManyToManyField(MenuItem, through='OrderItem')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True, null=True)
    tip_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    paid_at = models.DateTimeField(null=True, blank=True, help_text="When the order was paid")
    payment_reference = models.CharField(max_length=100, blank=True, null=True, help_text="Reference for checks or transfers")

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

    def get_status_display(self):
        """Returns the status name in Spanish"""
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    def get_payment_method_display(self):
        """Returns the payment method name in Spanish"""
        return dict(self.PAYMENT_METHOD_CHOICES).get(self.payment_method, self.payment_method)

    def save(self, *args, **kwargs):
        """Clean and validate data before saving"""
        # Limpiar espacios en blanco de room_number y client_identifier
        if self.room_number:
            self.room_number = self.room_number.strip()
        if self.client_identifier:
            self.client_identifier = self.client_identifier.strip()
        
        # Validar que al menos uno de room_number o client_identifier esté presente
        if not self.room_number and not self.client_identifier:
            raise ValueError("Debe proporcionar al menos una habitación o un cliente.")
        
        super().save(*args, **kwargs)

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

class RoomBill(models.Model):
    """
    Agrupación de múltiples pedidos de una habitación para cobro conjunto.
    """
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmada'),
        ('paid', 'Pagada'),
        ('cancelled', 'Cancelada'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Efectivo'),
        ('card', 'Tarjeta'),
        ('transfer', 'Transferencia'),
        ('check', 'Cheque'),
        ('mixed', 'Mixto'),
    ]
    
    room_number = models.CharField(max_length=10, db_index=True)
    guest_name = models.CharField(max_length=100, blank=True, null=True)
    orders = models.ManyToManyField(Order, related_name='roombills')
    
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tip_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True, null=True)
    payment_reference = models.CharField(max_length=100, blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', db_index=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='roombills_created')
    
    class Meta:
        verbose_name = 'Room Bill'
        verbose_name_plural = 'Room Bills'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Bill {self.id} - Habitación {self.room_number}"
    
    def calculate_total(self):
        """Calcula el total de todas las órdenes asociadas"""
        from django.db.models import Sum
        total = self.orders.aggregate(total=Sum('total_amount'))['total'] or 0
        return total
    
    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)
    
    def get_payment_method_display(self):
        return dict(self.PAYMENT_METHOD_CHOICES).get(self.payment_method, self.payment_method)
    
    @property
    def status_class(self):
        return {
            'draft': 'bg-gray-100 text-gray-800',
            'confirmed': 'bg-yellow-100 text-yellow-800',
            'paid': 'bg-green-100 text-green-800',
            'cancelled': 'bg-red-100 text-red-800',
        }.get(self.status, 'bg-gray-100 text-gray-800')


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
