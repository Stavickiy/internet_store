from django.db import models

from django.urls import reverse

from internet_store import settings
from vitamins.models import Vitamin


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Vitamin, on_delete=models.DO_NOTHING)
    quantity = models.IntegerField(default=1)
    time_added = models.DateTimeField(auto_now_add=True, null=True)
    promo_code = models.ForeignKey('PromoCod', on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:
        ordering = ['time_added']

    def __str__(self):
        return f"{self.quantity} x {self.product}"

    def get_absolute_url(self):
        return reverse("cart:cart_detail")


class PromoCod(models.Model):
    code = models.CharField(max_length=20, default=0, unique=True)
    is_active = models.BooleanField(default=False)
    discount = models.IntegerField(default=0)
    min_sum = models.IntegerField(default=0)

    def __str__(self):
        return self.code
