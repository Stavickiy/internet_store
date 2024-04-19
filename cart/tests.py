from django.contrib.messages import get_messages
from django.urls import reverse

from users.models import User
from vitamins.models import Category, Brand
from django.test import TestCase, Client




class CartViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')

        # Create instances of related models
        self.category = Category.objects.create(name='Supplements', slug='supplements')
        self.brand = Brand.objects.create(name='Nature Made', slug='nature-made')

        self.exchange_rate = ExchangeRate.objects.create(rate=1.0)
        self.delivery_cost = DeliveryCost.objects.create(cost_per_kg=1.0)

        # Now, create a Vitamin instance
        self.vitamin = Vitamin.objects.create(
            title="Test Vitamin",
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

        self.client = Client()

    def test_add_to_cart(self):
        self.client.login(username='testuser', password='12345')

        # Test adding a new product to the cart
        response = self.client.get(reverse('cart:add_to_cart', kwargs={'product_id': self.vitamin.id}))
        self.assertEqual(response.status_code, 302)  # Assuming a redirect to the cart detail page
        self.assertEqual(Cart.objects.count(), 1)
        self.assertEqual(Cart.objects.first().product, self.vitamin)

        # Test adding the same product again (should increase quantity)
        response = self.client.get(reverse('cart:add_to_cart', kwargs={'product_id': self.vitamin.id}))
        self.assertEqual(Cart.objects.first().quantity, 2)

        # Test adding a product with insufficient stock
        self.vitamin.count = 0
        self.vitamin.save()
        # Make the request and follow the redirect
        response = self.client.get(reverse('cart:add_to_cart', kwargs={'product_id': self.vitamin.id}), follow=True)

        # Now, response.context should be available, and you can access messages
        messages = list(response.context['messages'])

        # Assertions about the messages
        self.assertTrue(any("Недостаточное количество" in str(message) for message in messages))

    def test_remove_from_cart(self):
        self.client.login(username='testuser', password='12345')
        cart_item = Cart.objects.create(user=self.user, product=self.vitamin, quantity=1)

        # Test removing an item from the cart
        response = self.client.get(reverse('cart:remove_from_cart', kwargs={'cart_item_id': cart_item.id}))
        self.assertEqual(response.status_code, 302)  # Assuming a redirect to the cart detail page
        self.assertEqual(Cart.objects.count(), 0)

        # Test removing a non-existent item (should handle gracefully)
        response = self.client.get(reverse('cart:remove_from_cart', kwargs={'cart_item_id': 999}))
        self.assertEqual(response.status_code, 404)

    def test_cart_detail(self):
        self.client.login(username='testuser', password='12345')
        Cart.objects.create(user=self.user, product=self.vitamin, quantity=2)

        # Test viewing the cart with items
        response = self.client.get(reverse('cart:cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Vitamin")
        self.assertContains(response, "Корзина покупок")

        # Test viewing an empty cart
        Cart.objects.all().delete()
        response = self.client.get(reverse('cart:cart_detail'))
        self.assertNotContains(response, "Test Vitamin")
        self.assertContains(response, "Ваша корзина пуста!!!")


from django.test import TestCase, RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from .models import PromoCod, Cart, Vitamin
from vitamins.models import ExchangeRate, DeliveryCost
from .views import add_promo_cod


class PromoCodeTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Supplements', slug='supplements')
        self.brand = Brand.objects.create(name='Nature Made', slug='nature-made')
        self.exchange_rate = ExchangeRate.objects.create(rate=1.0)
        self.delivery_cost = DeliveryCost.objects.create(cost_per_kg=1.0)
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

        self.promo_code = PromoCod.objects.create(code="SAVE10", discount=10, is_active=True)
        self.vitamin = Vitamin.objects.create(
                        title="Vitamin A",
                        price=100,
                        count=20,
                        cat=self.category,
                        brand=self.brand,
                        weight=0.0,
                        percent=0,
                        product_code="VIT100",
                        packaging=1,
                        unit='bottle'
                    )
        self.cart_item = Cart.objects.create(user=self.user, product=self.vitamin, quantity=1)

        ExchangeRate.objects.create(rate=1.0)  # Assuming default rate is 1 for simplicity
        DeliveryCost.objects.create(cost_per_kg=1.0)  # Assuming default delivery cost is 1 for simplicity

    def apply_session_and_messages(self, request):
        middleware = SessionMiddleware(lambda x: x)
        middleware.process_request(request)
        request.session.save()

        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

    def test_add_valid_promo_code(self):
        request = self.factory.post('/add-promo-code/', {'promo_code': 'SAVE10'})
        request.user = self.user
        self.apply_session_and_messages(request)

        response = add_promo_cod(request)
        self.assertEqual(request.session['promo_code'], 'SAVE10')
        messages = [m.message for m in get_messages(request)]
        self.assertIn(f"Промокод {request.session['promo_code']} применен! Применена максимальная скидка, если на товар уже была скидка!", messages)  # Check your actual success message

    def test_add_invalid_promo_code(self):
        invalid_code = 'INVALID'
        request = self.factory.post('/add-promo-code/', {'promo_code': invalid_code})
        request.user = self.user
        self.apply_session_and_messages(request)

        response = add_promo_cod(request)
        # Check that if 'promo_code' is in session, it should not be the invalid code
        if 'promo_code' in request.session:
            self.assertNotEqual(request.session['promo_code'], invalid_code)

        messages = [m.message for m in get_messages(request)]
        self.assertIn("Не верный промокод!!!", messages)

    def test_promo_code_effect_on_cart(self):
        # Log in and set the promo code in the session
        self.client.login(username='testuser', password='12345')
        session = self.client.session
        session['promo_code'] = 'SAVE10'
        session.save()

        # Now make the request to the cart
        response = self.client.get('/cart/')  # Ensure this URL matches your actual cart URL

        # Check the context for the total price after discount
        self.assertIn('total_price', response.context)
        expected_total_price = 90  # Expected price after applying 10% discount on 100
        self.assertEqual(response.context['total_price'], expected_total_price)
