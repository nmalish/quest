from django import template

register = template.Library()

@register.filter
def lookup(d, key):
    """Template filter to look up dictionary values by key"""
    return d.get(key)

@register.filter
def div(value, arg):
    """Template filter to divide two numbers"""
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def mul(value, arg):
    """Template filter to multiply two numbers"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def sub(value, arg):
    """Template filter to subtract two numbers"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0 