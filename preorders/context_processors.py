from .models import PreOrderCart


def preorder_cart_processor(request):
    if request.user.is_authenticated:
        cart_items_count = PreOrderCart.objects.filter(user=request.user).count()
        return {'preorder_cart_items_count': cart_items_count}
    return {}
