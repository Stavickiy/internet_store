from django.db import models
from django.urls import reverse
from django_extensions.db.fields import AutoSlugField
from slugify import slugify

from users.models import User


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = AutoSlugField(populate_from='name', unique=True, max_length=200)

    def __str__(self):
        return self.name


class Vitamin(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    price = models.IntegerField(default=0)
    count = models.IntegerField(default=0)
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    discount = models.IntegerField(default=0)
    cat = models.ForeignKey('Category', on_delete=models.PROTECT, related_name='vitamins')
    slug = AutoSlugField(populate_from='title', max_length=300, slugify_function=slugify)
    tags = models.ManyToManyField(Tag, blank=True, related_name='vitamins')
    brand = models.ForeignKey('Brand', on_delete=models.PROTECT, blank=True,
                              default=None, null=True, related_name='vitamins')
    weight = models.FloatField(default=0)
    product_code = models.CharField(max_length=50, default=0, unique=True)

    packaging = models.PositiveIntegerField()
    unit = models.CharField(max_length=10)
    analog = models.ManyToManyField('Vitamin', blank=True, related_name='analog_set')
    short_content = models.TextField(blank=True, default=0)
    total_sold = models.IntegerField(default=0)
    percent = models.IntegerField(default=30)
    preorder_count = models.IntegerField(default=0)
    ordered = models.IntegerField(default=0, blank=True)
    arrival_date = models.DateField(default=None, null=True, blank=True)

    class Meta:
        ordering = ['-count', '-ordered', 'title']

    def get_absolute_url(self):
        brand_slug = self.brand.slug  # Используйте уже загруженный бренд
        return reverse('vitamin', kwargs={'brand_slug': brand_slug, 'vit_slug': self.slug})

    def __repr__(self):
        return self.title

    def __str__(self):
        return self.title

    def decrease_count(self, quantity):
        if self.count >= quantity:
            self.count -= quantity
            self.save()
        else:
            raise ValueError("Недостаточно товара на складе")

    def adding_count(self, quantity):
        self.count += quantity
        self.save()

    def adding_sold(self, quantity):
        self.total_sold += quantity
        self.save()

    def adding_preorder_count(self, quantity):
        self.preorder_count += quantity
        self.save()

    def decrease_preorder_count(self, quantity):
        if self.preorder_count >= quantity:
            self.preorder_count -= quantity
            self.save()


class VitaminImage(models.Model):
    vitamin = models.ForeignKey(Vitamin, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='vitamins_images/')
    is_main = models.BooleanField(default=False)

    class Meta:
        ordering = ['-is_main', 'image']


class Brand(models.Model):
    name = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    slug = AutoSlugField(populate_from='name', unique=True, max_length=300, slugify_function=slugify)
    image = models.ImageField(upload_to='brand_images/', null=True, default=None)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    slug = AutoSlugField(populate_from='name', unique=True, max_length=300, slugify_function=slugify)

    def get_absolut_url(self):
        return reverse('category', kwargs={'cat_slug': self.slug})

    def __str__(self):
        return self.name


class DeliveryRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    title = models.CharField(max_length=255)
    url = models.URLField()
    comment = models.TextField(max_length=500, blank=True, default=0)


class ExchangeRate(models.Model):
    rate = models.IntegerField(default=1)


class DeliveryCost(models.Model):
    cost_per_kg = models.IntegerField(default=1)


class Percent(models.Model):
    percent = models.IntegerField(default=30)
