from django.db import models
from django.contrib.auth.models import User, Group

class Ingredient(models.Model):
    """Representa un ingrediente en el inventario."""
    name = models.CharField(max_length=100, unique=True)
    stock_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    unit = models.CharField(max_length=20, help_text="Ej: kg, litros, unidades")
    low_stock_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return f"{self.name} ({self.stock_quantity} {self.unit})"

    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.low_stock_threshold


class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, default='General')
    available = models.BooleanField(default=True)
    ingredients = models.ManyToManyField(Ingredient, through='RecipeIngredient', related_name='menu_items')

    def __str__(self):
        return self.name

class RecipeIngredient(models.Model):
    """Modelo intermedio para la receta de un MenuItem."""
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity_required = models.DecimalField(max_digits=10, decimal_places=3)

    class Meta:
        unique_together = ('menu_item', 'ingredient')

class Table(models.Model):
    number = models.IntegerField(unique=True)
    capacity = models.IntegerField()

    def __str__(self):
        return f"Table {self.number}"

class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    guests = models.IntegerField()

    def __str__(self):
        return f"Reservation for {self.user.username} on {self.date}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
        ('served', 'Served'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    items = models.ManyToManyField(MenuItem, through='OrderItem')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

    @property
    def status_class(self):
        return {
            'pending': 'bg-gray-100 text-gray-800',
            'preparing': 'bg-yellow-100 text-yellow-800',
            'ready': 'bg-green-100 text-green-800',
            'served': 'bg-blue-100 text-blue-800',
            'paid': 'bg-indigo-100 text-indigo-800',
            'cancelled': 'bg-red-100 text-red-800',
        }.get(self.status, 'bg-gray-100 text-gray-800')


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name}"

class RegistrationPin(models.Model):
    """
    Un PIN de un solo uso para registrar nuevos usuarios con un rol específico.
    """
    pin = models.CharField(max_length=10, unique=True, help_text="PIN de registro de 10 caracteres.")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, help_text="El rol que se asignará al usuario.")
    created_at = models.DateTimeField(auto_now_add=True)
    used_by = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, help_text="Usuario que usó este PIN.")

    def __str__(self):
        status = "Usado" if self.used_by else "Activo"
        return f"PIN para '{self.group.name}' ({status})"
