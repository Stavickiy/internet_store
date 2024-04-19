from django.test import TestCase, Client
from django.urls import reverse

from users.models import User
from .models import Vitamin, Order, OrderItem, OrderStatus
from vitamins.models import ExchangeRate, DeliveryCost, Category, Brand
from cart.models import Cart, PromoCod
from django.contrib.messages import get_messages


class OrderTestCase(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = Client()
        self.client.login(username='testuser', password='testpass')

        # Create necessary objects
        self.category = Category.objects.create(name='Supplements', slug='supplements')
        self.brand = Brand.objects.create(name='Nature Made', slug='nature-made')

        self.exchange_rate = ExchangeRate.objects.create(rate=1.0)
        self.delivery_cost = DeliveryCost.objects.create(cost_per_kg=1.0)
        self.vitamin = Vitamin.objects.create(
                        title="Vitamin A",
                        price=100,
                        count=10,
                        discount=10,
                        cat=self.category,
                        brand=self.brand,
                        weight=0.5,
                        product_code="VIT100",
                        packaging=1,
                        unit='bottle'
                    )
        Cart.objects.create(user=self.user, product=self.vitamin, quantity=2)
        self.promo_code = PromoCod.objects.create(code="DISCOUNT10", discount=10, is_active=True, min_sum=50)

        # Set session data for delivery option and address
        session = self.client.session
        session['delivery_option'] = 'mail'
        session['last_name'] = 'test'
        session['first_name'] = 'test'
        session['middle_name'] = 'test'
        session['phone_number'] = 'test'
        session['region'] = 'test'
        session['city'] = 'test'
        session['address'] = 'test'
        session['postal_code'] = 'test'
        session['comment'] = 'Test comment'
        session['type_payment'] = 'cash'
        session['promo_code'] = 'DISCOUNT10'
        session.save()

    def test_create_order_success(self):
        # Assume 'create_order' is mapped to '/create-order/' URL
        response = self.client.post(reverse('orders:create_order'), follow=True)

        # Check the order was created successfully
        self.assertEqual(Order.objects.count(), 1)
        order_item = OrderItem.objects.first()
        self.assertEqual(order_item.quantity, 2)

        # Check for success message
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('Поздравляем, ваш заказ создан успешно!', messages)

        # Check if cart is empty after order creation
        self.assertEqual(Cart.objects.count(), 0)

    def test_create_order_with_stock_adjustment(self):
        # Reduce the stock of the product to simulate insufficient stock
        self.vitamin.count = 1
        self.vitamin.save()

        # Trigger order creation
        response = self.client.post(reverse('orders:create_order'), follow=True)

        # Check that the order was created successfully
        self.assertEqual(Order.objects.count(), 1)

        # There should still be only one OrderItem, but with adjusted quantity
        self.assertEqual(OrderItem.objects.count(), 1)
        order_item = OrderItem.objects.first()
        self.assertEqual(order_item.quantity, 1)  # Adjusted to available stock

        # Check for any messages that might be added in this scenario
        messages = [m.message for m in get_messages(response.wsgi_request)]
        # Add an assertion for a specific message if your view sends one in this case

        # Cart should be cleared after order creation
        self.assertEqual(Cart.objects.count(), 0)


class OrderCancellationTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'password123')
        self.client.login(username='testuser', password='password123')

        # Create a vitamin and order with order items
        # Create necessary objects
        self.category = Category.objects.create(name='Supplements', slug='supplements')
        self.brand = Brand.objects.create(name='Nature Made', slug='nature-made')

        self.exchange_rate = ExchangeRate.objects.create(rate=1.0)
        self.delivery_cost = DeliveryCost.objects.create(cost_per_kg=1.0)
        self.vitamin = Vitamin.objects.create(
            title="Vitamin A",
            price=100,
            count=10,
            discount=10,
            cat=self.category,
            brand=self.brand,
            weight=0.5,
            product_code="VIT100",
            packaging=1,
            unit='bottle'
        )
        self.order = Order.objects.create(user=self.user, status=OrderStatus.NEW)
        self.order_item = OrderItem.objects.create(order=self.order, product=self.vitamin, quantity=5, price=10)

    def test_order_cancellation(self):
        initial_count = self.vitamin.count

        response = self.client.post(reverse('orders:canceling_order', kwargs={'order_id': self.order.id}))

        # Refresh the instances from the database to get updated values
        self.order.refresh_from_db()
        self.vitamin.refresh_from_db()

        # Verify the order status is updated
        self.assertEqual(self.order.status, OrderStatus.CANCELED)

        # Verify the product count is incremented by the canceled quantity
        self.assertEqual(self.vitamin.count, initial_count + self.order_item.quantity)

        # Verify the user is redirected to the orders history page
        self.assertRedirects(response, reverse('orders:orders_history'))

    def test_order_cancellation_with_invalid_order(self):
        # Use an invalid order ID
        response = self.client.get(reverse('canceling_order', kwargs={'order_id': 9999}), follow=True)

        # Check for error message
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('Произошла ошибка при отмене заказа', messages)

        # Verify redirection to the orders history page
        self.assertRedirects(response, reverse('orders:orders_history'))
