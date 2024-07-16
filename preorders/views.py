from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.html import format_html, strip_tags

from internet_store import settings
from preorders.models import PreOrderCart, PreOrder, TypeDelivery, PreOrderItem, OrderStatus
from vitamins.models import Vitamin, ExchangeRate, DeliveryCost
from vitamins.views import calculate_price
import logging

# We get the Django logger instance that was configured in settings.py
logger = logging.getLogger('django')


def calculator_preorder_cart(request):
    """
    Calculates the total price of the preorders cart items.
    """
    cart_items = PreOrderCart.objects.filter(user=request.user).select_related('product__brand')
    exchange_rate = ExchangeRate.objects.all().first().rate
    delivery_cost = DeliveryCost.objects.all().first().cost_per_kg
    for item in cart_items:
        item.product = calculate_price(item.product, exchange_rate, delivery_cost)
        item.product.sum = (item.product.sale_price if item.product.discount else item.product.final_price) * item.quantity

    total_price = sum(item.product.sum for item in cart_items)
    total_price_without_discount = sum(item.quantity * item.product.final_price for item in cart_items)
    discount = total_price_without_discount - total_price
    return cart_items, total_price, total_price_without_discount, discount


@login_required
def add_to_preorder_cart(request, product_id: int):
    """
    Adds a product to the user's preorders cart.
    """
    cart_item = PreOrderCart.objects.filter(user=request.user, product=product_id).first()
    product = Vitamin.objects.get(pk=product_id)
    if cart_item:
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, "Количество товара увеличено.")

    else:
        PreOrderCart.objects.create(user=request.user, product=product)
        messages.success(request, "Продукт добавлен в корзину предзаказа.")

    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def remove_from_preorder_cart(request, cart_item_id: int):
    """
    Removes a product from the user's preorders cart.
    """
    cart_item = get_object_or_404(PreOrderCart, id=cart_item_id)

    if cart_item.user == request.user:
        cart_item.delete()
        messages.success(request, "1 Продукт удален из корзины предзаказа.")

    return redirect("preorders:preorder_cart_detail")


@login_required
def minus_from_preorder_cart(request, product_id: int):
    """
    Decreases the quantity of a product in the user's preorders cart by 1.
    """
    cart_item = PreOrderCart.objects.filter(user=request.user, product=product_id).first()
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
        messages.success(request, "Количество товара уменьшено.")
    else:
        messages.error(request, "Количество товара в корине предзаказа не может быть меньше 1!!!.")

    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def preorder_cart_detail(request):
    """
    Renders the preorders cart detail page displaying preorders cart items, calculates total price, discount,
    and handles availability checks.
    """

    cart_items, total_price, total_price_without_discount, discount = calculator_preorder_cart(request)
    context = {
        "cart_items": cart_items,
        "total_price": total_price,
        "total_price_without_discount": total_price_without_discount,
        'discount': discount,
        'title': 'Корзина Предзаказа',
    }
    if not cart_items:
        messages.error(request, "Ваша корзина предзаказа пуста!!!.")
        return render(request, "preorders/cart_detail.html", context)
    return render(request, "preorders/cart_detail.html", context)


@login_required
def checkout1(request):
    """
    Displays the checkout page with a choice of delivery method.
    Displays order value amounts, discounts and promotional codes if there is one.
    """
    cart_items, total_price, total_price_without_discount, discount = calculator_preorder_cart(request)
    request.session['total_price'] = total_price
    request.session['total_price_without_discount'] = total_price_without_discount
    request.session['discount'] = discount
    context = {
        'title': 'Выбор способа получения заказа',
        "total_price": total_price,
        "total_price_without_discount": total_price_without_discount,
        'discount': discount,
    }
    return render(request, "preorders/checkout1.html", context)


@login_required
def checkout2(request):
    """
    Displays the recipient data entry page depending on the delivery method.
    Adds shipping costs if sent by mail.
    """
    if request.method == 'POST':
        request.session['delivery_option'] = request.POST.get('delivery')
    if request.session['delivery_option'] == 'mail':
        request.session['total_price'] += 200
    context = {
        'title': 'Внесение данных к предзаказу',
        "total_price": request.session['total_price'],
        "total_price_without_discount": request.session['total_price_without_discount'],
        'discount': request.session['discount'],
        'delivery_option': request.session['delivery_option']
    }
    return render(request, "preorders/checkout2.html", context)


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
        'delivery_option': request.session['delivery_option'],
    }

    return render(request, "preorders/checkout3.html", context)


@login_required
def checkout4(request):
    """
    Saves the payment method.
    Displays the preorders cart details check page.
    """
    request.session['type_payment'] = request.POST.get('payment')
    cart_items, total_price, total_price_without_discount, discount = calculator_preorder_cart(request)
    if request.session['delivery_option'] == 'mail':
        total_price += 200
    context = {
        "cart_items": cart_items,
        "total_price": total_price,
        "total_price_without_discount": total_price_without_discount,
        'discount': discount,
        'title': 'Проверка предзаказа перед оформлением',
        'delivery_option': request.session['delivery_option']
    }

    return render(request, "preorders/checkout4.html", context)


@login_required
def create_order_from_cart(request, shipping_address: str):
    """
    Creates an preorder from the items in the user's cart.

    Retrieves preorders cart items, total price, total price without discount, discount from the session.
    Adds shipping cost if the selected delivery option is 'mail'.
    Creates an order with the provided shipping address, user details, and payment type.
    Creates order items for each product in the cart.
    Empties the preorders cart after creating the order.

    Returns:
        PreOrder: The created order instance.
    """
    cart_items, total_price, total_price_without_discount, discount = calculator_preorder_cart(request)
    if request.session['delivery_option'] == 'mail':
        # add shipping cost
        total_price += 200

    with transaction.atomic():
        order = PreOrder.objects.create(user=request.user,
                                        comment=request.session['comment'],
                                        type_delivery=TypeDelivery.PICKUP if request.session[
                                                                                 'delivery_option'] == 'pickup' else TypeDelivery.POST,
                                        total_price=total_price,
                                        without_discount=total_price_without_discount,
                                        discount_sum=discount,
                                        shipping_address=shipping_address,
                                        email=request.session['email'],
                                        phone_number=request.session['phone_number']
                                        )
        for item in cart_items:
            PreOrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.final_price,
                sum=item.product.sum,
                discount=item.product.discount
            )
            # Reducing the quantity of products in stock
            item.product.adding_preorder_count(item.quantity)
            item.product.adding_sold(item.quantity)
        # Empty preorders cart after creating preorder
        cart_items.delete()
    return order


@login_required
def create_preorder(request):
    """
    Creates an preorder based on the user's session data and cart items.

    Attempts to create an preorder within a database transaction. If successful, sends a confirmation email to the user
    and redirects them to the preorders history page. If an error occurs during the creation of the preorder,
    logs the error, displays an error message to the user, and redirects them back to the checkout page.
    """
    try:
        with transaction.atomic():
            shipping_address = '\n'.join([
                                             request.session['last_name'],
                                             request.session['first_name'],
                                             request.session['email'],
                                             request.session['phone_number'],
                                             request.session['comment']
                                         ] if request.session['delivery_option'] == 'pickup' else [
                request.session['last_name'],
                request.session['first_name'],
                request.session['middle_name'],
                request.session['email'],
                request.session['phone_number'],
                request.session['region'],
                request.session['city'],
                request.session['address'],
                request.session['postal_code'],
                request.session['comment']
            ])
            # Create preorder
            order = create_order_from_cart(request, shipping_address)

            messages.success(request, f'Поздравляем, ваш предзаказ успешно создан!')

            # Sending a confirmation email to the user
            subject = f'Ваш предзаказ #{order.id} успешно оформлен'
            # Forming an HTML link
            order_link = format_html('<a href="{}">#{}<a/>', order.get_absolute_url(), order.pk)
            message = format_html(
                'Ваш предзаказ {} оформлен!!! В ближайшее время наш менеджер свяжется с вами для подтверждения пердзаказа и уточнения деталей доставки.',
                order_link)
            html_message = render_to_string('email_template.html', {'message': message})
            plain_message = strip_tags(html_message)
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [order.email, settings.MY_EMAIL]
            send_mail(subject, plain_message, email_from, recipient_list, html_message=html_message)

            return redirect('preorders:preorders_history')

    except ValueError as e:
        # Loging
        logger.error(f'Ошибка при создании заказа: {e}', exc_info=True)
        # Returning the user back to the cart with an error message
        messages.error(request, 'Произошла ошибка при создании предзаказа: {}'.format(e))
        return redirect('checkout4')


@login_required
def preorders_history(request):
    """
    Displays the preorder history for the authenticated user.

    Retrieves the preorders associated with the current user and renders them in the preorders history page.
    """
    orders = PreOrder.objects.filter(user=request.user)

    context = {
        'title': 'История предзаказов',
        'orders': orders
    }
    return render(request, 'preorders/preorders_history.html', context)


@login_required
def preorder_detail(request, order_id: int):
    """
    Displays the details of a specific preorder.

    Retrieves the preorder details and associated order items for the specified preorder ID.
    Renders the order details page with the order information and its items.
    """
    order = get_object_or_404(PreOrder, pk=order_id)
    order_items = PreOrderItem.objects.filter(order__pk=order_id).select_related('product__brand')
    context = {
        'order': order,
        'order_items': order_items,
        'title': 'Детали предзаказа'
    }

    return render(request, 'preorders/preorder_detail.html', context)


@login_required
def canceling_preorder(request, order_id: int):
    """
    Cancels a specific preorder.

    Cancels the preorder identified by the given preorder ID. It updates the order status to "CANCELED"
    and restores the quantity of each product in the order back to the stock.
    """
    try:
        with transaction.atomic():
            order = get_object_or_404(PreOrder, pk=order_id)
            order_items = order.items.all()
            order.status = OrderStatus.CANCELED
            for item in order_items:
                item.product.decrease_preorder_count(item.quantity)
            order.save()
            return redirect('preorders:preorders_history')
    except Exception as e:
        messages.error(request, 'Произошла ошибка при отмене предзаказа: {}'.format(e))
        return redirect('preorders:preorders_history')
