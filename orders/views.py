from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404
from django.db import transaction
from django.shortcuts import redirect
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.html import strip_tags, format_html

from cart.views import calculator_cart
from internet_store import settings
from orders.models import OrderItem, Order, TypeDelivery, TypePayment, OrderStatus

import logging


# We get the Django logger instance that was configured in settings.py
logger = logging.getLogger('django')


@login_required
def create_order_from_cart(request, shipping_address):
    """
    Creates an order from the items in the user's cart.

    Retrieves cart items, total price, total price without discount, discount, and promo code from the session.
    Checks the availability of all products in the cart before creating the order.
    Adds shipping cost if the selected delivery option is 'mail'.
    Creates an order with the provided shipping address, user details, and payment type.
    Creates order items for each product in the cart, updating their quantities and sold counts.
    Empties the cart and clears the promo code from the session after creating the order.

    Returns:
        Order: The created order instance.
    """

    cart_items, total_price, total_price_without_discount, discount, code_name = calculator_cart(request)
    # Check availability of all products before creating an order
    for item in cart_items:
        if item.product.count < item.quantity:
            raise ValueError(f"Недостаточно товара на складе для {item.product.title}")

    if request.session['delivery_option'] == 'mail':
        # add shipping cost
        total_price += 200

    with transaction.atomic():
        order = Order.objects.create(user=request.user,
                                     comment=request.session['comment'] if 'comment' in request.session else '',
                                     type_delivery=TypeDelivery.PICKUP if request.session['delivery_option'] == 'pickup' else TypeDelivery.POST,
                                     total_price=total_price,
                                     without_discount=total_price_without_discount,
                                     discount_sum=discount,
                                     shipping_address=shipping_address,
                                     type_payment=TypePayment.CASH if request.session['type_payment'] == 'cash' else TypePayment.BY_CARD,
                                     email=request.session['email'],
                                     phone_number=request.session['phone_number'])

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.final_price,
                sum=item.product.sum,
                discount=item.product.discount
            )
            # Reducing the quantity of products in stock
            item.product.decrease_count(item.quantity)
            item.product.adding_sold(item.quantity)

        # Empty cart after creating order
        cart_items.delete()
        request.session['promo_code'] = None
    return order


@login_required
def create_order(request):
    """
    Creates an order based on the user's session data and cart items.

    Attempts to create an order within a database transaction. If successful, sends a confirmation email to the user
    and redirects them to the orders history page. If an error occurs during the creation of the order, logs the error,
    displays an error message to the user, and redirects them back to the checkout page.
    """
    try:
        with transaction.atomic():
            shipping_address = '\n'.join([
                request.session['last_name'],
                request.session['first_name'],
                request.session['email'],
                request.session['phone_number']
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
            # Create order
            order = create_order_from_cart(request, shipping_address)

            messages.success(request, f'Поздравляем, ваш заказ создан успешно!')

            # Sending a confirmation email to the user
            subject = f'Ваш заказ #{order.id} успешно оформлен'
            # Forming an HTML link
            order_link = format_html('<a href="{}">#{}<a/>', order.get_absolute_url(), order.pk)
            message = format_html('Ваш заказ {} оформлен!!! В ближайшее время наш менеджер свяжется '
                                  'с вами для подтверждения заказа и уточнения деталей доставки.', order_link)
            html_message = render_to_string('email_template.html', {'order': order, 'message': message})
            plain_message = strip_tags(html_message)
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [order.email, settings.MY_EMAIL]
            send_mail(subject, plain_message, email_from, recipient_list, html_message=html_message)
            logger.debug(f'Заказ {order.id} успешно создан для пользователя {request.user.username}')

            return redirect('orders:orders_history')
    except ValueError as e:
        # Loging
        logger.error(f'Ошибка при создании заказа: {e}', exc_info=True)
        # Returning the user back to the cart with an error message
        messages.error(request, f'Произошла ошибка при создании заказа: {e}')
        return redirect('checkout4')


@login_required
def orders_history(request):
    """
    Displays the order history for the authenticated user.

    Retrieves the orders associated with the current user and renders them in the orders history page.
    """
    orders = Order.objects.filter(user=request.user)
    context = {
        'title': 'История заказов',
        'orders': orders
    }
    return render(request, 'orders/orders_history.html', context)


@login_required
def order_detail(request, order_id):
    """
    Displays the details of a specific order.

    Retrieves the order details and associated order items for the specified order ID.
    Renders the order details page with the order information and its items.
    """
    order = get_object_or_404(Order, pk=order_id)
    order_items = OrderItem.objects.filter(order__pk=order_id).select_related('product__brand')
    context = {
        'order': order,
        'order_items': order_items,
        'title': 'Детали заказа'
    }

    return render(request, 'orders/order_detail.html', context)


@login_required
def canceling_order(request, order_id):
    """
    Cancels a specific order.

    Cancels the order identified by the given order ID. It updates the order status to "CANCELED"
    and restores the quantity of each product in the order back to the stock.
    """
    try:
        with transaction.atomic():
            order = get_object_or_404(Order, pk=order_id)
            order_items = order.items.all()
            order.status = OrderStatus.CANCELED
            for item in order_items:
                item.product.adding_count(item.quantity)
            order.save()
            return redirect('orders:orders_history')
    except Exception as e:
        messages.error(request, 'Произошла ошибка при отмене заказа: {}'.format(e))
        return redirect('orders:orders_history')
