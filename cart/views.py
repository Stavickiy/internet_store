from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from vitamins.models import Vitamin, ExchangeRate, DeliveryCost
from vitamins.views import calculate_price
from .models import Cart, PromoCod


@login_required
def validate_promo(request):
    """
    Validates the entered promo code.

    Checks if the promo code exists in the database, if it is active,
    and if there are any restrictions on the cart total amount.
    If the promo code is valid, it is applied to the cart.

    Returns:
        bool: True if the promo code is valid and applied successfully, False otherwise.
    """
    cart_items = Cart.objects.filter(user=request.user)
    promo_code = request.session.get('promo_code')

    if not promo_code:
        messages.error(request, "Вы не ввели промокод!!!")
        return False

    try:
        promo_code_obj = PromoCod.objects.get(code=promo_code)
    except PromoCod.DoesNotExist:
        messages.error(request, "Не верный промокод!!!")
        return False

    if not promo_code_obj.is_active:
        messages.error(request, f"Промокод '{promo_code}' не активен!!!")
        return False

    total_cart_price = sum(item.quantity * calculate_price(item.product).final_price for item in cart_items)
    if promo_code_obj.min_sum and promo_code_obj.min_sum > total_cart_price:
        messages.error(request,
                       f"Общая сумма корзины должна быть не менее {promo_code_obj.min_sum}, чтобы применить промокод.")
        return False

    # Apply promo code
    request.session['promo_code'] = promo_code
    messages.success(request, f"Промокод {promo_code} применен! "
                              f"Применена максимальная скидка, если на товар уже была скидка!")
    return True


def calculator_cart(request):
    """
    Calculates the total price of the cart items, considering any applied promo code.
    """
    promo_code = None
    if validate_promo(request):
        promo_code = PromoCod.objects.get(code=request.session.get('promo_code'))

    cart_items = Cart.objects.filter(user=request.user).select_related('product__brand')
    for item in cart_items:
        if item.product.count < item.quantity or item.quantity < 1:
            item.quantity = item.product.count
            messages.error(request, f"Недостаточное количество: {item.product.title}!!!")
            messages.error(request, f"Доступное количество: {item.product.count}шт.")
            item.save()
        if promo_code:
            item.product.discount = max(item.product.discount, promo_code.discount)
        item.product = calculate_price(item.product)
        item.product.sum = (item.product.sale_price if item.product.discount else item.product.final_price) * item.quantity

    total_price = sum(item.product.sum for item in cart_items)
    total_price_without_discount = sum(item.quantity * item.product.final_price for item in cart_items)
    discount = total_price_without_discount - total_price
    return cart_items, total_price, total_price_without_discount, discount, promo_code.code if promo_code else ''


@login_required
def add_to_cart(request, product_id: int):
    """
    Adds a product to the user's cart or increases its quantity if it already exists.
    """
    product = get_object_or_404(Vitamin, pk=product_id)
    cart_item = Cart.objects.filter(user=request.user, product=product).first()

    if cart_item:
        if product.count - cart_item.quantity < 1:
            messages.error(request, f"Недостаточное количество: {product.title}!!!")
            messages.error(request, f"Доступное количество: {product.count}шт")
            return redirect("cart:cart_detail")

        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, "Количество товара увеличено.")

    else:
        if product.count == 0:
            messages.error(request, f"Недостаточное количество: {product.title}!!!")
            messages.error(request, f"Доступное количество: {product.count}шт")
            return redirect("cart:cart_detail")

        Cart.objects.create(user=request.user, product=product)
        messages.success(request, "Продукт добавлен в корзину.")

    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def remove_from_cart(request, cart_item_id: int):
    """
    Removes a product from the user's cart.
    """

    cart_item = get_object_or_404(Cart, id=cart_item_id)

    if cart_item.user == request.user:
        cart_item.delete()
        messages.success(request, "1 Продукт удален из вашей корзины.")

    return redirect("cart:cart_detail")


@login_required
def minus_from_cart(request, product_id):
    """
    Decreases the quantity of a product in the user's cart by 1.
    """

    cart_item = Cart.objects.filter(user=request.user, product=product_id).first()

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
        messages.success(request, "Количество товара уменьшено.")
    else:
        messages.error(request, "Количество товара в корзине не может быть меньше 1!!!")

    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def cart_detail(request):
    """
    Renders the cart detail page displaying cart items, calculates total price, discount,
    and handles availability checks.
    """
    cart_items, total_price, total_price_without_discount, discount, code_name = calculator_cart(request)

    context = {
        "cart_items": cart_items,
        "total_price": total_price,
        "total_price_without_discount": total_price_without_discount,
        'discount': discount,
        'title': 'Корзина покупок',
        'code_name': code_name
    }
    if not cart_items:
        messages.error(request, "Ваша корзина пуста!!!")
        return render(request, "cart/cart_detail.html", context)

    return render(request, "cart/cart_detail.html", context)


@login_required
def add_promo_cod(request):
    """
    Adds a promo code to the session if provided via POST request.
    """
    if request.method == 'POST':
        code = request.POST['promo_code']
        request.session['promo_code'] = code
    return cart_detail(request)


@login_required
def checkout1(request):
    """
    Displays the checkout page with a choice of delivery method.
    Displays order value amounts, discounts and promotional codes if there is one.
    """
    cart_items, total_price, total_price_without_discount, discount, code_name = calculator_cart(request)
    request.session['total_price'] = total_price
    request.session['total_price_without_discount'] = total_price_without_discount
    request.session['discount'] = discount
    context = {
        'title': 'Выбор способа получения заказа',
        "total_price": total_price,
        "total_price_without_discount": total_price_without_discount,
        'discount': discount,
        'code_name': request.session['promo_code'] if 'promo_code' in request.session else ''
    }
    return render(request, "cart/checkout1.html", context)


@login_required
def checkout2(request):
    """
    Displays the recipient data entry page depending on the delivery method.
    Adds shipping costs if sent by mail.
    """
    if request.method == 'POST':
        request.session['delivery_option'] = request.POST.get('delivery')  # 'pickup' или 'mail'
    if request.session['delivery_option'] == 'mail':
        request.session['total_price'] += 200
    context = {
        'title': 'Внесение данных к заказу',
        "total_price": request.session['total_price'],
        "total_price_without_discount": request.session['total_price_without_discount'],
        'discount': request.session['discount'],
        'code_name': request.session['promo_code'] if 'promo_code' in request.session else '',
        'delivery_option': request.session['delivery_option']
    }
    return render(request, "cart/checkout2.html", context)


@login_required
def checkout3(request):
    """
    Saves the recipient's data in the session.
    Displays the payment method selection page.
    """
    if request.method == 'POST':
        request.session['last_name'] = request.POST.get('lastname')
        request.session['first_name'] = request.POST.get('firstname')
        request.session['email'] = request.POST.get('email')
        request.session['phone_number'] = request.POST.get('phone')
        request.session['comment'] = request.POST.get('comment')
        if request.session['delivery_option'] == 'mail':
            request.session['middle_name'] = request.POST.get('middle_name')
            request.session['region'] = request.POST.get('region')
            request.session['city'] = request.POST.get('city')
            request.session['address'] = request.POST.get('street')
            request.session['postal_code'] = request.POST.get('zip')


    context = {
        'title': 'Способ оплаты',
        "total_price": request.session['total_price'],
        "total_price_without_discount": request.session['total_price_without_discount'],
        'discount': request.session['discount'],
        'code_name': request.session['promo_code'] if 'promo_code' in request.session else '',
        'delivery_option': request.session['delivery_option'],
    }

    return render(request, "cart/checkout3.html", context)


@login_required
def checkout4(request):
    """
    Saves the payment method.
    Displays the cart details check page.
    """
    request.session['type_payment'] = request.POST.get('payment')
    cart_items, total_price, total_price_without_discount, discount, code_name = calculator_cart(request)
    if request.session['delivery_option'] == 'mail':
        total_price += 200
    context = {
        "cart_items": cart_items,
        "total_price": total_price,
        "total_price_without_discount": total_price_without_discount,
        'discount': discount,
        'title': 'Проверка заказа перед оформлением',
        'code_name': code_name,
        'delivery_option': request.session['delivery_option']
    }

    return render(request, "cart/checkout4.html", context)
