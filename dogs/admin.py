from django.contrib import admin
from .models import Dog, Breed


@admin.register(Dog)
class DogAdmin(admin.ModelAdmin):
    """
    Настройки отображения модели Dog в админке.
    """
    list_display = ('name', 'breed', 'age', 'image')  # Поля, которые будут отображаться в списке объектов
    list_filter = ('breed', 'age')  # Поля для фильтрации
    search_fields = ('name', 'breed__name', 'owner__username')  # Поля для поиска
    ordering = ('name',)  # Сортировка объектов
    list_per_page = 10  # Количество объектов на странице

    # Настройка формы редактирования
    fieldsets = (
        (None, {
            'fields': ('name', 'breed', 'age', 'image'),
        }),
    )


@admin.register(Breed)
class BreedAdmin(admin.ModelAdmin):
    """
    Настройки отображения модели Breed в админке.
    """
    list_display = ('name', 'description')  # Поля, которые будут отображаться в списке объектов
    search_fields = ('name',)  # Поля для поиска
    ordering = ('name',)  # Сортировка объектов
