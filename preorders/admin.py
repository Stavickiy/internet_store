from django.contrib import admin
from django.db import transaction
from django.utils.safestring import mark_safe

from preorders.models import PreOrder, OrderStatus, PreOrderItem


class PreOrderItemInline(admin.TabularInline):
    model = PreOrderItem
    extra = 0  # Prevents extra empty forms
    readonly_fields = ('vitamin_photo', 'product', 'quantity', 'price', 'discount', 'sum')

    @admin.display(description='Photo')
    def vitamin_photo(self, instance):
        if instance.product.images.exists():
            return mark_safe(f'<img src="{instance.product.images.first().image.url}" width="75" />')
        return ""


@admin.register(PreOrder)
class PreOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'type_delivery', 'type_payment',
                    'status', 'without_discount', 'discount_sum')
    inlines = [PreOrderItemInline]
    fields = ['user', 'created_at', 'type_delivery', 'type_payment', 'payment_status', 'status',
              'total_price', 'without_discount', 'discount_sum', 'shipping_address', 'comment', 'email', 'phone_number']
    readonly_fields = ('created_at',)
    actions = ('canceling_preorder',)
    list_filter = ('status', 'type_payment', 'type_delivery', 'payment_status', 'user')

    @admin.action(description='Отменить выбранные предзаказы')
    def canceling_preorder(self, request, queryset):
        with transaction.atomic():
            for order in queryset:
                for item in order.items.all():
                    item.product.decrease_preorder_count(item.quantity)
                order.status = OrderStatus.CANCELED
                order.save()


@admin.register(PreOrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'vitamin_photo', 'product', 'quantity', 'price', 'sum', 'discount')
    readonly_fields = ('vitamin_photo',)

    @admin.display(description='vitamin_photo')
    def vitamin_photo(self, order_item: PreOrderItem):
        return mark_safe(
            f"<a href='{order_item.product.images.first().image.url if order_item.product.images.first() else order_item.product.pk}'>"
            f"<img src='{order_item.product.images.first().image.url if order_item.product.images.first() else order_item.product.pk}'"
            f" alt='{order_item.product.title}' width='75'></a>")
