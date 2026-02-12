from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary using the key."""
    if dictionary is None:
        return []
    try:
        return dictionary.get(int(key), [])
    except (ValueError, AttributeError):
        return []

@register.filter
def split(value, arg):
    """Split a string by the given argument."""
    return value.split(arg)
