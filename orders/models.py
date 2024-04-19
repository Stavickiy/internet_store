from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse

from vitamins.models import Vitamin


class OrderStatus(models.TextChoices):
    NEW = 'new', 'Новый'
    PROCESSING = 'processing', 'В обработке'
    SHIPPED = 'shipped', 'Отправлен'
    READY = 'ready for issue', 'Готов к выдаче'
    EXECUTED = 'executed', 'Выполнен'
    CANCELED = 'canceled', 'Отменен'


class TypeDelivery(models.TextChoices):
    PICKUP = 'pickup', 'Самовывоз'
    POST = 'mail', 'Отправка почтой'


class TypePayment(models.TextChoices):
    CASH = 'cash', 'Наличные'
    BY_CARD = 'by_card', 'На банковскую карту'


class PaymentStatus(models.TextChoices):
    UNPAID = 'unpaid', 'Не оплачен'
    PAID = 'paid', 'Оплачен'


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.NEW)
    comment = models.TextField(blank=True)
    type_delivery = models.CharField(max_length=20, choices=TypeDelivery.choices, default=TypeDelivery.PICKUP)
    total_price = models.IntegerField(default=0)
    without_discount = models.IntegerField(default=0)
    discount_sum = models.IntegerField(default=0)
    shipping_address = models.TextField(max_length=1000)
    type_payment = models.CharField(max_length=20, choices=TypePayment.choices, default=TypePayment.CASH)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.UNPAID)
    email = models.EmailField(max_length=100, default=0)
    phone_number = models.CharField(max_length=12, default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Заказ {self.id}'

    def get_absolute_url(self):
        pk = self.pk
        return reverse('orders:order_detail', kwargs={'order_id': pk})


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Vitamin, on_delete=models.DO_NOTHING)
    quantity = models.IntegerField(default=1)
    price = models.IntegerField(default=0)  # Цена на момент оформления заказа
    sum = models.IntegerField(default=0)
    discount = models.IntegerField(default=0)  # Скидка на момент оформления заказа

    def __str__(self):
        return f"{self.quantity} x {self.product}"

    def get_total_price(self):
        return self.quantity * self.price - self.discount


postal_code_validator = RegexValidator(
    regex=r'^\d{6}$',
    message="Почтовый индекс должен состоять из 6 цифр."
)
