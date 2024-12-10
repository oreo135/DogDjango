from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Админ-класс для пользовательской модели CustomUser.

    Расширяет стандартный UserAdmin, добавляя отображение аватара, управление ролями и статусами,
    а также возможности массового управления активностью пользователей.
    """
    model = CustomUser

    # Поля для отображения в списке пользователей
    list_display = ('username', 'email', 'role', 'is_active', 'avatar', 'is_staff')

    # Фильтры для удобства
    list_filter = ('role', 'is_active')

    # Поля для редактирования пользователя
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {'fields': ('first_name', 'last_name', 'email')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
        ('Дополнительные поля', {'fields': ('role', 'avatar')}),
    )

    # Поля, отображаемые в формах создания пользователя
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'role', 'avatar'),
        }),
    )

    # Массовые действия для активации/деактивации
    actions = ['make_active', 'make_inactive']

    def make_active(self, request, queryset):
        """
        Массовая активация пользователей.
        """
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} пользователей активировано.")
    make_active.short_description = "Активировать пользователей"

    def make_inactive(self, request, queryset):
        """
        Массовая деактивация пользователей.
        """
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} пользователей деактивировано.")
    make_inactive.short_description = "Деактивировать пользователей"
