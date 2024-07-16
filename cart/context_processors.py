from .models import Cart


def cart_processor(request):
    if request.user.is_authenticated:
        cart_items_count = Cart.objects.filter(user=request.user).count()
        return {'cart_items_count': cart_items_count}
    return {'cart_items_count': 0}
