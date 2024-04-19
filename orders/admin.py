from django.contrib import admin
from django.db import transaction
from django.utils.safestring import mark_safe

from orders.models import Order, OrderItem, OrderStatus


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  # Prevents extra empty forms
    readonly_fields = ('vitamin_photo', 'product', 'quantity', 'price', 'discount', 'sum')

    @admin.display(description='Photo')
    def vitamin_photo(self, instance):
        if instance.product.images.exists():
            return mark_safe(f'<img src="{instance.product.images.first().image.url}" width="75" />')
        return ""


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'type_delivery', 'type_payment',
                    'status', 'without_discount', 'total_price', 'discount_sum')
    inlines = [OrderItemInline]
    fields = ['user', 'created_at', 'type_delivery', 'type_payment', 'payment_status', 'status',
              'total_price', 'without_discount', 'discount_sum', 'shipping_address', 'comment', 'email', 'phone_number']
    readonly_fields = ('created_at',)
    actions = ('canceling_order',)
    list_filter = ('status', 'type_payment', 'type_delivery', 'payment_status', 'user')

    @admin.action(description='Отменить выбранные заказы')
    def canceling_order(self, request, queryset):
        with transaction.atomic():
            for order in queryset:
                for item in order.items.all():
                    item.product.adding_count(item.quantity)
                order.status = OrderStatus.CANCELED
                order.save()


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'vitamin_photo', 'product', 'quantity', 'price', 'sum', 'discount')
    readonly_fields = ('vitamin_photo',)

    @admin.display(description='vitamin_photo')
    def vitamin_photo(self, order_item: OrderItem):
        return mark_safe(
            f"<a href='{order_item.product.images.first().image.url if order_item.product.images.first() else order_item.product.pk}'>"
            f"<img src='{order_item.product.images.first().image.url if order_item.product.images.first() else order_item.product.pk}'"
            f" alt='{order_item.product.title}' width='75'></a>")
