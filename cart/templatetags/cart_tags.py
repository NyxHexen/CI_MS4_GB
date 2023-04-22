from django import template

register = template.Library()

@register.filter
def multiply(number, multiplier):
    """
    Multiply a given number by a given multiplier.
    Args:
        number (int or float): The number to be multiplied.
        multiplier (int or float): The multiplier to apply to the number.
    Returns:
        int or float: The result of multiplying the number by the multiplier.
    """
    return number * multiplier
