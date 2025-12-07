#!/usr/bin/env python
import re

# Leer el archivo
with open('c:\\Users\\kamil\\Desktop\\Proyecto\\AbbarestauranteOficial\\restaurant\\views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Reemplazos MÁS ESPECÍFICOS
replacements = [
    # Imports
    ('from .models import Order, OrderItem, MenuItem, Group, RegistrationPin, Category',
     'from .models import Pedido, ItemPedido, ArticuloMenu, Group, PinRegistro, Categoria'),
    
    # Nombres de clase a inicio de línea o después de espacios/paréntesis
    (r'\bOrder\.objects\.all\(\)', 'Pedido.objects.all()'),
    (r'\bOrder\.objects\.get\(', 'Pedido.objects.get('),
    (r'\bOrder\.objects\.filter\(', 'Pedido.objects.filter('),
    (r'\bMenuItem\.objects\.all\(\)', 'ArticuloMenu.objects.all()'),
    (r'\bMenuItem\.objects\.get\(', 'ArticuloMenu.objects.get('),
    (r'\bMenuItem\.objects\.filter\(', 'ArticuloMenu.objects.filter('),
    (r'\bOrderItem\.objects\.create\(', 'ItemPedido.objects.create('),
    (r'\bOrderItem\.objects\.get\(', 'ItemPedido.objects.get('),
    (r'\bRegistrationPin\.objects\.get\(', 'PinRegistro.objects.get('),
    (r'\bRegistrationPin\.objects\.filter\(', 'PinRegistro.objects.filter('),
    (r'\bCategory\.objects\.all\(\)', 'Categoria.objects.all()'),
    
    # Objetos Order/MenuItem (donde NO están en función)
    (r'\border = Order\(', 'pedido = Pedido('),
    (r'\border = (?!.*\()', 'pedido = '),  # variable assignment
    (r'\.orderitem_set\.all\(\)', '.itempedido_set.all()'),
    (r'\.menu_item\.', '.articulo_menu.'),
    (r'menu_item:', 'articulo_menu:'),
    (r'menu_item,', 'articulo_menu,'),
    (r'menu_item )', 'articulo_menu )'),
    (r'item\.menu_item', 'item.articulo_menu'),
    (r'order\(', 'pedido('),
    (r'except Order\.DoesNotExist', 'except Pedido.DoesNotExist'),
    (r'except MenuItem\.DoesNotExist', 'except ArticuloMenu.DoesNotExist'),
    (r'except OrderItem\.DoesNotExist', 'except ItemPedido.DoesNotExist'),
    
    # Strings
    (r"'Order'", "'Pedido'"),
    (r'"Order"', '"Pedido"'),
    (r"'MenuItem'", "'ArticuloMenu'"),
    (r'"MenuItem"', '"ArticuloMenu"'),
    (r"'OrderItem'", "'ItemPedido'"),
    (r'"OrderItem"', '"ItemPedido"'),
]

for old, new in replacements:
    content = re.sub(old, new, content)

# Escribir el archivo actualizado
with open('c:\\Users\\kamil\\Desktop\\Proyecto\\AbbarestauranteOficial\\restaurant\\views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ views.py actualizado')
