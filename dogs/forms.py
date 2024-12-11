from django import forms
from django.forms import inlineformset_factory
from .models import Dog, Pedigree
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class DogForm(forms.ModelForm):
    """
    Форма для создания и редактирования объектов модели Dog.

    Класс Meta определяет модель и поля, которые будут использоваться в форме.
    """

    class Meta:
        model = Dog
        fields = ['name', 'breed', 'age', 'image']
        labels = {
            'name': _('Имя собаки'),
            'breed': _('Порода'),
            'age': _('Возраст'),
            'image': _('Фото'),
        }
        help_texts = {
            'name': _('Введите имя вашей собаки.'),
            'age': _('Укажите возраст собаки в годах.'),
        }
        error_messages = {
            'name': {
                'max_length': _('Имя собаки слишком длинное.'),
            },
            'age': {
                'invalid': _('Возраст должен быть числом.'),
            },
        }

    def __init__(self, *args, **kwargs):
        """
        Конструктор формы для настройки полей.

        Убирает пустой вариант в выпадающем списке для поля 'breed'.
        """
        super().__init__(*args, **kwargs)
        self.fields['breed'].empty_label = None  # Убираем пустой вариант для выбора породы

    def clean_age(self):
        """
        Проверяет, чтобы возраст был положительным числом.

        Возвращает:
            int: Валидный возраст собаки.

        Выбрасывает:
            ValidationError: Если возраст отрицательный.
        """
        age = self.cleaned_data.get('age')
        if age is not None and age < 0:
            raise ValidationError(_('Возраст не может быть отрицательным.'))
        return age

    def clean_image(self):
        """
        Проверяет тип и размер загружаемого изображения.

        Возвращает:
            image: Загруженное изображение.

        Выбрасывает:
            ValidationError: Если изображение имеет неверный формат или превышает допустимый размер.
        """
        image = self.cleaned_data.get('image')
        if image:
            if image.size > 5 * 1024 * 1024:  # Лимит на размер файла (5 MB)
                raise ValidationError(_('Размер изображения не должен превышать 5MB.'))
            if not image.content_type.startswith('image'):
                raise ValidationError(_('Загруженный файл должен быть изображением.'))
        return image

    def clean(self):
        """
        Общая проверка формы. Можно использовать для проверки зависимости между несколькими полями.
        """
        cleaned_data = super().clean()
        # Добавьте здесь дополнительные проверки, если нужно.
        return cleaned_data

def get_pedigree_formset(instance=None):
    return inlineformset_factory(
        Dog,  # Основная модель
        Pedigree,  # Связанная модель
        fields=('ancestor_name', 'relationship', 'birth_year'),
        extra=1 if instance is None else 0,  # Количество пустых форм для добавления
        can_delete=True  # Возможность удаления
    )