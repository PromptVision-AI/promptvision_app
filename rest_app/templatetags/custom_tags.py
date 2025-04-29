from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def is_list(value):
    return isinstance(value, list)

@register.filter
def local_part(email: str) -> str:
    """
    Returns everything before the “@” in an email address.
    If no “@” is found, returns the original string.
    """
    try:
        return email.split('@', 1)[0]
    except (AttributeError, TypeError):
        return email