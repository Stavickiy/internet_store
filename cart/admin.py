from django.contrib import admin

from cart.models import PromoCod


@admin.register(PromoCod)
class PromoCodAdmin(admin.ModelAdmin):
    list_display = ('code', 'is_active', 'discount', 'min_sum')
