from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Obtiene un valor de un diccionario usando una clave.
    Ejemplo: {{ my_dict|get_item:my_key }}
    """
    if not isinstance(dictionary, dict):
        return ''
    return dictionary.get(key, dictionary.get('otros', 'fas fa-utensils'))
