from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Vitamin, Brand, Category, Tag, ExchangeRate, DeliveryCost, VitaminImage, Percent, DeliveryRequest


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    list_display_links = ('id', 'name')


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'brand_photo')
    list_display_links = ('id', 'name')
    fields = ('name', 'brand_photo', 'image')
    readonly_fields = ['slug', 'brand_photo']

    @admin.display(description='Added image')
    def brand_photo(self, brand: Brand):
        return mark_safe(
            f"<a href='{brand.image.url}'><img src='{brand.image.url}' alt='{brand.name}' width='200'></a>")


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('rate',)


@admin.register(DeliveryCost)
class DeliveryCostAdmin(admin.ModelAdmin):
    list_display = ('cost_per_kg',)


@admin.register(Percent)
class PercentAdmin(admin.ModelAdmin):
    list_display = ('percent',)


@admin.register(VitaminImage)
class VitaminImageAdmin(admin.ModelAdmin):
    list_display = ('vitamin', 'image', 'is_main')


@admin.register(Vitamin)
class VitaminAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'brand', 'count', 'ordered', 'arrival_date', 'preorder_count', 'total_sold', 'price', 'percent',
                    'discount', 'vitamin_photo', 'cat', 'product_code')
    list_display_links = ('id', 'title')
    list_editable = ('discount', 'count', 'percent', 'total_sold')
    fields = ['title', 'brand', 'price', 'discount', 'percent', 'count', 'ordered', 'arrival_date', 'preorder_count', 'cat', 'tags',
              'weight', 'packaging', 'unit', 'product_code', 'total_sold', 'vitamin_photo',
              'analog', 'slug', 'short_content', 'content']
    ordering = ['time_create', 'title']
    filter_horizontal = ('tags', 'analog')
    list_per_page = 7
    list_filter = ['discount', 'cat__name', 'brand__name']
    search_fields = ['title', 'brand__name', 'cat__name']
    readonly_fields = ['slug', 'vitamin_photo']
    save_on_top = True

    @admin.display(description='Added image')
    def vitamin_photo(self, vitamin: Vitamin):
        return mark_safe(
            f"<a href='{vitamin.images.first().image.url if vitamin.images.first() else vitamin.pk}'>"
            f"<img src='{vitamin.images.first().image.url if vitamin.images.first() else vitamin.pk}'"
            f" alt='{vitamin.title}' width='75'></a>")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')


@admin.register(DeliveryRequest)
class DeliveryRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'title', 'url')
    list_display_links = ('id', 'name')
    fields = ('name', 'email', 'title', 'url', 'comment')
