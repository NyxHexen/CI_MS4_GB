from django import template

register = template.Library()

@register.filter
def multiply(number, multiplier):
    return number * multiplier
