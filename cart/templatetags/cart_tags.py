from django import template

register = template.Library()


@register.filter(name='has_zero_quantity')
def has_zero_quantity(cart_items):
    return any(item.quantity == 0 for item in cart_items)
