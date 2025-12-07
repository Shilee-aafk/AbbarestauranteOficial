from django.db import models
from django.contrib.auth.models import User, Group
import cloudinary.api

class Categoria(models.Model):
    """
    Categoría para agrupar los platos del menú.
    Valida que no existan categorías duplicadas (case-insensitive).
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Normalizar el nombre: trim y preservar mayúsculas como se escriba
        self.name = self.name.strip()
        super().save(*args, **kwargs)

class ArticuloMenu(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.CharField(max_length=50, default='General')
    available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='menu_items/', blank=True, null=True)

    class Meta:
        verbose_name = 'Artículo de Menú'
        verbose_name_plural = 'Artículos de Menú'

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

class Pedido(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('preparing', 'En Preparación'),
        ('ready', 'Listo'),
        ('served', 'Servido'),
        ('paid', 'Pagado'),
        ('charged_to_room', 'Cargado a Habitación'),
        ('cancelled', 'Cancelado'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room_number = models.CharField(max_length=10, blank=True, null=True, help_text="Número de habitación del huésped")
    client_identifier = models.CharField(max_length=100, help_text="Identificador del cliente (ej: 'Barra 1', 'Juan Pérez')", default='Pedido Antiguo')
    items = models.ManyToManyField(ArticuloMenu, through='ItemPedido')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    tip_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) # Nuevo campo para almacenar el total incluyendo la propina

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'

    def __str__(self):
        return f"Pedido {self.id} por {self.user.username}"

    def get_status_display(self):
        """Retorna el nombre en español del estado"""
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


class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    articulo_menu = models.ForeignKey(ArticuloMenu, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    note = models.TextField(blank=True, null=True)
    is_prepared = models.BooleanField(default=False, help_text="Marca si este item ya fue preparado/completado")

    class Meta:
        verbose_name = 'Item de Pedido'
        verbose_name_plural = 'Items de Pedidos'

    def __str__(self):
        return f"{self.quantity} x {self.articulo_menu.name}"

class PinRegistro(models.Model):
    """
    Un PIN de un solo uso para registrar nuevos usuarios con un rol específico.
    """
    pin = models.CharField(max_length=10, unique=True, help_text="PIN de registro de 10 caracteres.")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, help_text="El rol que se asignará al usuario.")
    created_at = models.DateTimeField(auto_now_add=True)
    used_by = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, help_text="Usuario que usó este PIN.")

    class Meta:
        verbose_name = 'PIN de Registro'
        verbose_name_plural = 'PINs de Registro'

    def __str__(self):
        status = "Usado" if self.used_by else "Activo"
        return f"PIN para '{self.group.name}' ({status})"
