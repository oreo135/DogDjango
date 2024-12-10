from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Расширенная модель пользователя.

    Атрибуты:
        role (CharField): Роль пользователя с предопределёнными значениями (admin, moderator, user).
        age (IntegerField): Возраст пользователя (может быть пустым).
        bio (TextField): Краткая биография пользователя (опционально).
        avatar (ImageField): Аватар пользователя (опционально).
        birth_date (DateField): Дата рождения пользователя (опционально).
    """

    ROLE_CHOICES = [
        ('admin', 'Администратор'),
        ('moderator', 'Модератор'),
        ('user', 'Пользователь'),
    ]
    is_active = models.BooleanField(default=True, verbose_name='Активный пользователь')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    age = models.IntegerField(null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    birth_date = models.DateField(blank=True, null=True)


    def get_role_display(self) -> str:
        """
        Возвращает отображаемое имя роли.
        """
        return dict(self.ROLE_CHOICES).get(self.role, "Неизвестная роль")

    def __str__(self):
        """
        Возвращает строковое представление пользователя (имя пользователя).
        """
        return f"{self.username} ({self.get_role_display()})"

    def is_admin(self):
        """
        Проверка, является ли пользователь администратором.
        """
        return self.role == 'admin'

    def is_moderator(self):
        """
        Проверка, является ли пользователь модератором.
        """
        return self.role == 'moderator'

    def is_user(self):
        """
        Проверка, является ли пользователь обычным пользователем.
        """
        return self.role == 'user'
