from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from users.models import User


class UserAdmin(BaseUserAdmin):
    # Добавляем дополнительные поля в список полей, которые будут отображаться на странице списка пользователей
    list_display = BaseUserAdmin.list_display + ('phone_number',)

    # Добавляем дополнительные поля в форму редактирования пользователя
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone_number',)}),
    )

    # Добавляем дополнительные поля в форму создания пользователя
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('phone_number',)}),
    )


admin.site.register(User, UserAdmin)
