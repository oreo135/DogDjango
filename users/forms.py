from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from django.utils.translation import gettext_lazy as _

class RegisterForm(UserCreationForm):
    """
    Форма для регистрации нового пользователя.
    """
    email = forms.EmailField(
        required=True,
        label=_("Электронная почта"),
        error_messages={
            'required': _("Электронная почта обязательна."),
            'invalid': _("Введите действительный адрес электронной почты."),
        },
    )
    age = forms.IntegerField(
        required=False,
        label=_("Возраст"),
        error_messages={
            'invalid': _("Возраст должен быть числом."),
        },
    )
    bio = forms.CharField(
        required=False,
        label=_("Биография"),
        widget=forms.Textarea,
    )
    avatar = forms.ImageField(
        required=False,
        label=_("Аватар"),
        error_messages={
            'invalid': _("Неверный формат файла."),
        },
    )
    birth_date = forms.DateField(
        required=False,
        label=_("Дата рождения"),
        widget=forms.DateInput(attrs={'type': 'date'}),
        error_messages={
            'invalid': _("Введите корректную дату."),
        },
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'age', 'bio', 'avatar', 'birth_date']
        labels = {
            'username': _("Имя пользователя"),
            'password1': _("Пароль"),
            'password2': _("Подтверждение пароля"),
        }
        error_messages = {
            'username': {
                'max_length': _("Имя пользователя слишком длинное."),
            },
        }

class UpdateProfileForm(forms.ModelForm):
    """
    Форма для редактирования профиля пользователя с поддержкой мультиязычности.
    """
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'age', 'bio', 'avatar', 'birth_date']
        labels = {
            'username': _("Имя пользователя"),
            'email': _("Электронная почта"),
            'age': _("Возраст"),
            'bio': _("Биография"),
            'avatar': _("Аватар"),
            'birth_date': _("Дата рождения"),
        }
        error_messages = {
            'username': {
                'max_length': _("Имя пользователя слишком длинное."),
            },
            'email': {
                'invalid': _("Введите действительный адрес электронной почты."),
            },
        }