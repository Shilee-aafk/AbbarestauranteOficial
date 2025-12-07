#!/usr/bin/env python
import re
import os

files_to_update = [
    'restaurant/views.py',
    'restaurant/forms.py',
    'restaurant/management/commands/setup_permissions.py',
]

replacements = [
    # Imports y clases
    ('from .models import Order, OrderItem, MenuItem, Group, RegistrationPin, Category', 
     'from .models import Pedido, ItemPedido, ArticuloMenu, Group, PinRegistro, Categoria'),
    
    # Métodos y atributos
    ('Order.objects', 'Pedido.objects'),
    ('MenuItem.objects', 'ArticuloMenu.objects'),
    ('OrderItem.objects', 'ItemPedido.objects'),
    ('RegistrationPin.objects', 'PinRegistro.objects'),
    ('Category.objects', 'Categoria.objects'),
    
    # Relaciones
    ('orderitem_set', 'itempedido_set'),
    ('order.orderitem_set', 'pedido.itempedido_set'),
    ('order.', 'pedido.'),
    ('menu_item.', 'articulo_menu.'),
    ('orderitem', 'item_pedido'),
    ('menu_item', 'articulo_menu'),
    
    # Strings de referencia a modelos
    ('\'Order\'', "'Pedido'"),
    ('"Order"', '"Pedido"'),
    ('\'MenuItem\'', "'ArticuloMenu'"),
    ('"MenuItem"', '"ArticuloMenu"'),
    ('\'OrderItem\'', "'ItemPedido'"),
    ('"OrderItem"', '"ItemPedido"'),
    ('\'RegistrationPin\'', "'PinRegistro'"),
    ('"RegistrationPin"', '"PinRegistro"'),
    ('\'Category\'', "'Categoria'"),
    ('"Category"', '"Categoria"'),
]

for filepath in files_to_update:
    full_path = os.path.join('c:\\Users\\kamil\\Desktop\\Proyecto\\AbbarestauranteOficial', filepath)
    
    if not os.path.exists(full_path):
        print(f"⚠️ Archivo no encontrado: {filepath}")
        continue
    
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    for old, new in replacements:
        content = content.replace(old, new)
    
    if content != original_content:
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ {filepath} actualizado")
    else:
        print(f"⚠️ {filepath} sin cambios")

print("\n✅ Proceso de renombre completado")
